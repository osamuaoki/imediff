# Test suite for imediff and git-ime

This directory contains files to test imediff and git-ime.

## Test code used by dh_test and autopkgtest

* `test_unittest_all.py`
  * Run a set of test to see its diff logics are valid
    * `./_diff23.py` -- test with files (file_a, file_b file_c)
    * `./_imediff.py` -- test with imediff in this source.
    * `../src/imediff/diff3lib.py` -- doctest
    * `../src/imediff/lines2lib.py` -- doctest

## Test codes manually run as you write and update codes

* `./90_local_imediff_tests.sh`
  * Run a set of test to see its diff logics are valid
    * `./_diff23.py`  -- test with files (file_a, file_b file_c)
    * `./_imediff.py` -- test with imediff in this source.
  * A subset of the test run by unittest via `./test_unittest_all.py`
  * Python path is adjusted as: `export PYTHONPATH=../src`
* `./90_local_git_ime_tests.sh`
  * Run a set of test to see its git ime are valid
  * Use local shell code `../usr/bin/git-ime.in`
* `./00_local_imediff.sh`
  * Run the local python module code with user provided arguments
  * Effectively the same test run by unittest via `./test_unittest_all.py`
* `./00_local_git_ime.sh`
  * Run the local shell code `../usr/bin/git-ime` with user provided arguments
  * Path is adjusted as: `export PATH=../usr/bin/:$PATH`

These are meant to be executed in this directory.

## NOTE

For Debian package building, dh_auto_test isn't run from here.  It looks like a
copy of test/ directory as test and a copy of src/imediff directory as imediff
are created at .pybuild/cpython3_*.*/ where the current directory is moved to.

Notable thing is that when test/ directories are copied, symlinks are copied as files.
