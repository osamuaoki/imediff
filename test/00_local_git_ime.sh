#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test git-ime codes
# Use installed imediff (deb or wheel)
#
# working toss-away repo location
THISFILE="$(realpath $0)"
THISDIR="${THISFILE%/*}"
NEWPATH="$(realpath ${THISDIR}/../usr/bin)"
GIT_IME="$(realpath $THISDIR/../usr/bin/git-ime.in)"
PATH="$THISDIR/../usr/bin:$PATH"
# echo GIT_IME
# echo $GIT_IME
# echo THISDIR
# echo $THISDIR
# echo $NEWPATH
# echo $PATH
$GIT_IME "$@"
echo "===== SUCCESS ALL ====="
