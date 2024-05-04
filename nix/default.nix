{ lib
, python3
, ps
, writeShellScript
, callPackage
,
}:

let
  pipwrap = writeShellScript "pipwrapper" ''
    exec python -m pip "$@"
  '';
  shtuff = with python3.pkgs; buildPythonApplication rec {
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

    nativeCheckInputs = [
      pip
    ];

    checkPhase = ''
      # venv uses ensurepip internally to install pip, which requires
      # internet access, and fails in an isolated build environment.
      # Instead, we hack together a pip that simply calls `python -m
      # pip`. There must be a better way of doing this...
      python -m venv venv --without-pip
      cp ${pipwrap} venv/bin/pip
      source venv/bin/activate

      make test
    '';

    postPatch = ''
      # shtuff uses `ps` internally. Point that to a direct path to ps.
      substituteInPlace shtuff.py \
        --replace-fail "ps -p" "${ps}/bin/ps -p"
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


  };

  unpywrap = callPackage ./unpywrap.nix { };
in

unpywrap shtuff
