{ pkgs }:

# Call the wrapped Python application directly. The problem with the wrappers
# is that they set the `PATH` (and perhaps less importantly, the
# `PYTHONNOUSERSITE`) environment variables (relevant nix code here:
# https://github.com/NixOS/nixpkgs/blob/7682f18720f3cc0a0abfbb47e9e7612f83141f01/pkgs/development/interpreters/python/wrap.sh#L75),
# which impacts subprocesses in undesirable ways. I don't know why nix needs
# the PATH env var set, because it already edited the `#!`s at the top of the
# relevant files to point at the correct python. The `PYTHONNOUSERSITE` is
# important (to make sure we don't import some random version of
# the same application that we `pip install --local`-ed at some point, but that can be
# replicated with python's `-s` parameter. I guess the only weirdness here
# would be if the Python process itself decided to try to invoke python as a
# subprocess, but that feels like a weird thing to do.
# TODO: seek help upstream with nix to see if there's a more appropriate
# way of accomplishing all this.
pyapp: pkgs.symlinkJoin {
  name = pyapp.name;
  paths = [ pyapp ];
  buildInputs = [ pkgs.makeWrapper ];
  postBuild = ''
    rm -r $out/bin/*
    for full_path in ${pyapp}/bin/.*-wrapped; do
      f=$(basename $full_path)
      f=''${f#.}  # remove leading dot
      f=''${f%-wrapped}  # remove trailing -wrapped

      # Add the -s parameter to the python #!, because we're bypassing
      # the wrapper script that sets the PYTHONNOUSERSITE env var.
      sed "1s/\(.*\)/\1 -s/" ${pyapp}/bin/.$f-wrapped > $out/bin/$f

      chmod +x $out/bin/$f
    done
  '';
}
