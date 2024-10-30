# Important Notes

## See the list of shared libraries required for an executable

```shell
ldd EXECUTABLE
```

## See the list of environment variables

```shell
env
```

## Set the path of the shared libraries

```shell
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/build/root/usr/lib64
export LD_LIBRARY_PATH
```

## Search for an already executed command

```shell
CTRL + r 
```

## Concatenate a command to a previously executed command

```shell
NEW_INSTRUCTION !!
```

## rpath

https://stackoverflow.com/questions/24598047/why-does-ld-need-rpath-link-when-linking-an-executable-against-a-so-that-needs?rq=3

```
-rpath comes into play at runtime, when the application tries to load the dynamic library. It informs the program
of an additional location to search in when trying to load a dynamic library.
```

```shell
readelf -d EXECUTABLE_FILE
```

Output: 

```
Dynamic section at offset 0x2da0 contains 29 entries:
  Tag        Type                         Name/Value
 0x0000000000000001 (NEEDED)             Shared library: [libcttest.so]
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
 0x000000000000001d (RUNPATH)            Library runpath: [../../../Optimized_Implementation/perk-128-fast-3/build/]
 0x000000000000000c (INIT)               0x1000
 0x000000000000000d (FINI)               0x11b4
 0x0000000000000019 (INIT_ARRAY)         0x3d90
 0x000000000000001b (INIT_ARRAYSZ)       8 (bytes)
 0x000000000000001a (FINI_ARRAY)         0x3d98
 0x000000000000001c (FINI_ARRAYSZ)       8 (bytes)
 0x000000006ffffef5 (GNU_HASH)           0x3b0
 0x0000000000000005 (STRTAB)             0x498
 0x0000000000000006 (SYMTAB)             0x3d8
 0x000000000000000a (STRSZ)              231 (bytes)
 0x000000000000000b (SYMENT)             24 (bytes)
 0x0000000000000015 (DEBUG)              0x0
 0x0000000000000003 (PLTGOT)             0x3fb0
 0x0000000000000002 (PLTRELSZ)           48 (bytes)
 0x0000000000000014 (PLTREL)             RELA
 0x0000000000000017 (JMPREL)             0x680
 0x0000000000000007 (RELA)               0x5c0
 0x0000000000000008 (RELASZ)             192 (bytes)
 0x0000000000000009 (RELAENT)            24 (bytes)
 0x000000000000001e (FLAGS)              BIND_NOW
 0x000000006ffffffb (FLAGS_1)            Flags: NOW PIE
 0x000000006ffffffe (VERNEED)            0x590
 0x000000006fffffff (VERNEEDNUM)         1
 0x000000006ffffff0 (VERSYM)             0x580
 0x000000006ffffff9 (RELACOUNT)          3
 0x0000000000000000 (NULL)               0x0

```