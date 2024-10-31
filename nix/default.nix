{
  lib,
  python3,
  ps,
  writeShellScript,
}:

let
  pipwrap = writeShellScript "pipwrapper" ''
    exec python -m pip "$@"
  '';
in

with python3.pkgs;
buildPythonApplication rec {
  pname = "shtuff";
  version = builtins.readFile ../VERSION;

  src = ../.;

  propagatedBuildInputs = [
    pexpect
    psutil
    pyxdg
    setproctitle
    setuptools
    setuptools_scm
  ];

  nativeCheckInputs = [ pip ];

  checkPhase = ''
    make test
  '';

  postPatch = ''
    # shtuff uses `ps` internally. Point that to a direct path to ps.
    substituteInPlace shtuff.py \
    --replace-fail "ps -p" "${ps}/bin/ps -p"
  '';

  # Don't wrap the Python application. The problem with the wrappers
  # is that they set the `PATH` (and perhaps less importantly, the
  # `PYTHONNOUSERSITE`) environment variables (relevant nix code here:
  # https://github.com/NixOS/nixpkgs/blob/7682f18720f3cc0a0abfbb47e9e7612f83141f01/pkgs/development/interpreters/python/wrap.sh#L75),
  # which impacts subprocesses in undesirable ways.
  dontWrapPythonPrograms = true;
  postFixup = ''
    buildPythonPath $out
    patchPythonScript $out/bin/shtuff
  '';

  meta = with lib; {
    inherit version;
    description = "It's like screen's stuff command, without screen";
    longDescription = ''
      Shell stuff will stuff commands into a shell à la tmux send-keys or screen stuff.
    '';
    homepage = "https://github.com/jfly/shtuff";
    license = licenses.mit;
  };
}
