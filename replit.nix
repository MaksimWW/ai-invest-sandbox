{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.keydb
    pkgs.stdenv.cc.cc.lib
    pkgs.gcc-unwrapped.lib
    pkgs.glibc
    pkgs.libgcc
    pkgs.gccStdenv
  ];
}