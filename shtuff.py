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

from pkg_resources import get_distribution, DistributionNotFound

CONFIG_DIR = os.path.expanduser("~/.config/shtuff/")

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('to_stuff', type=str, nargs='?', default='', help='Keys to stuff')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('--into', metavar="name", help='The name of the Shtuffee to run the command')
    parser.add_argument('-n', dest="suppress_newline", action='store_true', help='Suppress new lines, similar to echo')
    args = parser.parse_args()

    cmd = args.to_stuff
    if not args.suppress_newline:
        cmd += "\n"

    if args.into is None:
        spawn_and_stuff(os.environ['SHELL'], cmd)
    else:
        stuff(args.into, cmd)

def stuff(target, to_stuff):
    pid_file = get_pid_file(target)
    with open(pid_file) as f:
        pid = int(f.read().strip())

    with open(get_cmd_file(pid), 'w') as f:
        f.write(to_stuff)

    os.kill(pid, signal.SIGUSR1)

def get_pid_file(name):
    return os.path.join(CONFIG_DIR, "{name}.pid".format(name=name))

def get_cmd_file(pid):
    return os.path.join(CONFIG_DIR, "{pid}.command".format(pid=pid))

def shtuffee():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='The name of the Shtuffee to run the command')
    parser.add_argument('-v', '--version', action='version', version=__version__)

    name = parser.parse_args().name
    pid_file = get_pid_file(name)
    pid = find_nearest_shtuff_process()

    if not pid:
        spawn_and_stuff(os.environ['SHELL'], f'shtuffee {name}\n')

    with open(pid_file, 'w') as f:
        f.write(str(pid))


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
