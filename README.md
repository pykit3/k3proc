<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
#   Table of Content

- [Name](#name)
- [Status](#status)
- [Description](#description)
- [Synopsis](#synopsis)
- [Exceptions](#exceptions)
  - [proc.CalledProcessError](#proccalledprocesserror)
  - [proc.ProcError](#procprocerror)
- [Methods](#methods)
  - [proc.command](#proccommand)
  - [proc.command_ex](#proccommand_ex)
  - [proc.shell_script](#procshell_script)
  - [proc.start_process](#procstart_process)
- [Author](#author)
- [Copyright and License](#copyright-and-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

[![Build Status](https://travis-ci.com/drmingdrmer/pykit3proc.svg?branch=master)](https://travis-ci.com/drmingdrmer/pykit3proc)

#   Name

proc

#   Status

This library is considered production ready.

#   Description

Utility to create sub process.

#   Synopsis

```python
from pykit import proc

# execute a shell script

returncode, out, err = proc.shell_script('ls / | grep bin')
print returncode
print out
# output:
# > 0
# > bin
# > sbin

# Or run a command directly.
# Unlike the above snippet, following statement does not start an sh process.

returncode, out, err = proc.command('ls', 'a*', cwd='/usr/local')
```

```python
# a.py
import sys

with open('foo', 'w') as f:
    f.write(str(sys.argv))

# b.py
import time
from pykit import proc

proc.start_daemon('python', './a.py', 'test')
time.sleep(1)
try:
    with open('foo', 'r') as f:
        print repr(f.read())
except Exception as e:
    print repr(e)
```

#   Exceptions

##  proc.CalledProcessError

**syntax**:
`proc.CalledProcessError(returncode, out, err, cmd, arguments, options)`

It is sub class of `subprocess.CalledProcessError`.

It is raised if a sub process return code is not `0`.
Besides `CalledProcessError.args`, extended from super class `Exception`, it has 6
other attributes.

**attributes**:
<!-- TODO env -->

-   `CalledProcessError.returncode`:   process exit code.
-   `CalledProcessError.out`:          stdout in one string.
-   `CalledProcessError.err`:          stderr in one string.
-   `CalledProcessError.cmd`:          the command a process `exec()`.
-   `CalledProcessError.arguments`:    tuple of command arguments.
-   `CalledProcessError.options`:      other options passed to this process. Such as `close_fds`, `cwd` etc.

##  proc.ProcError

It is an alias to `proc.CalledProcessError`.

#   Methods

##  proc.command

**syntax**:
`proc.command(cmd, *arguments, **options)`

Run a `command` with arguments `arguments` in a subprocess.
It blocks until sub process exit.

**arguments**:

-   `cmd`:
    The path of executable to run.

-   `arguments`:
    is tuple or list of arguments passed to `cmd`.

-   `options`:
    is a dictionary of additional options, which are same as `subprocess.Popen`.
    But with some different default value for easy use:

    -   `encoding`: by default is the system default encoding.

    -   `env`: by default inherit from parent process.

    It also accept the following additional options:

    -   `check=False`: if `True`, raise `CalledProcessError` if returncode is not 0.
        By default it is `False`.

    -   `capture=True`: whether to capture stdin, stdout and stderr.
        Otherwise inherit these fd from current process.

    -   `inherit_env=True`: whether to inherit evironment vars from current process.

    -   `input=None`: input to send to stdin, if it is not None.

    -   `timeout=None`: seconds to wait for sub process to exit.
        By default it is None, for waiting for ever.

    -   `tty=False`: whether to create a speudo tty to run sub process so that
        the sub process believes it is in a tty(just like controlled by a
        human).


**return**:
a 3 element tuple that contains:

-   `returncode`:   sub process exit code in `int`.
-   `out`:  sub process stdout in a single string.
-   `err`:  sub process stderr in a single string.

##  proc.command_ex

**syntax**:
`proc.command_ex(cmd, *arguments, **options)`

It is the same as `proc.command` except that if sub process exit code is not
0, it raises exception `proc.CalledProcessError`.

See `proc.CalledProcessError`.

**return**:
a 3 element tuple of `returncode`, `out` and `err`, or raise exception
`proc.CalledProcessError`.

##  proc.shell_script

**syntax**:
`proc.shell_script(script_str, **options)`

It is just a shortcut of:
```
options['stdin'] = script_str
return command('sh', **options)
```

##  proc.start_process

**syntax**:
`proc.start_process(cmd, target, env, *args)`

Create a child process and replace it with `cmd`.
Besides `stdin`, `stdout` and `stderr`, all file
descriptors from parent process will be closed in
the child process. The parent process waits for
the child process until it is completed.

**arguments**:

-   `cmd`:
    The path of executable to run.
    Such as `sh`, `bash`, `python`.

-   `target`:
    The path of the script.

-   `env`:
    It is a dictionary to pass environment variables
    to the child process.

-   `*args`:
    Type is `tuple` or `list`.
    The arguments passed to the script.
    Type of every element must be `str`.

**return**:
nothing

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
