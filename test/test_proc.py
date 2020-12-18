import os
import sys
import time
import unittest

import k3proc
import k3ut

dd = k3ut.dd

this_base = os.path.dirname(__file__)


class TestProc(unittest.TestCase):

    foo_fn = '/tmp/foo'

    def _read_file(self, fn):
        try:
            with open(fn, 'r') as f:
                cont = f.read()
                return cont
        except EnvironmentError:
            return None

    def _clean(self):

        # remove written file
        try:
            os.unlink(self.foo_fn)
        except EnvironmentError:
            pass

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def test_procerror(self):
        inp = (1, 'out', 'err', ['ls', 'a', 'b'], {"close_fds": True})
        ex_args = (1, 'out', 'err', ['out'], ['err'], ['ls', 'a', 'b'], {"close_fds": True})
        ex = k3proc.CalledProcessError(*inp)

        self.assertEqual(ex_args, (ex.returncode,
                                   ex.stdout,
                                   ex.stderr,
                                   ex.out,
                                   ex.err,
                                   ex.cmd,
                                   ex.options))

        self.assertEqual(inp, ex.args)

    def test_error_str_with_capture_false(self):
        try:
            k3proc.command(
                'python', '-c', 'import sys; sys.exit(1)',
                capture=False,
                check=True,
            )
        except k3proc.CalledProcessError as e:
            self.assertEqual('', e.stdout)
            self.assertEqual([], e.out)
            self.assertEqual('', e.stderr)
            self.assertEqual([], e.err)

    def test_error_str(self):

        try:
            k3proc.command(
                'python', '-c', 'import sys; sys.exit(1)',
                check=True,
                env={"foo": "bar"},
                cwd="/tmp",
                input="123")
        except k3proc.CalledProcessError as e:
            s = '\n'.join([
                "CalledProcessError",
                'python -c import sys; sys.exit(1)',
                "options: {'cwd': '/tmp', 'env': {'foo': 'bar'}, 'input': '123'}",
                "exit code: 1"
            ])
            self.assertEqual(s, str(e))
            self.assertEqual(s, repr(e))

    def test_code_out_err(self):

        subproc = os.path.join(this_base, 'subproc.py')

        returncode, out, err = k3proc.command('python', subproc, '222')

        self.assertEqual(222, returncode)
        self.assertEqual('out-1\nout-2\n', out)
        self.assertEqual('err-1\nerr-2\n', err)

        try:
            returncode, out, err = k3proc.command_ex('python', subproc, '222')
        except k3proc.CalledProcessError as e:
            self.assertEqual(222, e.returncode)
            self.assertEqual('out-1\nout-2\n', e.stdout)
            self.assertEqual('out-1\nout-2\n'.splitlines(), e.out)
            self.assertEqual('err-1\nerr-2\n', e.stderr)
            self.assertEqual('err-1\nerr-2\n'.splitlines(), e.err)
            self.assertEqual('python', e.cmd[0])
            self.assertTrue(e.cmd[1].endswith('subproc.py'))
            self.assertEqual('222', e.cmd[2])
            self.assertEqual({}, e.options)
        else:
            self.fail('expect k3proc.CalledProcessError to be raised')

        returncode, out, err = k3proc.command_ex('python', subproc, '0')
        self.assertEqual(0, returncode)
        self.assertEqual('out-1\nout-2\n', out)
        self.assertEqual('err-1\nerr-2\n', err)

        returncode, out, err = k3proc.command('python', subproc, '0')

        self.assertEqual(0, returncode)
        self.assertEqual('out-1\nout-2\n', out)
        self.assertEqual('err-1\nerr-2\n', err)

    def test_text_true(self):

        cmd = ['python', '-c', 'import os; os.write(1, b"\\x89")', ]

        self.assertRaises(
            UnicodeDecodeError,
            k3proc.command,
            *cmd
        )

        returncode, out, err = k3proc.command(*cmd, text=False)

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual(b'\x89', out)

    def test_close_fds(self):

        read_fd = os.path.join(this_base, 'read_fd.py')

        with open(read_fd) as f:
            fd = f.fileno()
            os.set_inheritable(fd, True)

            returncode, out, err = k3proc.command(
                'python', read_fd, str(fd), close_fds=False)

            dd(returncode, out, err)
            self.assertEqual(0, returncode)
            self.assertEqual('###\n', out)
            self.assertEqual('', err)

            returncode, out, err = k3proc.command(
                'python', read_fd, str(fd), close_fds=True)

            self.assertEqual(1, returncode)
            self.assertEqual('errno=9\n', out)
            self.assertEqual('', err)

    def test_cwd(self):

        returncode, out, err = k3proc.command(
            'python', 'subproc.py', '111', cwd=this_base)
        self.assertEqual(111, returncode)

        returncode, out, err = k3proc.command('python', 'subproc.py', '111')
        if 'PyPy' in sys.version:
            # PyPy does not return code correctly. it is 1
            self.assertNotEqual(0, returncode)
        else:
            # 2 for can not find subproc.py
            self.assertEqual(2, returncode)

    def test_env(self):
        returncode, out, err = k3proc.command('python', 'print_env.py', 'abc',
                                              env={"abc": "xyz"},
                                              cwd=this_base)
        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual('xyz\n', out)

    def test_inherit_env(self):

        returncode, out, err = k3proc.command(
            'python', '-c', 'import os; print(os.environ.get("PATH"))',
            env={"abc": "xyz"},
            inherit_env=False,
        )
        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual('None\n', out, "no PATH inherited")

    def test_input(self):

        returncode, out, err = k3proc.command('python', 'read_fd.py', '0',
                                              input='abc',
                                              cwd=this_base)
        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual('abc\n', out)

    def test_timeout(self):

        with k3ut.Timer() as t:
            self.assertRaises(k3proc.TimeoutExpired,
                              k3proc.command, 'python', '-c',
                              'import time; time.sleep(1)',
                              timeout=0.1
                              )
            self.assertLess(t.spent(), 1)

    def test_check(self):

        self.assertRaises(k3proc.CalledProcessError,
                          k3proc.command,
                          'python', '-c',
                          'import sys; sys.exit(5)',
                          check=True,
                          )

    def test_capture(self):

        # no capture

        read_stdin_in_subproc = '''
import k3proc;
k3proc.command(
'python', '-c', 'import sys; print(sys.stdin.read())',
capture={}
)
        '''

        returncode, out, err = k3proc.command(
            'python', '-c',
            read_stdin_in_subproc.format('False'),
            input="123",
        )

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual("123\n", out)

        # capture

        returncode, out, err = k3proc.command(
            'python', '-c',
            read_stdin_in_subproc.format('True'),
            input="123",
        )

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual("", out)

        # default capture

        returncode, out, err = k3proc.command(
            'python', '-c',
            read_stdin_in_subproc.format('None'),
            input="123",
        )

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual("", out)

    def test_tty(self):

        returncode, out, err = k3proc.command(
            'python', '-c', 'import sys; print(sys.stdout.isatty())',
            tty=True,
        )

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)

        self.assertEqual('True\n', out)
        self.assertEqual("", err)

        # without pseudo tty, no color outupt:

        _, out, _ = k3proc.command(
            'python', '-c', 'import sys; print(sys.stdout.isatty())',
            tty=False,
        )

        self.assertEqual('False\n', out)

        # by default no tty:

        _, out, _ = k3proc.command(
            'python', '-c', 'import sys; print(sys.stdout.isatty())',
        )

        self.assertEqual('False\n', out)

    def test_shell_script(self):

        returncode, out, err = k3proc.shell_script(
            'ls ' + this_base + ' | grep init | grep -v pyc')

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual('__init__.py\n', out)

    def test_start_process(self):

        cases = (
            ('python', this_base + '/write.py', ['foo'], 'foo'),
            ('python', this_base + '/write.py', ['foo', 'bar'], 'foobar'),
            ('sh', this_base + '/write.sh', ['123'], '123'),
            ('sh', this_base + '/write.sh', ['123', '456'], '123456'),
        )

        for cmd, target, args, expected in cases:
            k3proc.start_process(cmd, target, os.environ, *args)
            time.sleep(0.1)
            self.assertEqual(expected, self._read_file(self.foo_fn))
