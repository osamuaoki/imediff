#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:
"""
Script to test imediff module in place.

Use as:

 $ ./test_imediff ...

"""
import sys

# Force to use in source modules over system installed ones
sys.path.insert(0, "..")

import imediff

imediff.main()
