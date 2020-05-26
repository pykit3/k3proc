# k3proc

[![Build Status](https://travis-ci.com/pykit3/k3proc.svg?branch=master)](https://travis-ci.com/pykit3/k3proc)
[![Documentation Status](https://readthedocs.org/projects/k3proc/badge/?version=stable)](https://k3proc.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3proc)](https://pypi.org/project/k3proc)

easy to use `Popen`

k3proc is a component of [pykit3] project: a python3 toolkit set.


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