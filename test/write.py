#!/usr/bin/env python2

import sys

fn = "/tmp/foo"


def write_file(fn, cont):
    with open(fn, "w") as f:
        f.write(cont)


if __name__ == "__main__":
    args = sys.argv[1:]
    write_file(fn, "".join(args))
