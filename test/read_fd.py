#######################
# unit test case read this file
import os
import sys

fd = int(sys.argv[1])

try:
    a = os.read(fd, 3)
    os.write(1, a)
    os.write(1, b"\n")
    sys.exit(0)
except OSError as e:
    print(('errno=' + str(e.errno)))
    sys.exit(1)
