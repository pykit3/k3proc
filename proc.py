#!/usr/bin/env python

import errno
import io
import logging
import os
import select
import subprocess
import sys
import time

try:
    import pty
except ModuleNotFoundError:
    # Windows does not support pty (no termios module)
    class pty:
        @staticmethod
        def openpty():
            raise NotImplementedError("PTY not supported on this platform")


logger = logging.getLogger(__name__)

defenc = sys.getfilesystemencoding() or sys.getdefaultencoding()


class CalledProcessError(subprocess.CalledProcessError):
    """
    It is sub class of `subprocess.CalledProcessError`.

    It is raised if a sub process return code is not `0`.
    Besides `CalledProcessError.args`, extended from super class `Exception`, it
    has 6 other attributes.

    Attributes:
        returncode(int): process exit code.
        stdout(str):     stdout in one string.
        stderr(str):     stderr in one string.
        out(list):       stdout in list.
        err(list):       stderr in list.
        cmd(list):       the command a process `exec()`.
        options(dict):   other options passed to this process. Such as
                         `close_fds`, `cwd` etc.
    """

    def __init__(self, returncode, out, err, cmd, options):
        super().__init__(returncode, cmd, output=out, stderr=err)

        self.returncode = returncode
        self.stdout = out
        self.stderr = err
        self.cmd = cmd
        self.options = options

        self.out = out.splitlines()
        self.err = err.splitlines()

    def __str__(self):
        s = [
            self.__class__.__name__,
            " ".join(self.cmd),
            "options: " + str(self.options),
            "exit code: " + str(self.returncode),
        ]

        for line in self.out:
            if isinstance(line, bytes):
                line = repr(line)
            s.append(line)

        for line in self.err:
            if isinstance(line, bytes):
                line = repr(line)
            s.append(line)
        return "\n".join(s)

    def __repr__(self):
        return self.__str__()


ProcError = CalledProcessError
TimeoutExpired = subprocess.TimeoutExpired


def command(
    cmd,
    *arguments,
    bufsize=-1,
    close_fds=True,
    creationflags=0,
    cwd=None,
    encoding=None,
    env=None,
    errors=None,
    executable=None,
    pass_fds=(),
    preexec_fn=None,
    restore_signals=True,
    shell=False,
    start_new_session=False,
    startupinfo=None,
    stderr=None,
    stdin=None,
    stdout=None,
    text=None,
    universal_newlines=None,
    # extended args
    input=None,
    check=False,
    inherit_env=None,
    timeout=None,
    capture=None,
    tty=None,
):
    """
    Run a `cmd` with arguments `arguments` in a subprocess.
    It blocks until sub process exit or timeout.

    By default it runs in ``text`` mode, i.e., stdin, stdout and stderr are
    encoded into string. Unless ``text=False``, ``encoding=some_encoding``,
    ``error=some_str`` or ``universal_newlines=True`` is specified.

    `**options` are the same as `subprocess.Popen`.
    Only those differ from `subprocess.Popen` are listed.

    Args:
        cmd(list, tuple, str): The path of executable to run.

        arguments(list, tuple): arguments passed to `cmd`.

        encoding: by default is the system default encoding.

        env: by default inherit from parent process.

        `check=False`: if `True`, raise `CalledProcessError` if returncode is not 0.
            By default it is `False`.

        `capture=True`: whether to capture stdin, stdout and stderr.
            Otherwise inherit these fd from current process.

        `inherit_env=True`: whether to inherit evironment vars from current process.

        `input=None`: input to send to stdin, if it is not None.

        `timeout=None`: seconds to wait for sub process to exit.
            By default it is None, for waiting for ever.

        `tty=False`: whether to create a pseudo tty to run sub process so that
            the sub process believes it is in a tty(just like controlled by a
            human). ``tty`` is NOT supported by Windows.

    Returns:
        (int, str, str):
            -   `returncode`: sub process exit code.
            -   `out`:        sub process stdout.
            -   `err`:        sub process stderr.

    Raises:
        CalledProcessError: If the sub process exit with non-zero and `check=True`.
        TimeoutExpired: If `timeout` is not `None` and expires before sub process exit.

    """

    # https://docs.python.org/3/library/io.html
    # io.TextIOWrapper:
    #     errors is an optional string that specifies how encoding and decoding
    #     errors are to be handled. Pass 'strict' to raise a ValueError
    #     exception if there is an encoding error (the default of None has the
    #     same effect), or pass 'ignore' to ignore errors. (Note that ignoring
    #     encoding errors can lead to data loss.) 'replace' causes a replacement
    #     marker (such as '?') to be inserted where there is malformed data.
    #     'backslashreplace' causes malformed data to be replaced by a
    #     backslashed escape sequence.  When writing, 'xmlcharrefreplace'
    #     (replace with the appropriate XML character reference) or
    #     'namereplace' (replace with \N{...} escape sequences) can be used. Any
    #     other error handling name that has been registered with
    #     codecs.register_error() is also valid.
    # text is alias to universal_newlines

    text_mode = text in (None, True) and universal_newlines in (None, True)

    if text_mode:
        if encoding is None:
            encoding = defenc

    if capture is None:
        capture = True

    if tty is None:
        tty = False

    # tty mode only support capture mode
    if tty:
        capture = True

    if inherit_env is None:
        inherit_env = True

    if inherit_env:
        merged_env = dict(os.environ, **(env or {}))
    else:
        merged_env = env

    if isinstance(cmd, (list, tuple)):
        cmds = cmd
    else:
        cmds = [cmd] + list(arguments)

    if tty:
        # If to run in a tty,
        # fake a tty and collect stdout and stderr.
        out_master_fd, out_slave_fd = pty.openpty()
        err_master_fd, err_slave_fd = pty.openpty()
        ioopt = {
            # TODO 'stdin':
            "stdout": out_slave_fd,
            "stderr": err_slave_fd,
        }
    else:
        if capture:
            ioopt = {
                "stdin": subprocess.PIPE,
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
            }

        else:
            ioopt = {}

    subproc = subprocess.Popen(
        cmds,
        bufsize=bufsize,
        close_fds=close_fds,
        creationflags=creationflags,
        cwd=cwd,
        encoding=encoding,
        env=merged_env,
        errors=errors,
        executable=executable,
        pass_fds=pass_fds,
        preexec_fn=preexec_fn,
        restore_signals=restore_signals,
        shell=shell,
        start_new_session=start_new_session,
        startupinfo=startupinfo,
        text=text,
        universal_newlines=universal_newlines,
        **ioopt,
    )

    if tty:
        out = []
        err = []

        now = time.time()

        while subproc.poll() is None:
            r, _, _ = select.select([err_master_fd, out_master_fd], [], [], 0.01)
            if out_master_fd in r:
                o = os.read(out_master_fd, 10240)
                out.append(o)
            if err_master_fd in r:
                o = os.read(err_master_fd, 10240)
                err.append(o)
            if timeout is not None and time.time() - now > timeout:
                subproc.kill()
                subproc.wait()
                raise TimeoutExpired(" ".join(cmds), timeout)

        out = b"".join(out)
        err = b"".join(err)

        if text_mode:
            out = io.TextIOWrapper(io.BytesIO(out), encoding=encoding, errors=errors).read()
            err = io.TextIOWrapper(io.BytesIO(err), encoding=encoding, errors=errors).read()

    else:
        try:
            out, err = subproc.communicate(input=input, timeout=timeout)
        except TimeoutExpired:
            subproc.kill()
            subproc.wait()
            raise

        if out is None:
            out = ""
        if err is None:
            err = ""

    if check and subproc.returncode != 0:
        opts = {}
        if cwd is not None:
            opts["cwd"] = cwd
        if env is not None:
            opts["env"] = env
        if input is not None:
            opts["input"] = input

        raise CalledProcessError(subproc.returncode, out, err, cmds, opts)
    return (subproc.returncode, out, err)


