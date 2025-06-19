
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.glibcLocales
    pkgs.imagemagick_light
    pkgs.stdenv.cc.cc.lib
    pkgs.glibc
    pkgs.gcc-unwrapped.lib
    pkgs.libcxx
    pkgs.libcxxabi
    pkgs.zlib
    pkgs.openssl
  ];
  env = {
    LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.glibc}/lib:${pkgs.gcc-unwrapped.lib}/lib";
  };
}
