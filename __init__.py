"""
pk3proc is utility to create sub process.

Execute a shell script::

    import pk3proc

    # execute a shell script

    returncode, out, err = pk3proc.shell_script('ls / | grep bin')
    print returncode
    print out
    # output:
    # > 0
    # > bin
    # > sbin

Run a command::

    # Unlike the above snippet, following statement does not start an sh process.
    returncode, out, err = pk3proc.command('ls', 'a*', cwd='/usr/local')

"""

from .proc import CalledProcessError
from .proc import ProcError
from .proc import TimeoutExpired
from .proc import command
from .proc import command_ex
from .proc import shell_script
from .proc import start_process

__version__ = "0.2.0"

__all__ = [
    'CalledProcessError',
    'TimeoutExpired',
    'ProcError',
    'command',
    'command_ex',
    'shell_script',
    'start_process',
]
