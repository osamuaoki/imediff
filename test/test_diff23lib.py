#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai:
"""
Test many aspect of imediff package via unittest.

To test the in-source-tree module, invoke this script from setup.py in the
root of the source tree as:

 $ python3 setup.py test


To test the installed module, invoke this script directly as:

 $ python3 test_diff23lib.py -v

Current diff2 uses Python standard library difflib which uses a variant of
longest contiguous matching subsequence algorithm by Ratcliff and Obershelp
developed in the late 1980's.  If I update this imediff program to use more
modern algorithm, this test may yield slightly different result.
"""
import unittest
import subprocess
import os
import os.path
import imediff.diff2lib
import imediff.diff3lib

# path to test directory
pwd = os.path.dirname(os.path.abspath(__file__))


class TestImediff(unittest.TestCase):

    a = "a12b345c6789d"
    b = "123456789"
    c = "a1234b567c89d"

    def test_diff2lib_ab(self):
        a = "a12b345c6789d"
        b = "123456789"
        self.assertEqual(
            imediff.diff2lib.SequenceMatcher2(None, a, b).get_chunks(),
            [
                ("N", 0, 1, 0, 0),
                ("E", 1, 3, 0, 2),
                ("N", 3, 4, 2, 2),
                ("E", 4, 7, 2, 5),
                ("N", 7, 8, 5, 5),
                ("E", 8, 12, 5, 9),
                ("N", 12, 13, 9, 9),
            ],
        )
        return

    def test_diff3lib_abc(self):
        a = "a12b345c6789d"
        b = "123456789"
        c = "a1234b567c89d"
        self.assertEqual(
            imediff.diff3lib.SequenceMatcher3(None, a, b, c).get_chunks(),
            [
                ("e", 0, 1, 0, 0, 0, 1),
                ("E", 1, 3, 0, 2, 1, 3),
                ("A", 3, 4, 2, 2, 3, 3),
                ("E", 4, 6, 2, 4, 3, 5),
                ("C", 6, 6, 4, 4, 5, 6),
                ("E", 6, 7, 4, 5, 6, 7),
                ("A", 7, 8, 5, 5, 7, 7),
                ("E", 8, 10, 5, 7, 7, 9),
                ("C", 10, 10, 7, 7, 9, 10),
                ("E", 10, 12, 7, 9, 10, 12),
                ("e", 12, 13, 9, 9, 12, 13),
            ],
        )
        return

    def test_diff2lib_doctest(self):
        result = subprocess.call(
            "cd " + pwd + ";PYTHONPATH=.. ../imediff/diff2lib.py", shell=True
        )
        self.assertEqual(result, 0)
        return

    def test_diff3lib_doctest(self):
        result = subprocess.call(
            "cd " + pwd + ";PYTHONPATH=.. ../imediff/diff3lib.py", shell=True
        )
        self.assertEqual(result, 0)
        return

    def test_diff23(self):
        result = subprocess.call(
            "cd " + pwd + ";./_diff23.py >z_diff23.out", shell=True
        )
        result = subprocess.call(
            "cd " + pwd + ";diff z_diff23.out z_diff23.ref >/dev/null", shell=True
        )
        self.assertEqual(result, 0)
        return

    def test_imediff2(self):
        result = subprocess.call(
            "cd " + pwd + ";./_imediff.py  -C BOGUS -n file_a file_b -o z_imediff2.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + pwd + ";diff z_imediff2.out z_imediff2.ref >/dev/null", shell=True
        )
        self.assertEqual(result, 0)
        return

    def test_imediff3(self):
        result = subprocess.call(
            "cd "
            + pwd
            + ";./_imediff.py -C BOGUS -n file_a file_b file_c -o z_imediff3.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + pwd + ";diff z_imediff3.out z_imediff3.ref >/dev/null", shell=True
        )
        self.assertEqual(result, 0)
        return

    def test_initialize(self):
        result = subprocess.call(
            "cd " + pwd + ";./_initialize.py  > z_initialize.out", shell=True
        )
        result = subprocess.call(
            "cd " + pwd + ";diff z_initialize.out z_initialize.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_macrotrans(self):
        result = subprocess.call(
            "cd "
            + pwd
            + ";./_macrotrans.py -C alternative_imediff.conf -n file_a file_b file_c > z_macrotrans.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + pwd + ";diff z_macrotrans.out z_macrotrans.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def tearDown(self):
        result = subprocess.call("cd " + pwd + ";rm -f z_*.out", shell=True)
        return


if __name__ == "__main__":
    unittest.main()
