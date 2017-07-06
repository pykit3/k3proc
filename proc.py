
import subprocess


class ProcError(Exception):

    def __init__(self, returncode, out, err, cmd, arguments, options):

        super(ProcError, self).__init__(returncode,
                                        out,
                                        err,
                                        cmd,
                                        arguments,
                                        options)

        self.returncode = returncode
        self.out = out
        self.err = err
        self.command = cmd
        self.arguments = arguments
        self.options = options


def command(cmd, *arguments, **options):

    close_fds = options.get('close_fds', True)
    cwd = options.get('cwd', None)
    env = options.get('env', None)
    stdin = options.get('stdin', None)

    subproc = subprocess.Popen([cmd] + list(arguments),
                               close_fds=close_fds,
                               cwd=cwd,
                               env=env,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, )

    out, err = subproc.communicate(input=stdin)

    subproc.wait()

    return (subproc.returncode, out, err)


def command_ex(cmd, *arguments, **options):
    returncode, out, err = command(cmd, *arguments, **options)
    if returncode != 0:
        raise ProcError(returncode, out, err, cmd, arguments, options)


def shell_script(script_str, **options):
    options['stdin'] = script_str
    return command('sh', **options)
