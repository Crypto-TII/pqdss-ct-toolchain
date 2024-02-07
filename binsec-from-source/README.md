# Build Binsec from sources


## Clone binsec repository
Clone binsec repository at: https://github.com/binsec/binsec



## Build gmp

For more details, please visit:
https://rstudio-pubs-static.s3.amazonaws.com/493124_a46782f9253a4b8193595b6b2a037d58.html


```bash
$ cd gmp-6.1.2
$ ./configure --prefix=/usr  --enable-cxx
$ make
$ make check
$ make install
```


## Build Binsec


From https://github.com/binsec/binsec/blob/master/INSTALL.md

Move to `binsec` folder
```bash
$ cd binsec

```

```bash
$ opam install dune menhir grain_dypgen ocamlgraph zarith toml
$ opam install bitwuzla # optional -- for native SMT solver binding
$ opam install unisim_archisec # optional -- for x86-64, ARMv7 and ARMv8
$ opam install curses # optional -- for real time summary window
```

```bash
$ opan install dune-site

```

```bash
$ make
$ make install

```