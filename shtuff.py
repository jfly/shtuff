#!/usr/bin/env python3

import os
import sys
import fcntl
import signal
import struct
import pexpect
import termios
import argparse
import subprocess
import setproctitle

from textwrap import dedent
from pkg_resources import get_distribution, DistributionNotFound

CONFIG_DIR = os.path.expanduser("~/.shtuff/")

os.makedirs(CONFIG_DIR, exist_ok=True)

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

def main():
    parser = argparse.ArgumentParser(
        description="Shtuff will stuff commands into a shell à la tmux send-keys or screen stuff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Examples:
                In shell A, run:
                  $ shtuff as shell-a

                In shell B, run:
                  $ shtuff into shell-a "git status"

                Observe how shell A ran "git status"

                An example use case for `shtuff new` might be a setup script to
                open a couple shells automatically. Consider this script:
                  #!/usr/bin/env bash
                  termite -e "shtuff new vim" &
                  termite -e "shtuff new 'tail -f /var/log/somelog.log'" &

                This script will open two terminals, one running vim, and one
                running tail.
        """),
    )
    parser.add_argument('-v', '--version', action='version', version=__version__)
    subparsers = parser.add_subparsers(metavar="action")

    parser_as = subparsers.add_parser('as', help='become a receiving shell')
    parser_as.add_argument('name', help='the current shell will take this name, use `shtuff into` to send commands here')
    parser_as.set_defaults(func=shtuff_as)

    def add_newline_argument(parser):
        parser.add_argument('-n', dest="newline", action='store_false', help="don't send a trailing newline, similar to echo")

    parser_into = subparsers.add_parser('into', help='send a command to a receiving shell')
    parser_into.add_argument('name', help='the name of the shell to send the given command to')
    parser_into.add_argument('cmd', help='the command to send to the shell')
    add_newline_argument(parser_into)
    parser_into.set_defaults(func=shtuff_into)

    parser_new = subparsers.add_parser('new', help='start a new shell and immediately send a command')
    parser_new.add_argument('cmd', help='start a new shell and immediately run the given command')
    add_newline_argument(parser_new)
    parser_new.set_defaults(func=shtuff_new)


    args = vars(parser.parse_args())
    func = args.pop('func')
    func(**args)

def shtuff_as(name):
    pid_file = get_pid_file(name)
    pid = find_nearest_shtuff_process()

    if not pid:
        spawn_and_stuff(os.environ['SHELL'], f'shtuff as {name}\n')

    with open(pid_file, 'w') as f:
        f.write(str(pid))

def shtuff_into(name, cmd, newline):
    if newline:
        cmd += "\n"

    pid_file = get_pid_file(name)
    with open(pid_file) as f:
        pid = int(f.read().strip())

    with open(get_cmd_file(pid), 'w') as f:
        f.write(cmd)

    os.kill(pid, signal.SIGUSR1)

def shtuff_new(cmd, newline):
    if newline:
        cmd += "\n"

    spawn_and_stuff(os.environ['SHELL'], cmd)

def get_pid_file(name):
    return os.path.join(CONFIG_DIR, "{name}.pid".format(name=name))

def get_cmd_file(pid):
    return os.path.join(CONFIG_DIR, "{pid}.command".format(pid=pid))

def find_nearest_shtuff_process():
    return subprocess.run(
        """pstree -lps $$ | grep -Eo "shtuff\([0-9]+\)" | grep -Eo '[0-9]+'""",
        shell=True,
        capture_output=True,
    ).stdout.decode().strip()

def spawn_and_stuff(to_spawn, to_stuff):
    setproctitle.setproctitle("shtuff")

    p = pexpect.spawn(to_spawn)
    def resize():
        s = struct.pack("HHHH", 0, 0, 0, 0)
        a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ , s))
        p.setwinsize(a[0], a[1])

    # Trap SIGWINCH and pass it down to our spawned process.
    # http://pexpect.readthedocs.io/en/stable/api/pexpect.html#pexpect.spawn.interact
    signal.signal(signal.SIGWINCH, lambda sig, data: resize())
    resize()

    def read_and_stuff_command():
        cmd_file = get_cmd_file(os.getpid())

        try:
            with open(cmd_file) as f:
                p.send(f.read())
        except FileNotFoundError:
            print("\nReceived SIGUSR1, tried to read commands from {}, but could not open the file.\n".format(CMD_FILE), file=sys.stderr)
    signal.signal(signal.SIGUSR1, lambda sig, data: read_and_stuff_command())

    p.send(to_stuff)
    p.interact()

if __name__ == "__main__":
    main()
