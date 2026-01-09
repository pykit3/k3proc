# k3proc

[![Build Status](https://github.com/pykit3/k3proc/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3proc/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3proc/badge/?version=stable)](https://k3proc.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3proc)](https://pypi.org/project/k3proc)

easy to use `Popen`

k3proc is a component of [pykit3] project: a python3 toolkit set.


k3proc is utility to create sub process.

Execute a shell script::

    >>> returncode, out, err = k3proc.shell_script('ls / | grep bin')

Run a command::

    # Unlike the above snippet, following statement does not start an sh process.
    returncode, out, err = k3proc.command('ls', 'a*', cwd='/usr/local')




# Install

```
pip install k3proc
```

# Synopsis

```python
>>> returncode, out, err = k3proc.shell_script('ls / | grep bin')

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3