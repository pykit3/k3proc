#!/usr/bin/env python
# coding: utf-8

import errno
import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)

defenc = None

if hasattr(sys, 'getfilesystemencoding'):
    defenc = sys.getfilesystemencoding()

if defenc is None:
    defenc = sys.getdefaultencoding()


class CalledProcessError(subprocess.CalledProcessError):

    def __init__(self, returncode, out, err, cmd, options):

        if sys.version_info.major == 3 and sys.version_info.minor >= 5:
            super(CalledProcessError, self).__init__(returncode,
                                                     cmd,
                                                     output=out,
                                                     stderr=err,
                                                     )
        else:
            # python 3.4 has no stderr arg
            super(CalledProcessError, self).__init__(returncode,
                                                     cmd,
                                                     output=out,
                                                     )

        self.returncode = returncode
        self.out = out
        self.err = err
        self.cmd = cmd
        self.options = options


ProcError = CalledProcessError
TimeoutExpired = subprocess.TimeoutExpired


def command(cmd, *arguments,
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
            inherit_env=True,
            timeout=None,
            capture=None,
            ):

    if encoding is None:
        encoding = defenc

    if inherit_env:
        if env is not None:
            env = dict(os.environ, **env)

    if isinstance(cmd, (list, tuple)):
        cmds = cmd
    else:
        cmds = [cmd] + list(arguments)

    if capture is None:
        capture = True

    if capture:
        io = {
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        }
    else:
        io = {}

    subproc = subprocess.Popen(cmds,

                               bufsize=bufsize,
                               close_fds=close_fds,
                               creationflags=creationflags,
                               cwd=cwd,
                               encoding=encoding,
                               env=env,
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
                               **io
                               )

    try:
        out, err = subproc.communicate(input=input, timeout=timeout)
    except TimeoutExpired:
        subproc.kill()
        subproc.wait()
        raise

    subproc.wait()

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
    options["check"] = True
    return command(cmd, *arguments, **options)


def shell_script(script_str, **options):
    options['input'] = script_str
    return command('sh', **options)


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

    try:
        pid = os.fork()
    except OSError as e:
        logger.error(repr(e) + ' while fork')
        raise

    if pid == 0:
        _close_fds()
        args = list(args)
        env = dict(os.environ, **env)
        args.append(env)
        try:
            os.execlpe(cmd, cmd, target, *args)
        except Exception:
            # we can do nothing when error in execlpe
            # don't logger here, logger need get GIL lock
            # children process may dead lock
            pass
    else:
        _waitpid(pid)


def _bytes(s):
    if isinstance(s, str):
        return bytes(s, 'utf-8')
    return s
