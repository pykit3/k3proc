import os

fn = "/tmp/foo"

# Check the standard descriptors before opening `fn`, which takes the lowest free descriptor.
open_fds = []
for fd in (0, 1, 2):
    try:
        os.fstat(fd)
    except OSError:
        continue
    open_fds.append(str(fd))

with open(fn, "w") as f:
    f.write(" ".join(open_fds))
