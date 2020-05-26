"""
k3proc is utility to create sub process.

Execute a shell script::

    >>> returncode, out, err = k3proc.shell_script('ls / | grep bin')

Run a command::

    # Unlike the above snippet, following statement does not start an sh process.
    returncode, out, err = k3proc.command('ls', 'a*', cwd='/usr/local')

"""

from .proc import CalledProcessError
from .proc import ProcError
from .proc import TimeoutExpired
from .proc import command
from .proc import command_ex
from .proc import shell_script
from .proc import start_process

__version__ = "0.2.3"
_name = 'k3proc'

__all__ = [
    'CalledProcessError',
    'TimeoutExpired',
    'ProcError',
    'command',
    'command_ex',
    'shell_script',
    'start_process',
]
