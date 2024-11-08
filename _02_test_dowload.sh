#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
type imediff
type git-ime
git reset --hard HEAD
git clean -dfx
echo -n "I: starting test download environment at pwd = "
pwd
python3 -m venv venv
. venv/bin/activate
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps imediff
type imediff
type git-ime
echo "I: starting subshell to continue.  Type ^D to exit"
bash -i
echo "I: exit test environment"
