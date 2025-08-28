#!/usr/bin/env python
# coding: utf-8

"""
build steup.py for this package.
"""

import ast
import subprocess
import sys
from string import Template

import requirements
import yaml

if hasattr(sys, "getfilesystemencoding"):
    defenc = sys.getfilesystemencoding()
if defenc is None:
    defenc = sys.getdefaultencoding()


def parse_assignment(filename, var_name):
    """Parse a Python file and extract the value of a variable assignment using AST."""
    with open(filename, "r") as f:
        content = f.read()

    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Check if this assignment is to our target variable
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    # Extract the literal value
                    if isinstance(node.value, ast.Constant):  # Python 3.8+
                        return node.value.value
                    elif isinstance(node.value, ast.Str):  # Python < 3.8
                        return node.value.s
                    elif isinstance(node.value, ast.Num):  # Python < 3.8
                        return node.value.n

    return None


def get_name():
    name = parse_assignment("__init__.py", "__name__")
    return name if name is not None else "k3git"  # fallback


name = get_name()


def get_ver():
    version = parse_assignment("__init__.py", "__version__")
    if version is None:
        raise ValueError("Could not find __version__ in __init__.py")
    return version


def get_gh_config():
    with open(".github/settings.yml", "r") as f:
        cont = f.read()

    cfg = yaml.safe_load(cont)
    tags = cfg["repository"]["topics"].split(",")
    tags = [x.strip() for x in tags]
    cfg["repository"]["topics"] = tags
    return cfg


def get_travis():
    try:
        with open(".travis.yml", "r") as f:
            cont = f.read()
    except OSError:
        return None

    cfg = yaml.safe_load(cont)
    return cfg


def get_compatible():
    # https://pypi.org/classifiers/

    rst = []
    t = get_travis()
    if t is None:
        return ["Programming Language :: Python :: 3"]

    for v in t["python"]:
        if v.startswith("pypy"):
            v = "Implementation :: PyPy"
        rst.append("Programming Language :: Python :: {}".format(v))

    return rst


def get_req():
    try:
        with open("requirements.txt", "r") as f:
            req = list(requirements.parse(f))
    except OSError:
        req = []

    # req.name, req.specs, req.extras
    # Django [('>=', '1.11'), ('<', '1.12')]
    # six [('==', '1.10.0')]
    req = [x.name + ",".join([a + b for a, b in x.specs]) for x in req]

    return req


cfg = get_gh_config()

ver = get_ver()
description = cfg["repository"]["description"]
long_description = open("README.md").read()
req = get_req()
prog = get_compatible()


tmpl = """# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="${name}",
    packages=["${name}"],
    version="$ver",
    license='MIT',
    description=$description,
    long_description=$long_description,
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/$name',
    keywords=$topics,
    python_requires='>=3.0',

    install_requires=$req,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + $prog,
)
"""

s = Template(tmpl)
rst = s.substitute(
    name=name,
    ver=ver,
    description=repr(description),
    long_description=repr(long_description),
    topics=repr(cfg["repository"]["topics"]),
    req=repr(req),
    prog=repr(prog),
)
with open("setup.py", "w") as f:
    f.write(rst)


sb = subprocess.Popen(
    ["git", "add", "setup.py"],
    encoding=defenc,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
out, err = sb.communicate()
if sb.returncode != 0:
    raise Exception("failure to add: ", out, err)

sb = subprocess.Popen(
    ["git", "commit", "setup.py", "-m", "release: v" + ver],
    encoding=defenc,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
out, err = sb.communicate()
if sb.returncode != 0:
    raise Exception("failure to commit new release: " + ver, out, err)


sb = subprocess.Popen(
    ["git", "tag", "v" + ver],
    encoding=defenc,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
out, err = sb.communicate()
if sb.returncode != 0:
    raise Exception("failure to add tag: " + ver, out, err)
