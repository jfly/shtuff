import os
import shutil
import pexpect
import unittest
import subprocess

class TestShtuff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['HOME'] = os.path.join(os.environ['PWD'], 'tests/build/fake_home')
        os.environ['XDG_DATA_HOME'] = os.path.join(os.environ['HOME'], 'xdg_data_home/')
        os.environ['SHELL'] = 'bash'

        os.makedirs(os.environ['HOME'], exist_ok=True)

        bashrc = os.path.join(os.environ['HOME'], '.bashrc')
        with open(bashrc, 'w') as f:
            f.write("PS1='$ '")

    def setUp(self):
        if os.path.exists(os.environ['XDG_DATA_HOME']):
            shutil.rmtree(os.environ['XDG_DATA_HOME'])

    def test_shtuff_new(self):
        child = pexpect.spawn("shtuff new 'echo foo\nexit'")
        child.expect("foo")

    def test_shtuff_single_receiver(self):
        receiver = pexpect.spawn("shtuff as receiver")
        receiver.expect('\$')
        receiver.expect('\$')

        os.system("shtuff into receiver 'echo foo'")
        receiver.expect('foo')

    def test_shtuff_single_receiver_can_be_aliased(self):
        receiver = pexpect.spawn("shtuff as receiver")
        receiver.expect('\$')
        receiver.expect('\$')

        os.system("shtuff into receiver 'shtuff as aliased'")
        receiver.expect('aliased')
        receiver.expect('\$')

        os.system("shtuff into aliased 'echo bar'")
        receiver.expect('bar')

    def test_shtuff_multiple_receivers(self):
        receiverA = pexpect.spawn("shtuff as receiverA")
        receiverA.expect('\$')
        receiverA.expect('\$')

        receiverB = pexpect.spawn("shtuff as receiverB")
        receiverB.expect('\$')
        receiverB.expect('\$')

        os.system("shtuff into receiverA 'echo foo'")
        receiverA.expect('foo')

        os.system("shtuff into receiverB 'echo bar'")
        receiverB.expect('bar')

    def test_shtuff_without_args_shows_help(self):
        child = pexpect.spawn("shtuff")
        child.expect("usage")

    def test_shtuff_with_bad_target_gracefully_dies(self):
        receiver = pexpect.spawn("shtuff as receiver")
        receiver.expect('\$')
        receiver.expect('\$')

        out = subprocess.run("shtuff into badreceiver 'echo foo'", shell=True, capture_output=True, encoding='utf-8')
        assert out.returncode == 1
        assert 'not found' in out.stderr
