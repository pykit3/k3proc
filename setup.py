# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="k3proc",
    packages=["."],
    version="0.2.6",
    license='MIT',
    description='easy to use `Popen`',
    long_description="# k3proc\n\n[![Build Status](https://travis-ci.com/pykit3/k3proc.svg?branch=master)](https://travis-ci.com/pykit3/k3proc)\n[![Documentation Status](https://readthedocs.org/projects/k3proc/badge/?version=stable)](https://k3proc.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3proc)](https://pypi.org/project/k3proc)\n\neasy to use `Popen`\n\nk3proc is a component of [pykit3] project: a python3 toolkit set.\n\n\n# Install\n\n```\npip install k3proc\n```\n\n# Synopsis\n\n```python\n>>> returncode, out, err = k3proc.shell_script('ls / | grep bin')\n\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3",
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/k3proc',
    keywords=['subprocess', 'popen'],
    python_requires='>=3.0',

    install_requires=['semantic_version~=2.8.5', 'jinja2~=2.11.2', 'PyYAML~=5.3.1', 'sphinx~=3.3.1', 'k3ut~=0.1.7'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + ['Programming Language :: Python :: 3.6', 'Programming Language :: Python :: 3.7', 'Programming Language :: Python :: 3.8', 'Programming Language :: Python :: Implementation :: PyPy'],
)
