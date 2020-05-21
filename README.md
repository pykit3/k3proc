# pk3proc

[![Build Status](https://travis-ci.com/pykit3/pk3proc.svg?branch=master)](https://travis-ci.com/pykit3/pk3proc)

TODO badge for doc.

pk3proc is utility to create sub process.

# Synopsis

```python
import pk3proc

# execute a shell script
returncode, out, err = pk3proc.shell_script('ls / | grep bin')
print returncode
print out
# output:
# > 0
# > bin
# > sbin
```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>
