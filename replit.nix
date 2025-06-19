{ pkgs }: {
  deps = [
    pkgs.glibcLocales
    pkgs.imagemagick_light
    pkgs.stdenv.cc.cc.lib
    pkgs.glibc
    pkgs.gcc-unwrapped.lib
  ];
}