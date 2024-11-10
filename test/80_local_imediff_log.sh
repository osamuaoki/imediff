#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test python codes
# This is redundant so this is not part of standard build check
# See 00_local_imediff_cfgs.sh
#
rm -f imediff.log

PYTHONPATH=$(pwd)/../src
PYTHONPATH=$(realpath $PYTHONPATH)
echo "I: Setting PYTHONPATH=$PYTHONPATH"
export PYTHONPATH

# ignore ~/.imediff
python3 _imediff.py -C none -D -n --macro=q
sed -e '/external editor/,$d' imediff.log >z_imediff-log.new


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
