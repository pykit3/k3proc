# k3proc

[![Action-CI](https://github.com/pykit3/k3proc/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3proc/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3proc/badge/?version=stable)](https://k3proc.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3proc)](https://pypi.org/project/k3proc)

Utility to create subprocess with support for timeout, tty, and text mode.

k3proc is a component of [pykit3](https://github.com/pykit3) project: a python3 toolkit set.

## Installation

```bash
pip install k3proc
```

## Quick Start

Execute a shell script:

```python
import k3proc

returncode, out, err = k3proc.shell_script('ls / | grep bin')
```

Run a command (without starting a shell process):

```python
returncode, out, err = k3proc.command('ls', 'a*', cwd='/usr/local')
```

Run with check=True to raise exception on non-zero exit:

```python
try:
    returncode, out, err = k3proc.command_ex('false')
except k3proc.CalledProcessError as e:
    print(f"Command failed with code {e.returncode}")
```

## API Reference

::: k3proc

## License

The MIT License (MIT) - Copyright (c) 2015 Zhang Yanpo (张炎泼)
