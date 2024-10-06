#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:
"""
Script to test imediff.main module

Use as:

 $ python3 _imediff ...

"""
import os
import sys
import imediff.main
print("\nI: _imediff start >>>", file=sys.stderr)
cwd_dir = os.getcwd()
print("I: cwd_dir     = '{}'".format(cwd_dir), file=sys.stderr)
print("I: test_file   = '{}' (active)".format(__file__), file=sys.stderr)
test_dir = os.path.dirname(os.path.abspath(__file__))
print("I: test_dir    = '{}' (active)".format(test_dir), file=sys.stderr)
if "PYTHONPATH" in os.environ:
    print("I: PYTHONPATH  = '{}'".format(os.environ["PYTHONPATH"]), file=sys.stderr)
else:
    print("I: PYTHONPATH  = <undefined>", file=sys.stderr)
print("I: _imediff end   <<<", file=sys.stderr)
#
sys.exit(imediff.main.main())
