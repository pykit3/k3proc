"""
k3proc is utility to create sub process.

Execute a shell script::

    >>> returncode, out, err = k3proc.shell_script('ls / | grep bin')

Run a command::

    # Unlike the above snippet, following statement does not start an sh process.
    returncode, out, err = k3proc.command('ls', 'a*', cwd='/usr/local')

"""

from .proc import CalledProcessError, ProcError, TimeoutExpired, command, command_ex, shell_script, start_process

__all__ = [
    "CalledProcessError",
    "ProcError",
    "TimeoutExpired",
    "command",
    "command_ex",
    "shell_script",
    "start_process",
]


def __getattr__(name: str) -> str:
    # importlib.metadata takes about 20 ms to import, so it is loaded only
    # when __version__ is read
    if name != "__version__":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib.metadata import version

    return version("k3proc")
