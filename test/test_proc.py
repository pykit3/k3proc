import os
import sys
import time
import unittest

import pykit3proc
import pykit3ut

dd = pykit3ut.dd

this_base = os.path.dirname(__file__)


class TestProcError(unittest.TestCase):

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
        ex_args = (1, 'out', 'err', 'ls', ('a', 'b'), {"close_fds": True})
        ex = pykit3proc.ProcError(*ex_args)

        self.assertEqual(ex_args, (ex.returncode,
                                   ex.out,
                                   ex.err,
                                   ex.command,
                                   ex.arguments,
                                   ex.options))

        self.assertEqual(ex_args, ex.args)

    def test_code_out_err(self):

        subproc = os.path.join(this_base, 'subproc.py')

        returncode, out, err = pykit3proc.command('python', subproc, '222')

        self.assertEqual(222, returncode)
        self.assertEqual(b'out-1\nout-2\n', out)
        self.assertEqual(b'err-1\nerr-2\n', err)

        try:
            returncode, out, err = pykit3proc.command_ex('python', subproc, '222')
        except pykit3proc.ProcError as e:
            self.assertEqual(222, e.returncode)
            self.assertEqual(b'out-1\nout-2\n', e.out)
            self.assertEqual(b'err-1\nerr-2\n', e.err)
            self.assertEqual('python', e.command)
            self.assertTrue(e.arguments[0].endswith('subproc.py'))
            self.assertEqual('222', e.arguments[1])
            self.assertEqual({}, e.options)
        else:
            self.fail('expect pykit3proc.ProcError to be raised')

        returncode, out, err = pykit3proc.command_ex('python', subproc, '0')
        self.assertEqual(0, returncode)
        self.assertEqual(b'out-1\nout-2\n', out)
        self.assertEqual(b'err-1\nerr-2\n', err)

        returncode, out, err = pykit3proc.command('python', subproc, '0')

        self.assertEqual(0, returncode)
        self.assertEqual(b'out-1\nout-2\n', out)
        self.assertEqual(b'err-1\nerr-2\n', err)

    def test_close_fds(self):

        read_fd = os.path.join(this_base, 'read_fd.py')

        with open(read_fd) as f:
            fd = f.fileno()
            os.set_inheritable(fd, True)

            returncode, out, err = pykit3proc.command(
                'python', read_fd, str(fd), close_fds=False)

            dd(returncode, out, err)
            self.assertEqual(0, returncode)
            self.assertEqual(b'###\n', out)
            self.assertEqual(b'', err)

            returncode, out, err = pykit3proc.command(
                'python', read_fd, str(fd), close_fds=True)

            self.assertEqual(1, returncode)
            self.assertEqual(b'errno=9\n', out)
            self.assertEqual(b'', err)

    def test_cwd(self):

        returncode, out, err = pykit3proc.command(
            'python', 'subproc.py', '111', cwd=this_base)
        self.assertEqual(111, returncode)

        returncode, out, err = pykit3proc.command('python', 'subproc.py', '111')
        if 'PyPy' in sys.version:
            # PyPy does not return code correctly. it is 1
            self.assertNotEqual(0, returncode)
        else:
            # 2 for can not find subproc.py
            self.assertEqual(2, returncode)

    def test_env(self):
        returncode, out, err = pykit3proc.command('python', 'print_env.py', 'abc',
                                            env={"abc": "xyz"},
                                            cwd=this_base)
        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual(b'xyz\n', out)

    def test_stdin(self):

        returncode, out, err = pykit3proc.command('python', 'read_fd.py', '0',
                                            stdin='abc',
                                            cwd=this_base)
        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual(b'abc\n', out)

    def test_shell_script(self):

        returncode, out, err = pykit3proc.shell_script(
            'ls ' + this_base + ' | grep init | grep -v pyc')

        dd('returncode:', returncode)
        dd('out:', out)
        dd('err:', err)

        self.assertEqual(0, returncode)
        self.assertEqual(b'__init__.py\n', out)

    def test_start_process(self):

        cases = (
            ('python', this_base + '/write.py', ['foo'], 'foo'),
            ('python', this_base + '/write.py', ['foo', 'bar'], 'foobar'),
            ('sh', this_base + '/write.sh', ['123'], '123'),
            ('sh', this_base + '/write.sh', ['123', '456'], '123456'),
        )

        for cmd, target, args, expected in cases:
            pykit3proc.start_process(cmd, target, os.environ, *args)
            time.sleep(0.1)
            self.assertEqual(expected, self._read_file(self.foo_fn))
