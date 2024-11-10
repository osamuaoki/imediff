#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test git-ime codes
# Use installed imediff (deb or wheel)
#
# working toss-away repo location
THISFILE="$(realpath $0)"
THISDIR="${THISFILE%/*}"
REPO_DIR="${THISDIR}/repo"

set -x
rm -f *.new *.out
rm -rf "$REPO_DIR"
rm -f imediff.log
echo "===== CLEAN ALL ====="
