#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test python codes

rm -f imediff.log z_imediff.conf.new

PYTHONPATH=$(pwd)/../src
PYTHONPATH=$(realpath $PYTHONPATH)
echo "I: Setting PYTHONPATH=$PYTHONPATH"
export PYTHONPATH

# ignore ~/.imediff
python3 _imediff.py -l -C z_imediff.conf.new -t
echo
for f in *.new; do
	g="${f%.new}.ref"
	echo " ==== COMPARE: $g vs. $f ==="
	if diff -u "$g" "$f"; then
		echo " -> = NO_DIFF: $g"
	else
		echo " -> ! DIFF: $g"
		EXITSTATUS=false
	fi
	echo
done
$EXITSTATUS
