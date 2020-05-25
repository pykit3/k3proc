import pk3proc

# execute a shell script
returncode, out, err = pk3proc.shell_script('ls / | grep bin')
print returncode
print out
# output:
# > 0
# > bin
# > sbin
