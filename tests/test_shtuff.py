import os
import shutil
import pexpect
import unittest
import subprocess

SHTUFF = 'python -c "import shtuff; shtuff.main()"'


class TestShtuff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["HOME"] = os.path.join(os.environ["PWD"], "tests/build/fake_home")
        os.environ["XDG_DATA_HOME"] = os.path.join(os.environ["HOME"], "xdg_data_home/")
        os.environ["SHELL"] = "bash"

        if os.path.exists(os.environ["HOME"]):
            shutil.rmtree(os.environ["HOME"])

        os.makedirs(os.environ["HOME"], exist_ok=True)

        bashrc = os.path.join(os.environ["HOME"], ".bashrc")
        with open(bashrc, "w") as f:
            f.write("PS1='$ '")

    def setUp(self):
        if os.path.exists(os.environ["XDG_DATA_HOME"]):
            shutil.rmtree(os.environ["XDG_DATA_HOME"])

    def test_shtuff_new(self):
        child = pexpect.spawn(f"{SHTUFF} new 'echo foo\nexit'")
        child.expect("foo")

    def test_shtuff_single_receiver(self):
        receiver = pexpect.spawn(f"{SHTUFF} as receiver")
        receiver.expect("\\$")

        subprocess.run(f"{SHTUFF} into receiver 'echo foo'", shell=True, check=True)
        receiver.expect("foo")

    def test_shtuff_single_receiver_can_be_aliased(self):
        receiver = pexpect.spawn(f"{SHTUFF} as receiver")
        receiver.expect("\\$")

        subprocess.run(
            f"{SHTUFF} into receiver '{SHTUFF} as aliased'", shell=True, check=True
        )
        receiver.expect("aliased")
        receiver.expect("\\$")

        subprocess.run(f"{SHTUFF} into aliased 'echo bar'", shell=True, check=True)
        receiver.expect("bar")

    def test_shtuff_multiple_receivers(self):
        receiverA = pexpect.spawn(f"{SHTUFF} as receiverA")
        receiverA.expect("\\$")

        receiverB = pexpect.spawn(f"{SHTUFF} as receiverB")
        receiverB.expect("\\$")

        subprocess.run(f"{SHTUFF} into receiverA 'echo foo'", shell=True, check=True)
        receiverA.expect("foo")

        subprocess.run(f"{SHTUFF} into receiverB 'echo bar'", shell=True, check=True)
        receiverB.expect("bar")

    def test_shtuff_without_args_shows_help(self):
        child = pexpect.spawn(SHTUFF)
        child.expect("usage")

    def test_shtuff_with_bad_target_gracefully_dies(self):
        receiver = pexpect.spawn(f"{SHTUFF} as receiver")
        receiver.expect("\\$")

        out = subprocess.run(
            f"{SHTUFF} into badreceiver 'echo foo'",
            shell=True,
            capture_output=True,
            encoding="utf-8",
        )
        self.assertEqual(out.returncode, 1)
        self.assertIn("not found", out.stderr)

    def test_shtuff_exit(self):
        receiver = pexpect.spawn(f"{SHTUFF} as receiver")
        receiver.expect("\\$")

        subprocess.run(f"{SHTUFF} into receiver exit", shell=True, check=True)
        receiver.expect("exit")
        receiver.expect("exit")
        receiver.wait()

        out = subprocess.run(
            f"{SHTUFF} into receiver ls",
            shell=True,
            capture_output=True,
            encoding="utf-8",
        )
        self.assertEqual(out.returncode, 1)
        self.assertIn("not found", out.stderr)

    def test_shtuff_has(self):
        receiver = pexpect.spawn(f"{SHTUFF} as cheezeburgerz")
        receiver.expect("\\$")

        out = subprocess.run(
            f"{SHTUFF} has cheezeburgerz",
            shell=True,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        )
        self.assertIn("was found", out.stdout)

    def test_shtuff_does_not_have(self):
        out = subprocess.run(
            f"{SHTUFF} has cheezeburgerz",
            shell=True,
            capture_output=True,
            encoding="utf-8",
        )
        self.assertEqual(out.returncode, 1)
        self.assertIn("not found", out.stderr)

    def test_shtuff_does_not_have_after_exit(self):
        receiver = pexpect.spawn(f"{SHTUFF} as cheezeburgerz")
        receiver.expect("\\$")
        subprocess.run(f"{SHTUFF} into cheezeburgerz exit", shell=True, check=True)
        receiver.expect("exit")
        receiver.expect("exit")
        receiver.wait()

        out = subprocess.run(
            f"{SHTUFF} has cheezeburgerz",
            shell=True,
            capture_output=True,
            encoding="utf-8",
        )
        self.assertEqual(out.returncode, 1)
        self.assertIn("not found", out.stderr)
