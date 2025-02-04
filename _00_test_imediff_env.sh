#!/bin/bash -e
# vim: set sw=2 et sw=2 sts=2:
#
# test script used before uploading wheel package to pypi.org
#
type imediff
type git-ime
git reset --hard HEAD
git clean -dfx
python3 -m build
echo -n "I: starting test environment at pwd = "
pwd
python3 -m venv venv
. venv/bin/activate
echo "I: starting test environment"
pip install dist/imediff-*-any.whl
imediff_install
type imediff
type git-ime
echo "I: imediff installed with helper script"
imediff test/file_a test/file_b test/file_c -o test/file_out
echo "I: starting subshell to continue.  Type ^D to exit"
bash -i
echo "I: exit test environment"
