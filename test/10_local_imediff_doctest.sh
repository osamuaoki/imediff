#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test python codes
#
# This is the same as test_unittest_all.py but easier to modify to identify issues from console
# This is not for unittest
#

PYTHONPATH=$(pwd)/../src
PYTHONPATH=$(realpath $PYTHONPATH)
echo "I: Setting PYTHONPATH=$PYTHONPATH"
export PYTHONPATH

EXITSTATUS=true

echo
# doctest
python3 ../src/imediff/diff3lib.py
echo "I: success for doctest on src/imediff/diff3lib.py"
echo
python3 ../src/imediff/lines2lib.py
echo "I: success for doctest on src/imediff/lines2lib.py"
echo
