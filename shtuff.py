#!/usr/bin/env python3

import os
import sys
import fcntl
import signal
import struct
import pexpect
import termios
import argparse
import setproctitle

from pkg_resources import get_distribution, DistributionNotFound

CMD_FILE = os.path.expanduser("~/.config/shtuff/{pid}.command".format(pid=os.getpid()))

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('to_spawn', type=str, help='Command to spawn')
    parser.add_argument('to_stuff', type=str, nargs='?', default='', help='Keys to stuff')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    args = parser.parse_args()
    spawn_and_stuff(args.to_spawn, args.to_stuff)

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
        try:
            with open(CMD_FILE) as f:
                p.send(f.read())
        except FileNotFoundError:
            print("\nReceived SIGUSR1, tried to read commands from {}, but could not open the file.\n".format(CMD_FILE), file=sys.stderr)
    signal.signal(signal.SIGUSR1, lambda sig, data: read_and_stuff_command())

    p.send(to_stuff)
    p.interact()

if __name__ == "__main__":
    main()