def command_ex(cmd, *arguments, **options):
    """
    This is a shortcut of `command` with `check=True`:
    if sub process exit code is not 0, it raises exception
    `CalledProcessError`.

    """

    options["check"] = True
    return command(cmd, *arguments, **options)


def shell_script(script_str, **options):
    """
    This is a shortcut of `command("sh", input=script_str)`.

    Run a shell script::

        shell_script('ls | grep foo.txt')

    """

    options["input"] = script_str
    return command("sh", **options)


def _waitpid(pid):
    while True:
        try:
            os.waitpid(pid, 0)
            break
        except OSError as e:
            # In case we encountered an OSError due to EINTR (which is
            # caused by a SIGINT or SIGTERM signal during
            # os.waitpid()), we simply ignore it and enter the next
            # iteration of the loop, waiting for the child to end.  In
            # any other case, this is some other unexpected OS error,
            # which we don't want to catch, so we re-raise those ones.
            if e.errno != errno.EINTR:
                raise


def _close_fds():
    # Try to get list of open FDs efficiently via /proc or /dev
    for fd_dir in ("/proc/self/fd", "/dev/fd"):
        try:
            fds = [int(fd) for fd in os.listdir(fd_dir)]
            for fd in fds:
                try:
                    os.close(fd)
                except OSError:
                    pass
            return
        except (OSError, ValueError):
            continue

    # Fallback: iterate through all possible FDs
    try:
        max_fd = os.sysconf("SC_OPEN_MAX")
    except ValueError:
        max_fd = 65536

    for i in range(max_fd):
        try:
            os.close(i)
        except OSError:
            pass


def start_process(cmd, target, env, *args):
    """
    Create a child process and replace it with `cmd`.  Besides `stdin`, `stdout`
    and `stderr`, all file descriptors from parent process will be closed in the
    child process.
    The parent process waits for the child process until it is completed.

    Args:

        cmd(str): The path of executable to run.
            Such as `sh`, `bash`, `python`.

        target(str): The path of the script.

        env(dict): pass environment variables to the child process.

        *args: The arguments passed to the script.
            Type of every element must be `str`.
    """

    try:
        pid = os.fork()
    except OSError as e:
        logger.error(repr(e) + " while fork")
        raise

    if pid == 0:
        _close_fds()
        args = list(args)
        env = dict(os.environ, **env)
        args.append(env)
        try:
            os.execlpe(cmd, cmd, target, *args)
        except Exception:
            # Can't use logger here - GIL deadlock risk in forked child.
            # Exit with non-zero code to signal failure to parent.
            os._exit(1)
    else:
        _waitpid(pid)
