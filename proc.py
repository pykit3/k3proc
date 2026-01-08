#!/usr/bin/env python
from __future__ import annotations

import errno
import io
import logging
import os
import select
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, Sequence

try:
    import pty
except ModuleNotFoundError:
    # Windows does not support pty (no termios module)
    class pty:  # type: ignore[no-redef]
        @staticmethod
        def openpty() -> tuple[int, int]:
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

    returncode: int
    stdout: str | bytes
    stderr: str | bytes
    cmd: list[str]
    options: dict[str, Any]
    out: list[str] | list[bytes]
    err: list[str] | list[bytes]

    def __init__(
        self,
        returncode: int,
        out: str | bytes,
        err: str | bytes,
        cmd: list[str],
        options: dict[str, Any],
    ) -> None:
        super().__init__(returncode, cmd, output=out, stderr=err)

        self.returncode = returncode
        self.stdout = out
        self.stderr = err
        self.cmd = cmd
        self.options = options

        self.out = out.splitlines()
        self.err = err.splitlines()

    def __str__(self) -> str:
        s: list[str] = [
            self.__class__.__name__,
            " ".join(self.cmd),
            "options: " + str(self.options),
            "exit code: " + str(self.returncode),
        ]

        for line in self.out:
            if isinstance(line, bytes):
                s.append(repr(line))
            else:
                s.append(line)

        for line in self.err:
            if isinstance(line, bytes):
                s.append(repr(line))
            else:
                s.append(line)
        return "\n".join(s)

    def __repr__(self) -> str:
        return self.__str__()


ProcError = CalledProcessError
TimeoutExpired = subprocess.TimeoutExpired


def command(
    cmd: str | Sequence[str],
    *arguments: str,
    bufsize: int = -1,
    close_fds: bool = True,
    creationflags: int = 0,
    cwd: str | bytes | os.PathLike[str] | os.PathLike[bytes] | None = None,
    encoding: str | None = None,
    env: Mapping[str, str] | None = None,
    errors: str | None = None,
    executable: str | bytes | os.PathLike[str] | os.PathLike[bytes] | None = None,
    pass_fds: Sequence[int] = (),
    preexec_fn: Callable[[], Any] | None = None,
    restore_signals: bool = True,
    shell: bool = False,
    start_new_session: bool = False,
    startupinfo: Any = None,
    stderr: int | None = None,
    stdin: int | None = None,
    stdout: int | None = None,
    text: bool | None = None,
    universal_newlines: bool | None = None,
    # extended args
    input: str | bytes | None = None,
    check: bool = False,
    inherit_env: bool | None = None,
    timeout: float | None = None,
    capture: bool | None = None,
    tty: bool | None = None,
) -> tuple[int, str | bytes, str | bytes]:
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

    merged_env: Mapping[str, str] | None
    if inherit_env:
        merged_env = dict(os.environ, **(env or {}))
    else:
        merged_env = env

    cmds: list[str]
    if isinstance(cmd, str):
        cmds = [cmd] + list(arguments)
    else:
        cmds = list(cmd)

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

    subproc = subprocess.Popen(  # type: ignore[call-overload, misc]
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

    out: str | bytes
    err: str | bytes

    if tty:
        out_chunks: list[bytes] = []
        err_chunks: list[bytes] = []

        now = time.time()

        while subproc.poll() is None:
            r, _, _ = select.select([err_master_fd, out_master_fd], [], [], 0.01)
            if out_master_fd in r:
                o = os.read(out_master_fd, 10240)
                out_chunks.append(o)
            if err_master_fd in r:
                o = os.read(err_master_fd, 10240)
                err_chunks.append(o)
            if timeout is not None and time.time() - now > timeout:
                subproc.kill()
                subproc.wait()
                raise TimeoutExpired(" ".join(cmds), timeout)

        out_bytes = b"".join(out_chunks)
        err_bytes = b"".join(err_chunks)

        if text_mode:
            out = io.TextIOWrapper(io.BytesIO(out_bytes), encoding=encoding, errors=errors).read()
            err = io.TextIOWrapper(io.BytesIO(err_bytes), encoding=encoding, errors=errors).read()
        else:
            out = out_bytes
            err = err_bytes

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
        opts: dict[str, Any] = {}
        if cwd is not None:
            opts["cwd"] = cwd
        if env is not None:
            opts["env"] = env
        if input is not None:
            opts["input"] = input

        raise CalledProcessError(subproc.returncode, out, err, cmds, opts)
    return (subproc.returncode, out, err)


def command_ex(
    cmd: str | Sequence[str],
    *arguments: str,
    **options: Any,
) -> tuple[int, str | bytes, str | bytes]:
    """
    This is a shortcut of `command` with `check=True`:
    if sub process exit code is not 0, it raises exception
    `CalledProcessError`.

    """

    options["check"] = True
    return command(cmd, *arguments, **options)


def shell_script(
    script_str: str,
    **options: Any,
) -> tuple[int, str | bytes, str | bytes]:
    """
    This is a shortcut of `command("sh", input=script_str)`.

    Run a shell script::

        shell_script('ls | grep foo.txt')

    """

    options["input"] = script_str
    return command("sh", **options)


def _waitpid(pid: int) -> None:
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


def _close_fds() -> None:
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


def start_process(
    cmd: str,
    target: str,
    env: Mapping[str, str],
    *args: str,
) -> None:
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
        args_list: list[Any] = list(args)
        merged_env = dict(os.environ, **env)
        args_list.append(merged_env)
        try:
            os.execlpe(cmd, cmd, target, *args_list)
        except Exception:
            # Can't use logger here - GIL deadlock risk in forked child.
            # Exit with non-zero code to signal failure to parent.
            os._exit(1)
    else:
        _waitpid(pid)
