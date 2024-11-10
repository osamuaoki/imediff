#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai:
"""
Test many aspect of imediff package via unittest.

  pybuild(1)
  https://docs.python.org/3/library/unittest.html#test-discovery
  In order to be compatible with test discovery, all of the test files must be
  modules or packages importable from the top-level directory of the project

  https://stackoverflow.com/questions/3295386/python-unittest-and-discovery
  The unittest filename needs to be test_*.py

To test the in-source-tree module, invoke this script in this directory as:

 $ export PYTHONPATH=$(pwd)/../src
 $ python3 test_unittest_all.py -v

To test the system installed module, invoke this script directly in this
directory as:

 $ python3 test_unittest_all.py -v

Current diff2 uses Python standard library difflib which uses a variant of
longest contiguous matching sub-sequence algorithm by Ratcliff and Obershelp
developed in the late 1980's.  If I update this imediff program to use more
modern algorithm, this test may yield slightly different result.
"""
import unittest
import subprocess
import os
import os.path
import imediff.diff3lib

# Deb package build dh_test
#
# test/ and imediff/ are copied to ../build/ directory and cwd is set to there
# test_dir = cwd_dir + "/test"
# cwd_dir + "/imediff" -- exist
# PYTHONPATH = 'PROJECT_ROOT/debian/tmp/usr/lib/python3.11/dist-packages:PROJECT_ROOT/.pybuild/cpython3_3.11/build'
# doctest_dir = "../src/imediff/"

### TEST installed system module
# Deb autopkgtest
#
# The cwd of each test is guaranteed to be the root of the source package,
# which will have been unpacked but not built. However note that the tests must
# test the installed version of the package, as opposed to programs or any
# other file from the built tree. Tests may not modify the source tree (and may
# not have write access to it).
# test_dir = cwd_dir + "/test"
# cwd_dir + "/debian" -- exist
# cwd_dir + "/src" -- exist
# cwd_dir + "/src/imediff" -- exist
# doctest_dir = "imediff/"

# Direct invocation from test_dir
# test_dir == cwd_dir
# doctest_dir = "imediff/"

# Direct invocation from PROJECT_ROOT
# test_dir = cwd_dir + "/test"
# cwd_dir + "/debian" -- exist
# cwd_dir + "/src" -- exist
# cwd_dir + "/src/imediff" -- exist
# doctest_dir = "imediff/"

##### Build time
# This is run from copied files with PYTHONPATH set
# I: PYTHONPATH = 'PROJECT_ROOT/debian/tmp/usr/lib/python3.11/dist-packages:PROJECT_ROOT/.pybuild/cpython3_3.11/build'
##### path to test directory
####print("I: test_dir ='{}'".format(test_dir))
##### I: test_dir ='PROJECT_ROOT/.pybuild/cpython3_3.11/build/test'
####
##### path to current working directory
####print("I: cwd_dir  ='{}'".format(cwd_dir))
##### I: cwd_dir  ='PROJECT_ROOT/.pybuild/cpython3_3.11/build'
##### <<< This is where imediff module is copied and located
####
##### --- subprocess.run(["ls", "-laR"])

cwd_dir = os.getcwd()
print("I: cwd_dir     = '{}'".format(cwd_dir))
print("I: test_file   = '{}' (active)".format(__file__))
test_dir = os.path.dirname(os.path.abspath(__file__))
print("I: test_dir    = '{}' (active)".format(test_dir))
base_dir = os.path.dirname(test_dir)
print("I: base_dir    = '{}'".format(base_dir))
if os.path.isdir(base_dir + "/src"):
    print("I: test in the original source tree invoked")
    doctest_dir = base_dir + "/src/imediff"
elif os.path.isdir(base_dir + "/imediff"):
    print("I: test in the copied source tree in Debian pybuild invoked")
    doctest_dir = base_dir + "/imediff"
else:
    print("I: test in an unknown environment invoked")
    exit(1)
print("I: doctest_dir = '{}'".format(doctest_dir))
if "PYTHONPATH" in os.environ:
    print("I: PYTHONPATH  = '{}'".format(os.environ["PYTHONPATH"]))
else:
    print("I: PYTHONPATH  = <undefined>")


class TestImediff(unittest.TestCase):
    a = "a12b345c6789d"
    b = "123456789"
    c = "a1234b567c89d"

    def test_diff3lib_abc(self):
        a = "a12b345c6789d"
        b = "123456789"
        c = "a1234b567c89d"
        self.assertEqual(
            imediff.diff3lib.SequenceMatcher3(a, b, c, 0, None, True).get_opcodes(),
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

    def test_lines2lib_doctest(self):
        result = subprocess.call(
            "python3 " + doctest_dir + "/lines2lib.py",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_diff3lib_doctest(self):
        result = subprocess.call(
            "python3 " + doctest_dir + "/diff3lib.py",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_diff23(self):
        result = subprocess.call(
            "cd " + test_dir + ";python3 _diff23.py >z_diff23.out", shell=True
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_diff23.out z_diff23.ref >/dev/null", shell=True
        )
        self.assertEqual(result, 0)
        return

    def test_imediff2(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -C none --macro=w -n file_a file_b -o z_imediff2.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff2.out z_imediff2.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff2_a(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -a -C none --macro=w -n file_a file_b -o z_imediff2_a.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff2_a.out z_imediff2_a.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff2_b(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -b -C none --macro=w -n file_a file_b -o z_imediff2_b.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff2_b.out z_imediff2_b.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff2_d(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -d -C none --macro=w -n file_a file_b -o z_imediff2_d.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff2_d.out z_imediff2_d.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff2_f(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -f -C none --macro=w -n file_a file_b -o z_imediff2_f.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff2_f.out z_imediff2_f.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff3(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -C none --macro=w -n file_a file_b file_c -o z_imediff3.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff3.out z_imediff3.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff3_a(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -a -C none --macro=w -n file_a file_b file_c -o z_imediff3_a.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff3_a.out z_imediff3_a.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff3_b(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -b -C none --macro=w -n file_a file_b file_c -o z_imediff3_b.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff3_b.out z_imediff3_b.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff3_c(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -c -C none --macro=w -n file_a file_b file_c -o z_imediff3_c.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff3_c.out z_imediff3_c.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff3_d(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -d -C none --macro=w -n file_a file_b file_c -o z_imediff3_d.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff3_d.out z_imediff3_d.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff3_f(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -f -C none --macro=w -n file_a file_b file_c -o z_imediff3_f.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff3_f.out z_imediff3_f.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def test_imediff3_g(self):
        result = subprocess.call(
            "cd "
            + test_dir
            + ";python3 _imediff.py -g -C none --macro=w -n file_a file_b file_c -o z_imediff3_g.out",
            shell=True,
        )
        result = subprocess.call(
            "cd " + test_dir + ";diff z_imediff3_g.out z_imediff3_g.ref >/dev/null",
            shell=True,
        )
        self.assertEqual(result, 0)
        return

    def tearDown(self):
        _ = subprocess.call("cd " + test_dir + ";rm -f z_*.out", shell=True)
        return


if __name__ == "__main__":
    unittest.main()
