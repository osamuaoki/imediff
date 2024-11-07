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
# doctest for diff23.py
python3 _diff23.py >z_diff23.new
for f in *.new; do
	g="${f%.new}.ref"
	echo " ==== COMPARE: $g vs. $f ==="
	if diff -u "$g" "$f"; then
		echo " -> = NO_DIFF: $g"
	else
		echo " -> ! DIFF: $g"
		EXITSTATUS=false
		$CONTINUE_TEST
	fi
	echo
done
$EXITSTATUS
