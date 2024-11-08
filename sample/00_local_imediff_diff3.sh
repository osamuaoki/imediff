#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test python codes


PYTHONPATH=$(pwd)/../src
PYTHONPATH=$(realpath $PYTHONPATH)
echo "I: Setting PYTHONPATH=$PYTHONPATH"
export PYTHONPATH

# ignore ~/.imediff
python3 ../test/_imediff.py -C none -n -Mw file_a2 file_b2 file_c2 -o file_out_imediff
diff3 -m file_a2 file_b2 file_c2 > file_out_diff3

rm -f imediff.log
