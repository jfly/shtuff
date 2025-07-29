#!/usr/bin/env python3

import os
import sys
import fcntl
import base64
import psutil
import signal
import struct
import pexpect
import termios
import argparse
import subprocess
import setproctitle
import xdg.BaseDirectory

from textwrap import dedent
from importlib.metadata import version, PackageNotFoundError


def data_dir(file=None):
    data_dir = xdg.BaseDirectory.save_data_path("shtuff")

    if file is None:
        return data_dir

    return os.path.join(data_dir, file)


try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # package is not installed
    __version__ = "development"


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
    parser.add_argument("-v", "--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(metavar="action")

    parser_as = subparsers.add_parser("as", help="become a receiving shell")
    parser_as.add_argument(
        "name",
        help="the current shell will take this name, use `shtuff into` to send commands here",
    )
    parser_as.set_defaults(func=shtuff_as)

    def add_newline_argument(parser):
        parser.add_argument(
            "-n",
            dest="newline",
            action="store_false",
            help="don't send a trailing newline, similar to echo",
        )

    parser_into = subparsers.add_parser(
        "into", help="send a command to a receiving shell"
    )
    parser_into.add_argument(
        "name", help="the name of the shell to send the given command to"
    )
    parser_into.add_argument("cmd", help="the command to send to the shell")
    add_newline_argument(parser_into)
    parser_into.set_defaults(func=shtuff_into)

    parser_new = subparsers.add_parser(
        "new", help="start a new shell and immediately send a command"
    )
    parser_new.add_argument(
        "cmd", help="start a new shell and immediately run the given command"
    )
    add_newline_argument(parser_new)
    parser_new.set_defaults(func=shtuff_new)

    parser_has = subparsers.add_parser(
        "has", help="check to see if target is available to receive commands"
    )
    parser_has.add_argument(
        "name", help="the name of the shell to send the given command to"
    )
    parser_has.set_defaults(func=shtuff_has)

    parser_whoami = subparsers.add_parser(
        "whoami", help="print any found receiver names for the current shtuff shell"
    )
    parser_whoami.set_defaults(func=shtuff_whoami)

    args = vars(parser.parse_args())
    if not args:
        return parser.print_help()

    func = args.pop("func")
    func(**args)


def shtuff_as(name):
    pid = find_nearest_shtuff_process()

    if not pid:
        spawn_and_stuff(os.environ["SHELL"], name=name)
        return

    write_shtuff_pid(name, pid)


def write_shtuff_pid(name, pid):
    pid_file = get_pid_file(name)
    with open(pid_file, "w") as f:
        f.write(str(pid))


def shtuff_into(name, cmd, newline):
    if newline:
        cmd += "\n"

    pid_file = get_pid_file(name)
    if not os.path.exists(pid_file):
        print_target_not_found(name)
        exit(1)

    pid = get_pid_from_file(pid_file)

    with open(get_cmd_file(pid), "w") as f:
        f.write(cmd)

    if shtuff_process_has_terminated(pid):
        print_target_not_found(name)
        exit(1)

    os.kill(pid, signal.SIGUSR1)


def shtuff_new(cmd, newline):
    if newline:
        cmd += "\n"

    spawn_and_stuff(os.environ["SHELL"], to_stuff=cmd)


def shtuff_has(name):
    pid_file = get_pid_file(name)

    if not os.path.exists(pid_file):
        print_target_not_found(name)
        exit(1)

    pid = get_pid_from_file(pid_file)

    if shtuff_process_has_terminated(pid):
        print_target_not_found(name)
        exit(1)

    print(f"Shtuff process {name} was found with pid of {pid}.")


def shtuff_whoami():
    pid = find_nearest_shtuff_process()

    if pid is None:
        print(
            "Error: this is not a shtuff shell. Use 'shtuff new' or 'shtuff as' to make one.",
            file=sys.stderr,
        )
        sys.exit(1)

    pid_files = [x for x in os.listdir(data_dir()) if os.path.splitext(x)[1] == ".pid"]
    receivers = sorted(
        get_unsafe_name(x) for x in pid_files if get_pid_from_file(data_dir(x)) == pid
    )

    if len(receivers) == 0:
        print(
            "Warning: this shtuff has no name. Use 'shtuff as' to give it a name.",
            file=sys.stderr,
        )
        return

    print("\n".join(receivers))


def get_unsafe_name(name):
    return base64.urlsafe_b64decode(name.replace(".pid", "")).decode("utf8")


def get_pid_file(name):
    safe_name = base64.urlsafe_b64encode(name.encode("utf8")).decode("utf8")
    return data_dir(f"{safe_name}.pid")


def get_pid_from_file(pid_file):
    with open(pid_file) as f:
        return int(f.read().strip())


def get_cmd_file(pid):
    return data_dir(f"{pid}.command")


def get_process_command(pid):
    return (
        subprocess.run(
            f"ps -p {pid} -o command",
            capture_output=True,
            shell=True,
        )
        .stdout.decode()
        .split("\n")[-2]
        .strip()
    )


def find_nearest_shtuff_process():
    def ppid(process):
        parent = process.parent()
        if parent is None or parent.pid == process.pid:
            return None

        if get_process_command(parent.pid) == "shtuff":
            return parent.pid

        return ppid(parent)

    return ppid(psutil.Process())


def spawn_and_stuff(to_spawn, to_stuff=None, name=None):
    setproctitle.setproctitle("shtuff")

    p = pexpect.spawn(to_spawn)

    def resize():
        s = struct.pack("HHHH", 0, 0, 0, 0)
        a = struct.unpack(
            "hhhh", fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
        )
        p.setwinsize(a[0], a[1])

    # Trap SIGWINCH and pass it down to our spawned process.
    # http://pexpect.readthedocs.io/en/stable/api/pexpect.html#pexpect.spawn.interact
    signal.signal(signal.SIGWINCH, lambda sig, data: resize())
    resize()

    shtuff_pid = os.getpid()

    def read_and_stuff_command():
        cmd_file = get_cmd_file(shtuff_pid)

        try:
            with open(cmd_file) as f:
                p.send(f.read())
        except FileNotFoundError:
            print(
                f"\nReceived SIGUSR1, tried to read commands from {cmd_file}, but could not open the file.\n",
                file=sys.stderr,
            )

    signal.signal(signal.SIGUSR1, lambda sig, data: read_and_stuff_command())

    if to_stuff:
        p.send(to_stuff)

    if name:
        write_shtuff_pid(name, shtuff_pid)

    p.interact()


def print_target_not_found(name):
    print(f"Shtuff target {name} was not found.", file=sys.stderr)


def shtuff_process_has_terminated(pid):
    return get_process_command(pid) != "shtuff"


if __name__ == "__main__":
    main()
