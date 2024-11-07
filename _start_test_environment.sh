#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
git reset --hard HEAD
git clean -dfx
python3 -m build
echo -n "I: starting test environment at pwd = "
pwd
python3 -m venv venv
. venv/bin/activate
pip install dist/imediff-*-any.whl
imediff_install
echo "I: finish istarting test environment"
echo "I: ... type ^C to exit test environment"
#bash -i
imediff -D test/file_al test/file_bl test/file_cl -o test/file_outl
#imediff test/file_a test/file_b -o test/file_out
echo "I: ^C typed. exit test environment"
#rm -rf dist
#rm -rf venv
echo "I: exit test environment"
