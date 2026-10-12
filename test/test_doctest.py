import doctest
import unittest

import k3proc


class TestDoctest(unittest.TestCase):
    def test_doctest(self):
        # pytest does not call the unittest load_tests hook, so a test method runs the examples.
        result = doctest.testmod(k3proc)
        self.assertEqual(doctest.TestResults(failed=0, attempted=2), result)
