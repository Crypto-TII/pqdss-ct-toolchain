(**************************************************************************)
(*  This file is part of BINSEC.                                          *)
(*                                                                        *)
(*  Copyright (C) 2016-2025                                               *)
(*    CEA (Commissariat à l'énergie atomique et aux énergies              *)
(*         alternatives)                                                  *)
(*                                                                        *)
(*  you can redistribute it and/or modify it under the terms of the GNU   *)
(*  Lesser General Public License as published by the Free Software       *)
(*  Foundation, version 2.1.                                              *)
(*                                                                        *)
(*  It is distributed in the hope that it will be useful,                 *)
(*  but WITHOUT ANY WARRANTY; without even the implied warranty of        *)
(*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *)
(*  GNU Lesser General Public License for more details.                   *)
(*                                                                        *)
(*  See the GNU Lesser General Public License version 2.1                 *)
(*  for more details (enclosed in the file licenses/LGPLv2.1).            *)
(*                                                                        *)
(**************************************************************************)

let byte_size = Natural.to_int Basic_types.Constants.bytesize
let memory_name = "@" ^ Suid.(to_string zero)

module Session = struct
  let n = ref 0

  type state = Dead | Assert | Sat | Unsat

  type session = {
    solver : Prover.t;
    mutable state : state;
    pid : Subprocess.t;
    stdin : out_channel;
    stdout : in_channel;
    stderr : in_channel;
    stdlog : out_channel option;
    fdlog : out_channel option;
    formatter : Format.formatter;
  }

  let close t =
    if t.state <> Dead then (
      t.state <- Dead;
      ignore @@ Subprocess.close t.pid;
      match t.fdlog with None -> () | Some fd -> close_out fd)

  let start ?stdlog solver =
    Options.Logger.debug "Openning session %d" !n;
    let fdlog =
      match Smt_options.SMT_dir.get_opt () with
      | None -> None
      | Some dir ->
          if not (Sys.file_exists dir) then Unix.mkdir dir 0o777;
          let filename =
            Filename.concat dir (Printf.sprintf "query_%d.smt2" !n)
          in
          Some (open_out filename)
    in
    incr n;
    let cmd = Prover.command ~incremental:true 0 solver in
    let pid = Subprocess.spawn ~pdeathsig:Sys.sigkill cmd in
    let stdin = Subprocess.stdin pid
    and stdout = Subprocess.stdout pid
    and stderr = Subprocess.stderr pid in
    let formatter =
      match (stdlog, fdlog) with
      | None, None -> Format.formatter_of_out_channel stdin
      | Some stdlog, None ->
          let output str pos len =
            output_substring stdlog str pos len;
            output_substring stdin str pos len
          and flush () =
            flush stdlog;
            flush stdin
          in
          Format.make_formatter output flush
      | None, Some fdlog ->
          let output str pos len =
            output_substring fdlog str pos len;
            output_substring stdin str pos len
          and flush () =
            flush fdlog;
            flush stdin
          in
          Format.make_formatter output flush
      | Some stdlog, Some fdlog ->
          let output str pos len =
            output_substring stdlog str pos len;
            output_substring fdlog str pos len;
            output_substring stdin str pos len
          and flush () =
            flush stdlog;
            flush fdlog;
            flush stdin
          in
          Format.make_formatter output flush
    in
    Format.fprintf formatter
      "@[<v 0>(set-option :print-success false)@ (set-info :smt-lib-version \
       2.5)@ (set-logic QF_ABV)@ @]@[<hov>";
    {
      solver;
      state = Assert;
      pid;
      stdin;
      stdout;
      stderr;
      stdlog;
      fdlog;
      formatter;
    }

  let rec parse_check_with_deadline t fd deadline : Libsolver.status =
    match deadline with
    | None -> parse_check_line t fd deadline Float.minus_one
    | Some deadline' ->
        let timeout = deadline' -. Unix.gettimeofday () in
        if Float.sign_bit timeout then (
          close t;
          Unknown)
        else parse_check_line t fd deadline timeout

  and parse_check_line t fd deadline timeout : Libsolver.status =
    match Unix.select [ fd ] [] [] timeout with
    | [ _ ], _, _ ->
        Unix.set_nonblock fd;
        parse_check_line_nonblock t fd deadline
    | _ ->
        close t;
        Unknown

  and parse_check_line_nonblock t fd deadline : Libsolver.status =
    match input_line t.stdout with
    | "sat" ->
        Unix.clear_nonblock fd;
        t.state <- Sat;
        Sat
    | "unsat" ->
        Unix.clear_nonblock fd;
        t.state <- Unsat;
        Unsat
    | "unknown" ->
        Unix.clear_nonblock fd;
        t.state <- Assert;
        Unknown
    | "" -> parse_check_line_nonblock t fd deadline
    | s ->
        Options.Logger.error "Solver returned: %s" s;
        close t;
        Unknown
    | exception Sys_blocked_io ->
        Unix.clear_nonblock fd;
        parse_check_with_deadline t fd deadline
    | exception End_of_file ->
        close t;
        Unknown

  let parse_check t ~timeout =
    parse_check_with_deadline t
      (Unix.descr_of_in_channel t.stdout)
      (Option.map (fun timeout -> Unix.gettimeofday () +. timeout) timeout)

  let check_sat t ~timeout =
    Format.fprintf t.formatter "(check-sat)@.@[<hov>";
    parse_check t ~timeout

  let check_sat_assuming t ~timeout e =
    Format.fprintf t.formatter "(check-sat-assuming (%s))@.@[<hov>" e;
    parse_check t ~timeout

  let value_of_constant cst =
    let open Smtlib in
    match cst with
    | CstBool false -> Z.zero
    | CstBool true -> Z.one
    | CstBinary b -> Z.of_string_base 2 b
    | CstDecimal d | CstDecimalSize (d, _) -> Z.of_string_base 10 d
    | CstHexadecimal x -> Z.of_string_base 16 x
    | CstNumeral _ | CstString _ ->
        Options.Logger.fatal
          "Model construction: unexpected constant %a as bitvector value"
          Smtlib_pp.pp_spec_constant cst

  let get_value t pp x =
    assert (t.state = Sat);
    Format.fprintf t.formatter "(get-value (%a))@.@[<hov>" pp x;
    let lexbuf = Lexing.from_channel t.stdout in
    let open Smtlib in
    match Smtlib_parser.ivalue Smtlib_lexer.token lexbuf with
    | [ (_, { term_desc = TermSpecConstant cst; _ }) ] -> value_of_constant cst
    | _ -> assert false
end

(* utils *)
let pp_int_as_bv ppf x = function
  | 1 -> Format.fprintf ppf "#b%d" (x land 1)
  | 4 -> Format.fprintf ppf "#x%01x" (x land 0xf)
  | 8 -> Format.fprintf ppf "#x%02x" (x land 0xff)
  | 12 -> Format.fprintf ppf "#x%03x" (x land 0xfff)
  | 16 -> Format.fprintf ppf "#x%04x" (x land 0xffff)
  | 20 -> Format.fprintf ppf "#x%05x" (x land 0xfffff)
  | 24 -> Format.fprintf ppf "#x%06x" (x land 0xffffff)
  | 28 -> Format.fprintf ppf "#x%07x" (x land 0xfffffff)
  | 32 -> Format.fprintf ppf "#x%08x" (x land 0xffffffff)
  | sz when x < 0 ->
      Format.fprintf ppf "(_ bv%a %d)" Z.pp_print
        (Z.extract (Z.of_int x) 0 sz)
        sz
  | sz -> Format.fprintf ppf "(_ bv%d %d)" x sz

let pp_bv ppf value size =
  try pp_int_as_bv ppf (Z.to_int value) size
  with Z.Overflow ->
    Format.fprintf ppf "(_ bv%a %d)" Z.pp_print
      (if Z.lt value Z.zero then Z.extract value 0 size else value)
      size

module Printer = struct
  open Sexpr

  type term = string

  type access = Select of term * int | Store of term * int
  and def = Bl of Expr.t | Bv of Expr.t | Ax of Memory.t | Decl of string

  and t = {
    fvariables : Expr.t StTbl.t;
    farrays : Memory.t StTbl.t;
    mutable id : Suid.t;
    bl_cons : string BvTbl.t;
    bv_cons : string BvTbl.t;
    ax_cons : string AxTbl.t;
    ax_root : Memory.t AxTbl.t;
    ordered_defs : def Queue.t;
    ordered_mem : access Queue.t AxTbl.t;
    word_size : int;
    debug : name:string -> label:string -> string;
  }

  let create ?(word_size = Kernel_options.Machine.word_size ())
      ?(debug = fun ~name ~label:_ -> name) ~next_id () =
    let bv_cons = BvTbl.create 128 and bl_cons = BvTbl.create 32 in
    BvTbl.add bl_cons Expr.zero "false";
    BvTbl.add bv_cons Expr.zero "#b0";
    BvTbl.add bl_cons Expr.one "true";
    BvTbl.add bv_cons Expr.one "#b1";
    {
      fvariables = StTbl.create 16;
      farrays = StTbl.create 4;
      id = next_id;
      bl_cons;
      bv_cons;
      ax_cons = AxTbl.create 64;
      ax_root = AxTbl.create 64;
      ordered_defs = Queue.create ();
      ordered_mem = AxTbl.create 4;
      word_size;
      debug;
    }

  let copy
      {
        fvariables;
        farrays;
        id;
        bl_cons;
        bv_cons;
        ax_cons;
        ax_root;
        ordered_defs;
        ordered_mem;
        word_size;
        debug;
      } =
    let ordered_mem =
      AxTbl.fold
        (fun ax history tbl ->
          AxTbl.add tbl ax (Queue.copy history);
          tbl)
        ordered_mem
        (AxTbl.create (AxTbl.length ordered_mem))
    in
    {
      fvariables = StTbl.copy fvariables;
      farrays = StTbl.copy farrays;
      id;
      bl_cons = BvTbl.copy bl_cons;
      bv_cons = BvTbl.copy bv_cons;
      ax_cons = AxTbl.copy ax_cons;
      ax_root;
      ordered_defs = Queue.copy ordered_defs;
      ordered_mem;
      word_size;
      debug;
    }

  let pp_int_as_offset size ppf i = pp_bv ppf i size

  let once = ""
  and evicted = "\\"

  let rec visit_bl ctx bl =
    match BvTbl.find ctx.bl_cons bl with
    | exception Not_found -> visit_and_mark_bl ctx bl BvTbl.add once
    | label ->
        if label == once then (
          let name = Suid.to_string ctx.id in
          ctx.id <- Suid.incr ctx.id;
          BvTbl.replace ctx.bl_cons bl name)
        else if label == evicted then (
          let name = Suid.to_string ctx.id in
          ctx.id <- Suid.incr ctx.id;
          visit_and_mark_bl ctx bl BvTbl.replace name)

  and visit_and_mark_bl ctx (bl : Expr.t) set label =
    match bl with
    | Cst _ -> ()
    | Load _ (* cannot be a bl<1> *) -> assert false
    | Unary { f = Not; x; _ } ->
        set ctx.bl_cons bl label;
        visit_bl ctx x;
        Queue.push (Bl bl) ctx.ordered_defs
    | Binary { f = And | Or | Xor; x; y; _ } ->
        set ctx.bl_cons bl label;
        visit_bl ctx x;
        visit_bl ctx y;
        Queue.push (Bl bl) ctx.ordered_defs
    | Binary
        {
          f = Eq | Diff | Uge | Ule | Ugt | Ult | Sge | Sle | Sgt | Slt;
          x;
          y;
          _;
        } ->
        set ctx.bl_cons bl label;
        visit_bv ctx x;
        visit_bv ctx y;
        Queue.push (Bl bl) ctx.ordered_defs
    | Ite { c; t; e; _ } ->
        set ctx.bl_cons bl label;
        visit_bl ctx c;
        visit_bl ctx t;
        visit_bl ctx e;
        Queue.push (Bl bl) ctx.ordered_defs
    | Var _ | Unary _ | Binary _ ->
        set ctx.bl_cons bl label;
        visit_bv ctx bl;
        Queue.push (Bl bl) ctx.ordered_defs

  and visit_bv ctx bv =
    match BvTbl.find ctx.bv_cons bv with
    | exception Not_found -> visit_and_mark_bv ctx bv BvTbl.add once
    | label ->
        if label == once then (
          let name = Suid.to_string ctx.id in
          ctx.id <- Suid.incr ctx.id;
          BvTbl.replace ctx.bv_cons bv name)
        else if label == evicted then (
          let name = Suid.to_string ctx.id in
          ctx.id <- Suid.incr ctx.id;
          visit_and_mark_bv ctx bv BvTbl.replace name)

  and visit_and_mark_bv ctx bv set label' =
    match bv with
    | Var { name; size; label; _ } ->
        StTbl.add ctx.fvariables name bv;
        let name = ctx.debug ~name ~label in
        BvTbl.add ctx.bv_cons bv name;
        Queue.push
          (Decl (Format.sprintf "(declare-fun %s () (_ BitVec %d))" name size))
          ctx.ordered_defs
    | Load { len; addr; label; _ } ->
        let name = Suid.to_string ctx.id in
        ctx.id <- Suid.incr ctx.id;
        BvTbl.add ctx.bv_cons bv name;
        visit_bv ctx addr;
        visit_bv ctx addr;
        visit_ax ctx label;
        if len > 1 then visit_ax ctx label;
        Queue.push (Bv bv) ctx.ordered_defs;
        let root = AxTbl.find ctx.ax_root label in
        let ordered_mem = AxTbl.find ctx.ordered_mem root in
        Queue.push (Select (BvTbl.find ctx.bv_cons addr, len)) ordered_mem
    | Cst _ ->
        set ctx.bv_cons bv label';
        Queue.push (Bv bv) ctx.ordered_defs
    | Unary { x; _ } ->
        set ctx.bv_cons bv label';
        visit_bv ctx x;
        Queue.push (Bv bv) ctx.ordered_defs
    | Binary
        { f = Eq | Diff | Uge | Ule | Ugt | Ult | Sge | Sle | Sgt | Slt; _ } ->
        set ctx.bv_cons bv label';
        visit_bl ctx bv;
        Queue.push (Bv bv) ctx.ordered_defs
    | Binary
        { f = Rol | Ror; x; y = (Load _ | Unary _ | Binary _ | Ite _) as y; _ }
      ->
        set ctx.bv_cons bv label';
        visit_bv ctx x;
        visit_bv ctx x;
        visit_bv ctx y;
        visit_bv ctx y;
        Queue.push (Bv bv) ctx.ordered_defs
    | Binary { x; y; _ } ->
        set ctx.bv_cons bv label';
        visit_bv ctx x;
        visit_bv ctx y;
        Queue.push (Bv bv) ctx.ordered_defs
    | Ite { c; t; e; _ } ->
        set ctx.bv_cons bv label';
        visit_bl ctx c;
        visit_bv ctx t;
        visit_bv ctx e;
        Queue.push (Bv bv) ctx.ordered_defs

  and visit_ax ctx (ax : Memory.t) =
    match AxTbl.find ctx.ax_cons ax with
    | exception Not_found -> visit_and_mark_ax ctx ax AxTbl.add once
    | label ->
        if label == once then (
          let name = Suid.to_string ctx.id in
          ctx.id <- Suid.incr ctx.id;
          AxTbl.replace ctx.ax_cons ax name)
        else if label == evicted then (
          let name = Suid.to_string ctx.id in
          ctx.id <- Suid.incr ctx.id;
          visit_and_mark_ax ctx ax AxTbl.replace name)

  and visit_and_mark_ax ctx (ax : Memory.t) set label =
    match ax with
    | Root ->
        AxTbl.add ctx.ax_cons ax (ctx.debug ~name:memory_name ~label:"memory");
        AxTbl.add ctx.ax_root ax ax;
        AxTbl.add ctx.ordered_mem ax (Queue.create ());
        Queue.push
          (Decl
             (Format.sprintf
                "(declare-fun %s () (Array (_ BitVec %d) (_ BitVec %d)))"
                (ctx.debug ~name:memory_name ~label:"memory")
                ctx.word_size byte_size))
          ctx.ordered_defs
    | Symbol name ->
        StTbl.add ctx.farrays name ax;
        AxTbl.add ctx.ax_cons ax name;
        AxTbl.add ctx.ax_root ax ax;
        AxTbl.add ctx.ordered_mem ax (Queue.create ());
        Queue.push
          (Decl
             (Format.sprintf
                "(declare-fun %s () (Array (_ BitVec %d) (_ BitVec %d)))" name
                ctx.word_size byte_size))
          ctx.ordered_defs
    | Layer { addr = Cst _; store; over; _ } ->
        set ctx.ax_cons ax label;
        Store.iter_term
          (fun _ bv ->
            visit_bv ctx bv;
            if Expr.sizeof bv <> 8 then visit_bv ctx bv)
          store;
        visit_ax ctx over;
        let root = AxTbl.find ctx.ax_root over in
        AxTbl.add ctx.ax_root ax root;
        Queue.push (Ax ax) ctx.ordered_defs;
        let ordered_mem = AxTbl.find ctx.ordered_mem root in
        Store.iter_term
          (fun i bv ->
            let index =
              Format.asprintf "%a" (pp_int_as_offset ctx.word_size) i
            in
            Queue.push (Store (index, Expr.sizeof bv lsr 3)) ordered_mem)
          store
    | Layer { addr; store; over; _ } ->
        set ctx.ax_cons ax label;
        visit_bv ctx addr;
        visit_bv ctx addr;
        Store.iter_term
          (fun _ bv ->
            visit_bv ctx bv;
            if Expr.sizeof bv <> 8 then visit_bv ctx bv)
          store;
        visit_ax ctx over;
        let root = AxTbl.find ctx.ax_root over in
        AxTbl.add ctx.ax_root ax root;
        Queue.push (Ax ax) ctx.ordered_defs;
        let ordered_mem = AxTbl.find ctx.ordered_mem root in
        let index = BvTbl.find ctx.bv_cons addr in
        Store.iter_term
          (fun i bv ->
            let index =
              Format.asprintf "(bvadd %s %a)" index
                (pp_int_as_offset ctx.word_size)
                i
            in
            Queue.push (Store (index, Expr.sizeof bv lsr 3)) ordered_mem)
          store

  let pp_unop ppf (op : Term.unary Term.operator) =
    match op with
    | Not -> Format.pp_print_string ppf "bvnot"
    | Minus -> Format.pp_print_string ppf "bvneg"
    | Uext n -> Format.fprintf ppf "(_ zero_extend %d)" n
    | Sext n -> Format.fprintf ppf "(_ sign_extend %d)" n
    | Restrict { Interval.hi; lo } ->
        Format.fprintf ppf "(_ extract %d %d)" hi lo

  let pp_binop =
    let string_of_binop (op : Term.binary Term.operator) =
      match op with
      | Plus -> "bvadd"
      | Minus -> "bvsub"
      | Mul -> "bvmul"
      | Udiv -> "bvudiv"
      | Sdiv -> "bvsdiv"
      | Umod -> "bvurem"
      | Smod -> "bvsrem"
      | Or -> "bvor"
      | And -> "bvand"
      | Xor -> "bvxor"
      | Concat -> "concat"
      | Lsl -> "bvshl"
      | Lsr -> "bvlshr"
      | Asr -> "bvashr"
      | Rol -> "rotate_left"
      | Ror -> "rotate_right"
      | Eq -> "="
      | Diff -> assert false
      | Ule -> "bvule"
      | Ult -> "bvult"
      | Uge -> "bvuge"
      | Ugt -> "bvugt"
      | Sle -> "bvsle"
      | Slt -> "bvslt"
      | Sge -> "bvsge"
      | Sgt -> "bvsgt"
    in
    fun ppf f -> Format.pp_print_string ppf (string_of_binop f)

  let rec print_bl ctx ppf bl =
    try
      let name = BvTbl.find ctx.bl_cons bl in
      if name == once || name == evicted then print_bl_no_cons ctx ppf bl
      else Format.pp_print_string ppf name
    with Not_found ->
      Format.pp_print_string ppf "(= ";
      Format.pp_print_space ppf ();
      print_bv ctx ppf bl;
      Format.pp_print_string ppf " #b1)"

  and print_bl_no_cons ctx ppf bl =
    match bl with
    | Cst _ (* true and false should already be in the cache *)
    | Load _ (* cannot be a bl<1> *) ->
        assert false
    | Unary { f = Not; x; _ } ->
        Format.pp_print_string ppf "(not";
        Format.pp_print_space ppf ();
        print_bl ctx ppf x;
        Format.pp_print_char ppf ')'
    | Binary { f = (And | Or | Xor) as f; x; y; _ } ->
        Format.pp_print_char ppf '(';
        (Format.pp_print_string ppf
        @@
        match f with
        | And -> "and"
        | Or -> "or"
        | Xor -> "xor"
        | _ -> assert false);
        Format.pp_print_space ppf ();
        print_bl ctx ppf x;
        Format.pp_print_space ppf ();
        print_bl ctx ppf y;
        Format.pp_print_char ppf ')'
    | Binary { f = Diff; x; y; _ } ->
        Format.pp_print_string ppf "(not";
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf "(=";
        Format.pp_print_space ppf ();
        print_bv ctx ppf x;
        Format.pp_print_space ppf ();
        print_bv ctx ppf y;
        Format.pp_print_string ppf "))"
    | Binary
        {
          f = (Eq | Uge | Ule | Ugt | Ult | Sge | Sle | Sgt | Slt) as f;
          x;
          y;
          _;
        } ->
        Format.pp_print_char ppf '(';
        pp_binop ppf f;
        Format.pp_print_space ppf ();
        print_bv ctx ppf x;
        Format.pp_print_space ppf ();
        print_bv ctx ppf y;
        Format.pp_print_char ppf ')'
    | Ite { c; t; e; _ } ->
        Format.pp_print_string ppf "(ite";
        Format.pp_print_space ppf ();
        print_bl ctx ppf c;
        Format.pp_print_space ppf ();
        print_bl ctx ppf t;
        Format.pp_print_space ppf ();
        print_bl ctx ppf e;
        Format.pp_print_char ppf ')'
    | Var _ | Unary _ | Binary _ ->
        Format.pp_print_string ppf "(=";
        Format.pp_print_space ppf ();
        print_bv ctx ppf bl;
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf "#b1)"

  and print_bv ctx ppf bv =
    let name = BvTbl.find ctx.bv_cons bv in
    if name == once || name == evicted then print_bv_no_cons ctx ppf bv
    else Format.pp_print_string ppf name

  and print_bv_no_cons ctx ppf bv =
    match bv with
    | Var { name; _ } -> Format.pp_print_string ppf name
    | Load { len = 1; addr; label; _ } ->
        Format.pp_print_string ppf "(select";
        Format.pp_print_space ppf ();
        print_ax ctx ppf label;
        Format.pp_print_space ppf ();
        print_bv ctx ppf addr;
        Format.pp_print_char ppf ')'
    | Load { len; dir; addr; label; _ } ->
        Format.pp_print_string ppf "(concat";
        print_multi_select dir ppf len
          (AxTbl.find ctx.ax_cons label)
          (BvTbl.find ctx.bv_cons addr)
          (Expr.sizeof addr);
        Format.pp_print_char ppf ')'
    | Cst bv ->
        let size = Bv.size_of bv and value = Bv.value_of bv in
        pp_bv ppf value size
    | Unary { f; x; _ } ->
        Format.pp_print_char ppf '(';
        pp_unop ppf f;
        Format.pp_print_space ppf ();
        print_bv ctx ppf x;
        Format.pp_print_char ppf ')'
    | Binary { f = Eq | Uge | Ule | Ugt | Ult | Sge | Sle | Sgt | Slt; _ } ->
        Format.pp_print_string ppf "(ite";
        Format.pp_print_space ppf ();
        print_bl ctx ppf bv;
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf "#b1";
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf "#b0)"
    | Binary { f = Diff; x; y; _ } ->
        Format.pp_print_string ppf "(ite (=";
        Format.pp_print_space ppf ();
        print_bv ctx ppf x;
        Format.pp_print_space ppf ();
        print_bv ctx ppf y;
        Format.pp_print_char ppf ')';
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf "#b0";
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf "#b1)"
    | Binary { f = (Rol | Ror) as f; x; y = Cst bv; _ } ->
        Format.pp_print_string ppf "((_";
        Format.pp_print_space ppf ();
        pp_binop ppf f;
        Format.pp_print_space ppf ();
        Z.pp_print ppf (Bv.value_of bv);
        Format.pp_print_char ppf ')';
        Format.pp_print_space ppf ();
        print_bv ctx ppf x;
        Format.pp_print_char ppf ')'
    | Binary { f = (Rol | Ror) as f; x; y; _ } ->
        Format.pp_print_string ppf "(bvor";
        Format.pp_print_space ppf ();
        Format.pp_print_char ppf '(';
        pp_binop ppf
          (match f with Rol -> Lsl | Ror -> Lsr | _ -> assert false);
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf (BvTbl.find ctx.bv_cons x);
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf (BvTbl.find ctx.bv_cons y);
        Format.pp_print_char ppf ')';
        Format.pp_print_space ppf ();
        Format.pp_print_char ppf '(';
        pp_binop ppf
          (match f with Rol -> Lsr | Ror -> Lsl | _ -> assert false);
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf (BvTbl.find ctx.bv_cons x);
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf "(bvsub";
        Format.pp_print_space ppf ();
        pp_int_as_bv ppf (Expr.sizeof x) (Expr.sizeof x);
        Format.pp_print_space ppf ();
        Format.pp_print_string ppf (BvTbl.find ctx.bv_cons y);
        Format.pp_print_string ppf ")))"
    | Binary { f; x; y; _ } ->
        Format.pp_print_char ppf '(';
        pp_binop ppf f;
        Format.pp_print_space ppf ();
        print_bv ctx ppf x;
        Format.pp_print_space ppf ();
        print_bv ctx ppf y;
        Format.pp_print_char ppf ')'
    | Ite { c; t; e; _ } ->
        Format.pp_print_string ppf "(ite";
        Format.pp_print_space ppf ();
        print_bl ctx ppf c;
        Format.pp_print_space ppf ();
        print_bv ctx ppf t;
        Format.pp_print_space ppf ();
        print_bv ctx ppf e;
        Format.pp_print_char ppf ')'

  and print_ax ctx ppf ax =
    let name = AxTbl.find ctx.ax_cons ax in
    if name == once || name == evicted then print_ax_no_cons ctx ppf ax
    else Format.pp_print_string ppf name

  and print_ax_no_cons ctx ppf (ax : Memory.t) =
    match ax with
    | Root -> Suid.pp ppf Suid.zero
    | Symbol _ -> assert false
    | Layer { addr; store; over; _ } ->
        Store.iter_term
          (fun _ value ->
            for _ = 1 to Expr.sizeof value lsr 3 do
              Format.pp_print_string ppf "(store";
              Format.pp_print_space ppf ()
            done)
          store;
        print_ax ctx ppf over;
        let addr_space = ctx.word_size in
        let rebase, idx =
          match addr with
          | Cst _ -> (false, "")
          | _ -> (true, BvTbl.find ctx.bv_cons addr)
        in
        let rec unroll_store lo i bv =
          Format.pp_print_space ppf ();
          if rebase then
            if Z.zero = i then (
              Format.pp_print_string ppf idx;
              Format.pp_print_space ppf ())
            else (
              Format.pp_print_string ppf "(bvadd";
              Format.pp_print_space ppf ();
              Format.pp_print_string ppf idx;
              Format.pp_print_space ppf ();
              pp_bv ppf i addr_space;
              Format.pp_print_char ppf ')')
          else pp_bv ppf i addr_space;
          Format.pp_print_space ppf ();
          let size = Expr.sizeof bv in
          if size > 8 then (
            Format.fprintf ppf "((_ extract %d %d)" (lo + 7) lo;
            Format.pp_print_space ppf ();
            print_bv ctx ppf bv;
            Format.pp_print_string ppf "))";
            let lo' = lo + 8 in
            if lo' < size then unroll_store lo' (Z.succ i) bv)
          else (
            print_bv ctx ppf bv;
            Format.pp_print_char ppf ')')
        in
        Store.iter_term (unroll_store 0) store

  and print_multi_select =
    let rec print_multi_select_le ppf len ax bv size =
      if len = 1 then Format.fprintf ppf " (select@ %s@ %s)" ax bv
      else
        let len = len - 1 in
        Format.fprintf ppf " (select@ %s@ (bvadd@ %s@ " ax bv;
        pp_int_as_bv ppf len size;
        Format.pp_print_string ppf "))";
        print_multi_select_le ppf len ax bv size
    in
    let rec print_multi_select_be i ppf len ax bv size =
      if i = 0 then (
        Format.fprintf ppf "@ (select@ %s@ %s)" ax bv;
        print_multi_select_be 1 ppf len ax bv size)
      else if i < len then (
        Format.fprintf ppf " (select@ %s@ (bvadd@ %s@ " ax bv;
        pp_int_as_bv ppf i size;
        Format.pp_print_string ppf "))";
        print_multi_select_be (i + 1) ppf len ax bv size)
    in
    function
    | LittleEndian -> print_multi_select_le
    | BigEndian -> print_multi_select_be 0

  let pp_print_defs ppf ctx =
    Queue.iter
      (function
        | Bl bl ->
            let name = BvTbl.find ctx.bl_cons bl in
            if name == once then BvTbl.replace ctx.bl_cons bl evicted
            else if name == evicted then ()
            else (
              Format.fprintf ppf "@[<h>(define-fun %s () Bool " name;
              print_bl_no_cons ctx ppf bl;
              Format.fprintf ppf ")@]@ ")
        | Bv bv ->
            let name = BvTbl.find ctx.bv_cons bv in
            if name == once then BvTbl.replace ctx.bv_cons bv evicted
            else if name == evicted then ()
            else (
              Format.fprintf ppf "@[<h>(define-fun %s () (_ BitVec %d) " name
                (Expr.sizeof bv);
              print_bv_no_cons ctx ppf bv;
              Format.fprintf ppf ")@]@ ")
        | Ax ax ->
            let name = AxTbl.find ctx.ax_cons ax in
            if name == once then AxTbl.replace ctx.ax_cons ax evicted
            else if name == evicted then ()
            else (
              Format.fprintf ppf
                "@[<h>(define-fun %s () (Array (_ BitVec %d) (_ BitVec %d)) "
                name
                (Kernel_options.Machine.word_size ())
                byte_size;
              print_ax_no_cons ctx ppf ax;
              Format.fprintf ppf ")@]@ ")
        | Decl dl ->
            Format.pp_print_string ppf dl;
            Format.pp_print_space ppf ())
      ctx.ordered_defs

  let pp_flush_defs ppf ctx =
    pp_print_defs ppf ctx;
    Queue.clear ctx.ordered_defs

  let pp_print_bl = print_bl
  let pp_print_bv = print_bv
  let pp_print_ax = print_ax
end

module Cross = struct
  open Sexpr

  type k =
    | Bl of Expr.t
    | Bv of Expr.t
    | Ax of Memory.t
    | Assert of Expr.t
    | BvDefine of Formula.bv_var * Expr.t
    | AxDefine of Formula.ax_var * Memory.t

  and t = {
    mutable id : Suid.t;
    bv_decl : Formula.decl BvTbl.t;
    ax_decl : Formula.decl AxTbl.t;
    bl_cons : Formula.bl_var BvTbl.t;
    bv_cons : Formula.bv_var BvTbl.t;
    ax_cons : Formula.ax_var AxTbl.t;
    ordered : k Queue.t;
    word_size : int;
    debug : name:string -> label:string -> string;
  }

  let create ?(word_size = Kernel_options.Machine.word_size ())
      ?(debug = fun ~name ~label:_ -> name) ~next_id () =
    {
      id = next_id;
      bv_decl = BvTbl.create 16;
      ax_decl = AxTbl.create 1;
      bl_cons = BvTbl.create 32;
      bv_cons = BvTbl.create 128;
      ax_cons = AxTbl.create 64;
      ordered = Queue.create ();
      word_size;
      debug;
    }

  let bl_once = Formula.bl_var "!"
  let bv_once = Formula.bv_var "!" 1
  let ax_once = Formula.ax_var "!" 1 1

  let rec visit_bl ctx bl =
    try
      if BvTbl.find ctx.bl_cons bl == bl_once then (
        let name = Suid.to_string ctx.id in
        ctx.id <- Suid.incr ctx.id;
        BvTbl.replace ctx.bl_cons bl (Formula.bl_var name))
    with Not_found -> (
      match bl with
      | Cst _ -> ()
      | Load _ (* cannot be a bl<1> *) -> assert false
      | Unary { f = Not; x; _ } ->
          BvTbl.add ctx.bl_cons bl bl_once;
          visit_bl ctx x;
          Queue.push (Bl bl) ctx.ordered
      | Binary { f = And | Or; x; y; _ } ->
          BvTbl.add ctx.bl_cons bl bl_once;
          visit_bl ctx x;
          visit_bl ctx y;
          Queue.push (Bl bl) ctx.ordered
      | Binary
          {
            f = Eq | Diff | Uge | Ule | Ugt | Ult | Sge | Sle | Sgt | Slt;
            x;
            y;
            _;
          } ->
          BvTbl.add ctx.bl_cons bl bl_once;
          visit_bv ctx x;
          visit_bv ctx y;
          Queue.push (Bl bl) ctx.ordered
      | Ite { c; t; e; _ } ->
          BvTbl.add ctx.bl_cons bl bl_once;
          visit_bl ctx c;
          visit_bl ctx t;
          visit_bl ctx e;
          Queue.push (Bl bl) ctx.ordered
      | Var _ | Unary _ | Binary _ -> visit_bv ctx bl)

  and visit_bv ctx bv =
    try
      if BvTbl.find ctx.bv_cons bv == bv_once then (
        let name = Suid.to_string ctx.id in
        ctx.id <- Suid.incr ctx.id;
        BvTbl.replace ctx.bv_cons bv (Formula.bv_var name (Expr.sizeof bv)))
    with Not_found -> (
      match bv with
      | Var { name; size; label; _ } ->
          let name = ctx.debug ~name ~label in
          let var = Formula.bv_var name size in
          BvTbl.add ctx.bv_cons bv var;
          BvTbl.add ctx.bv_decl bv (Formula.mk_bv_decl var [])
      | Load { addr; label; _ } ->
          BvTbl.add ctx.bv_cons bv bv_once;
          visit_bv ctx addr;
          visit_ax ctx label;
          Queue.push (Bv bv) ctx.ordered
      | Cst _ ->
          BvTbl.add ctx.bv_cons bv bv_once;
          Queue.push (Bv bv) ctx.ordered
      | Unary { x; _ } ->
          BvTbl.add ctx.bv_cons bv bv_once;
          visit_bv ctx x;
          Queue.push (Bv bv) ctx.ordered
      | Binary
          { f = Eq | Diff | Uge | Ule | Ugt | Ult | Sge | Sle | Sgt | Slt; _ }
        ->
          BvTbl.add ctx.bv_cons bv bv_once;
          visit_bl ctx bv;
          Queue.push (Bv bv) ctx.ordered
      | Binary { x; y; _ } ->
          BvTbl.add ctx.bv_cons bv bv_once;
          visit_bv ctx x;
          visit_bv ctx y;
          Queue.push (Bv bv) ctx.ordered
      | Ite { c; t; e; _ } ->
          BvTbl.add ctx.bv_cons bv bv_once;
          visit_bl ctx c;
          visit_bv ctx t;
          visit_bv ctx e;
          Queue.push (Bv bv) ctx.ordered)

  and visit_ax ctx ax =
    try
      if AxTbl.find ctx.ax_cons ax == ax_once then (
        let name = Suid.to_string ctx.id in
        ctx.id <- Suid.incr ctx.id;
        AxTbl.replace ctx.ax_cons ax (Formula.ax_var name ctx.word_size 8))
    with Not_found -> (
      match ax with
      | Memory.Root ->
          let var =
            Formula.ax_var
              (ctx.debug ~name:memory_name ~label:"memory")
              ctx.word_size 8
          in
          AxTbl.add ctx.ax_cons ax var;
          AxTbl.add ctx.ax_decl ax (Formula.mk_ax_decl var [])
      | Memory.Symbol name ->
          let var =
            Formula.ax_var (ctx.debug ~name ~label:"") ctx.word_size 8
          in
          AxTbl.add ctx.ax_cons ax var;
          AxTbl.add ctx.ax_decl ax (Formula.mk_ax_decl var [])
      | Memory.Layer { addr; store; over; _ } ->
          AxTbl.add ctx.ax_cons ax ax_once;
          visit_bv ctx addr;
          Store.iter_term (fun _ bv -> visit_bv ctx bv) store;
          visit_ax ctx over;
          Queue.push (Ax ax) ctx.ordered)

  let assert_bl ctx bl =
    visit_bl ctx bl;
    Queue.push (Assert bl) ctx.ordered

  let define_bv ctx name bv =
    visit_bv ctx bv;
    let var = Formula.bv_var name (Expr.sizeof bv) in
    Queue.push (BvDefine (var, bv)) ctx.ordered

  let define_ax ctx name ax =
    visit_ax ctx ax;
    let var = Formula.ax_var name ctx.word_size 8 in
    Queue.push (AxDefine (var, ax)) ctx.ordered

  let mk_unop (op : Term.unary Term.operator) =
    match op with
    | Not -> Formula.BvNot
    | Minus -> Formula.BvNeg
    | Uext n -> Formula.BvZeroExtend n
    | Sext n -> Formula.BvSignExtend n
    | Restrict i -> Formula.BvExtract i

  let mk_comp (op : Term.binary Term.operator) =
    match op with
    | Eq -> Formula.BvEqual
    | Diff -> Formula.BvDistinct
    | Uge -> Formula.BvUge
    | Ule -> Formula.BvUle
    | Ugt -> Formula.BvUgt
    | Ult -> Formula.BvUlt
    | Sge -> Formula.BvSge
    | Sle -> Formula.BvSle
    | Sgt -> Formula.BvSgt
    | Slt -> Formula.BvSlt
    | Plus | Minus | Mul | Udiv | Sdiv | Umod | Smod | Or | And | Xor | Concat
    | Lsl | Lsr | Asr | Rol | Ror ->
        assert false

  let mk_bnop (op : Term.binary Term.operator) =
    match op with
    | Eq | Diff | Uge | Ule | Ugt | Ult | Sge | Sle | Sgt | Slt -> assert false
    | Plus -> Formula.BvAdd
    | Minus -> Formula.BvSub
    | Mul -> Formula.BvMul
    | Udiv -> Formula.BvUdiv
    | Sdiv -> Formula.BvSdiv
    | Umod -> Formula.BvUrem
    | Smod -> Formula.BvSmod
    | Or -> Formula.BvOr
    | And -> Formula.BvAnd
    | Xor -> Formula.BvXor
    | Concat -> Formula.BvConcat
    | Lsl -> Formula.BvShl
    | Lsr -> Formula.BvLshr
    | Asr -> Formula.BvAshr
    | Rol | Ror -> assert false

  let rec mk_bl ctx bl =
    try
      let var = BvTbl.find ctx.bl_cons bl in
      if var == bl_once then mk_bl_no_cons ctx bl else Formula.mk_bl_var var
    with Not_found -> Formula.mk_bv_equal (mk_bv ctx bl) Formula.mk_bv_one

  and mk_bl_no_cons ctx bl =
    match bl with
    | Cst bv ->
        if Bitvector.is_one bv then Formula.mk_bl_true else Formula.mk_bl_false
    | Load _ (* cannot be a bl<1> *) -> assert false
    | Unary { f = Not; x; _ } -> Formula.mk_bl_not (mk_bl ctx x)
    | Binary { f = And; x; y; _ } ->
        Formula.mk_bl_and (mk_bl ctx x) (mk_bl ctx y)
    | Binary { f = Or; x; y; _ } -> Formula.mk_bl_or (mk_bl ctx x) (mk_bl ctx y)
    | Binary
        {
          f = (Eq | Diff | Uge | Ule | Ugt | Ult | Sge | Sle | Sgt | Slt) as f;
          x;
          y;
          _;
        } ->
        Formula.mk_bv_comp (mk_comp f) (mk_bv ctx x) (mk_bv ctx y)
    | Ite { c; t; e; _ } ->
        Formula.mk_bl_ite (mk_bl ctx c) (mk_bl ctx t) (mk_bl ctx e)
    | Var _ | Unary _ | Binary _ ->
        Formula.mk_bv_equal (mk_bv ctx bl) Formula.mk_bv_one

  and mk_bv ctx bv =
    let var = BvTbl.find ctx.bv_cons bv in
    if var == bv_once then mk_bv_no_cons ctx bv else Formula.mk_bv_var var

  and mk_bv_no_cons ctx bv =
    match bv with
    | Var _ -> assert false
    | Load { len; dir = LittleEndian; addr; label; _ } ->
        Formula.mk_select len (mk_ax ctx label) (mk_bv ctx addr)
    | Load { len; dir = BigEndian; addr; label; _ } ->
        mk_select_be len (mk_ax ctx label) (mk_bv ctx addr)
    | Cst bv -> Formula.mk_bv_cst bv
    | Unary { f; x; _ } -> Formula.mk_bv_unop (mk_unop f) (mk_bv ctx x)
    | Binary
        { f = Eq | Diff | Uge | Ule | Ugt | Ult | Sge | Sle | Sgt | Slt; _ } ->
        Formula.mk_bv_ite (mk_bl ctx bv) Formula.mk_bv_one Formula.mk_bv_zero
    | Binary { f = Rol; x; y = Cst bv; _ } ->
        Formula.mk_bv_rotate_left (Bv.to_uint bv) (mk_bv ctx x)
    | Binary { f = Ror; x; y = Cst bv; _ } ->
        Formula.mk_bv_rotate_right (Bv.to_uint bv) (mk_bv ctx x)
    | Binary { f = Rol; x; y; _ } ->
        Formula.mk_bv_or
          (Formula.mk_bv_shl (mk_bv ctx x) (mk_bv ctx y))
          (Formula.mk_bv_lshr (mk_bv ctx x)
             (Formula.mk_bv_sub_int (mk_bv ctx y) (Expr.sizeof x)))
    | Binary { f = Ror; x; y; _ } ->
        Formula.mk_bv_or
          (Formula.mk_bv_lshr (mk_bv ctx x) (mk_bv ctx y))
          (Formula.mk_bv_shl (mk_bv ctx x)
             (Formula.mk_bv_sub_int (mk_bv ctx y) (Expr.sizeof x)))
    | Binary { f; x; y; _ } ->
        Formula.mk_bv_bnop (mk_bnop f) (mk_bv ctx x) (mk_bv ctx y)
    | Ite { c; t; e; _ } ->
        Formula.mk_bv_ite (mk_bl ctx c) (mk_bv ctx t) (mk_bv ctx e)

  and mk_ax ctx ax =
    let var = AxTbl.find ctx.ax_cons ax in
    if var == ax_once then mk_ax_no_cons ctx ax else Formula.mk_ax_var var

  and mk_ax_no_cons ctx ax =
    match ax with
    | Memory.Root | Memory.Symbol _ -> assert false
    | Memory.Layer { addr; store; over; _ } ->
        let addr = mk_bv ctx addr in
        Store.fold_term
          (fun i bv store ->
            Formula.mk_store
              (Expr.sizeof bv lsr 3)
              store
              (Formula.mk_bv_add addr
                 (Formula.mk_bv_cst (Bitvector.create i ctx.word_size)))
              (mk_bv ctx bv))
          (mk_ax ctx over) store

  and mk_select_be =
    let rec mk_select_be len ax bv sel =
      if len = 0 then sel
      else
        let len = len - 1 in
        mk_select_be len ax bv
          (Formula.mk_bv_concat sel
             (Formula.mk_select 1 ax (Formula.mk_bv_add_int bv len)))
    in
    fun len ax bv ->
      let len = len - 1 in
      mk_select_be len ax bv
        (Formula.mk_select 1 ax (Formula.mk_bv_add_int bv len))

  let to_formula ctx =
    Queue.fold
      (fun formula -> function
        | Bl bl ->
            let var = BvTbl.find ctx.bl_cons bl in
            if var != bl_once then
              Formula.push_front_define
                (Formula.mk_bl_def var [] (mk_bl_no_cons ctx bl))
                formula
            else formula
        | Bv bv ->
            let var = BvTbl.find ctx.bv_cons bv in
            if var != bv_once then
              Formula.push_front_define
                (Formula.mk_bv_def var [] (mk_bv_no_cons ctx bv))
                formula
            else formula
        | Ax ax ->
            let var = AxTbl.find ctx.ax_cons ax in
            if var != ax_once then
              Formula.push_front_define
                (Formula.mk_ax_def var [] (mk_ax_no_cons ctx ax))
                formula
            else formula
        | Assert bl -> Formula.push_front_assert (mk_bl ctx bl) formula
        | BvDefine (var, bv) ->
            Formula.push_front_define
              (Formula.mk_bv_def var [] (mk_bv ctx bv))
              formula
        | AxDefine (var, ax) ->
            Formula.push_front_define
              (Formula.mk_ax_def var [] (mk_ax ctx ax))
              formula)
      (BvTbl.fold
         (fun _ decl formula -> Formula.push_front_declare decl formula)
         ctx.bv_decl
         (AxTbl.fold
            (fun _ decl formula -> Formula.push_front_declare decl formula)
            ctx.ax_decl Formula.empty))
      ctx.ordered
end

module Solver () : Solver.S = struct
  open Sexpr

  let session =
    Session.start (* ~stdlog:stderr *) (Formula_options.Solver.get ())

  let ctx = ref [ Printer.create ~next_id:Suid.zero () ]
  let top () = List.hd !ctx

  let visit_formula formula =
    let ctx = top () in
    List.iter
      (fun bl ->
        Printer.visit_bl ctx bl;
        Printer.visit_bl ctx bl)
      formula

  let iter_free_variables f = StTbl.iter f (top ()).fvariables
  let iter_free_arrays f = StTbl.iter f (top ()).farrays

  let push () =
    ctx := Printer.copy (List.hd !ctx) :: !ctx;
    Format.pp_print_string session.formatter "(push 1)"

  let pop () =
    ctx := List.tl !ctx;
    Format.pp_print_string session.formatter "(pop 1)"

  let flush_x find visit (ctx : Printer.t) x =
    let name =
      match find ctx x with
      | exception Not_found ->
          visit ctx x;
          visit ctx x;
          find ctx x
      | name ->
          if name == Printer.once || name == Printer.evicted then (
            visit ctx x;
            find ctx x)
          else name
    in
    Printer.pp_flush_defs session.formatter ctx;
    name

  let flush_bl =
    flush_x (fun ctx bl -> BvTbl.find ctx.bl_cons bl) Printer.visit_bl

  let assert_formula bl =
    let ctx = top () in
    (* print declarations *)
    let bl = flush_bl ctx bl in
    (* print assertion *)
    Format.pp_print_string session.formatter "(assert ";
    Format.pp_print_string session.formatter bl;
    Format.pp_print_char session.formatter ')';
    Format.pp_print_space session.formatter ()

  let flush_bv =
    flush_x (fun ctx bv -> BvTbl.find ctx.bv_cons bv) Printer.visit_bv

  let assert_distinct x y =
    let ctx = top () in
    (* print declarations *)
    let x = flush_bv ctx x in
    let y = flush_bv ctx y in
    (* print assertion *)
    Format.pp_print_string session.formatter "(assert (not (= ";
    Format.pp_print_string session.formatter x;
    Format.pp_print_space session.formatter ();
    Format.pp_print_string session.formatter y;
    Format.pp_print_string session.formatter ")))";
    Format.pp_print_space session.formatter ()

  let get_value x =
    let ctx = top () in
    let bv = flush_bv ctx x in
    Session.get_value session Format.pp_print_string bv

  let get_at name x s =
    Session.get_value session
      (fun ppf x ->
        Format.pp_print_string ppf "(select ";
        Format.pp_print_string ppf name;
        Format.pp_print_char ppf ' ';
        pp_bv ppf x s;
        Format.pp_print_char ppf ')')
      x

  let fold_array_values f ar x =
    let ctx = top () in
    match AxTbl.find ctx.ordered_mem ar with
    | exception Not_found -> x
    | history ->
        if Queue.is_empty history then x
        else
          let dirty = BiTbl.create (Queue.length history) in
          let name = Format.asprintf "%a" (Printer.pp_print_ax ctx) ar
          and addr_space = ctx.word_size in
          Queue.fold
            (fun x (access : Printer.access) ->
              match access with
              | Select (index, len) ->
                  let index =
                    Session.get_value session Format.pp_print_string index
                  in
                  let rec fold index len x =
                    if len = 0 then x
                    else if BiTbl.mem dirty index then
                      fold (Z.succ index) (len - 1) x
                    else
                      let k = get_at name index addr_space in
                      fold (Z.succ index) (len - 1) (f index k x)
                  in
                  fold index len x
              | Store (index, len) ->
                  let index =
                    Session.get_value session Format.pp_print_string index
                  in
                  let rec loop index len =
                    if len <> 0 then (
                      BiTbl.replace dirty index ();
                      loop (Z.succ index) (len - 1))
                  in
                  loop index len;
                  x)
            x history

  let check_sat ?timeout () : Libsolver.status =
    Session.check_sat session ~timeout

  let check_sat_assuming ?timeout bl : Libsolver.status =
    let ctx = top () in
    let bl = flush_bl ctx bl in
    Session.check_sat_assuming session ~timeout bl

  let close () = Session.close session
end
