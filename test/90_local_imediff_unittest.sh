#!/bin/bash -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test python codes

rm -f imediff.log

PYTHONPATH=$(pwd)/../src
PYTHONPATH=$(realpath $PYTHONPATH)
echo "I: Setting PYTHONPATH=$PYTHONPATH"
export PYTHONPATH

python3 test_unittest_all.py -v
