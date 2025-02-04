#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
#
# script for uploading wheel package to official pypi.org
#
git reset --hard HEAD
git clean -dfx
python3 -m build
echo -n "I: starting upload environment at pwd = "
pwd
python3 -m venv venv
. venv/bin/activate
python3 -m pip install --upgrade twine
python3 -m twine upload dist/*
echo "I: check upload at https://pypi.org/project/imediff"
echo "I: exit test environment"
