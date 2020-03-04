#!/usr/bin/env python
# coding: utf-8

import errno
import logging
import os
import sys

import subprocess


logger = logging.getLogger(__name__)


class CalledProcessError(subprocess.CalledProcessError):

    def __init__(self, returncode, out, err, cmd, arguments, options):

        if sys.version_info.major == 3 and sys.version_info.minor >= 5:
            super(CalledProcessError, self).__init__(returncode,
                                                     str([cmd] + list(arguments)),
                                                     output=out,
                                                     stderr=err, 
                                            )
        else:
            # python 3.4 has no stderr arg
            super(CalledProcessError, self).__init__(returncode,
                                                     str([cmd] + list(arguments)),
                                                     output=out,
                                            )

        self.returncode = returncode
        self.out = out
        self.err = err
        self.command = cmd
        self.arguments = arguments
        self.options = options

ProcError = CalledProcessError

def command(cmd, *arguments, **options):

    close_fds = options.get('close_fds', True)
    cwd = options.get('cwd', None)
    shell = options.get('shell', False)
    env = options.get('env', None)
    if env is not None:
        env = dict(os.environ, **env)
    stdin = options.get('stdin', None)

    arguments = [_bytes(x) for x in arguments]
    stdin = _bytes(stdin)


    subproc = subprocess.Popen([cmd] + list(arguments),
                                 close_fds=close_fds,
                                 shell=shell,
                                 cwd=cwd,
                                 env=env,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, )

    out, err = subproc.communicate(input=stdin)

    subproc.wait()

    return (subproc.returncode, out, err)


def command_ex(cmd, *arguments, **options):
    returncode, out, err = command(cmd, *arguments, **options)
    if returncode != 0:
        raise CalledProcessError(returncode, out, err, cmd, arguments, options)

    return returncode, out, err


def shell_script(script_str, **options):
    options['stdin'] = script_str
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
