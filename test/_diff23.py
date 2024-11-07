#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai:
"""
Script to test diff2 and diff3 logic

The diff3 logic is build on top of diff2 logic.

Current diff2 uses Python standard library difflib which uses a variant of
longest contiguous matching subsequence algorithm by Ratcliff and Obershelp
developed in the late 1980's.  If I update this imediff program to use more
modern algorithm, this test may yield slightly different result in some
corner cases.
"""

import os
import sys
import difflib
import imediff.diff3lib


def diff23(a, b, c, name=""):
    print("# Test type: " + name)
    print("  a='%s' -> %i" % (a, len(a)))
    print("  b='%s' -> %i" % (b, len(b)))
    print("  c='%s' -> %i" % (c, len(c)))
    sa = difflib.SequenceMatcher(None, a, b)
    print("$ diff2 A B")
    for tag, i1, i2, j1, j2 in sa.get_opcodes():
        print(
            (
                "  %s     a[%d:%d] (%s) / b[%d:%d] (%s)"
                % (tag, i1, i2, a[i1:i2], j1, j2, b[j1:j2])
            )
        )
    print("$ diff2 C B")
    sc = difflib.SequenceMatcher(None, c, b)
    for tag, i1, i2, j1, j2 in sc.get_opcodes():
        print(
            (
                "  %s     c[%d:%d] (%s) / b[%d:%d] (%s)"
                % (tag, i1, i2, c[i1:i2], j1, j2, b[j1:j2])
            )
        )
    s = imediff.diff3lib.SequenceMatcher3(a, b, c, 0, None, True)
    print("$ diff3 A B C")
    for tag, i1, i2, j1, j2, k1, k2 in s.get_opcodes():
        print(
            (
                "  %s     a[%d:%d] (%s) / b[%d:%d] (%s) / c[%d:%d] (%s)"
                % (tag, i1, i2, a[i1:i2], j1, j2, b[j1:j2], k1, k2, c[k1:k2])
            )
        )
    print("===========================================================")
    return


print("\nI: _diff23 start >>>", file=sys.stderr)
cwd_dir = os.getcwd()
print("I: cwd_dir     = '{}'".format(cwd_dir), file=sys.stderr)
print("I: test_file   = '{}' (active)".format(__file__), file=sys.stderr)
test_dir = os.path.dirname(os.path.abspath(__file__))
print("I: test_dir    = '{}' (active)".format(test_dir), file=sys.stderr)
if "PYTHONPATH" in os.environ:
    print("I: PYTHONPATH  = '{}'".format(os.environ["PYTHONPATH"]), file=sys.stderr)
else:
    print("I: PYTHONPATH  = <undefined>", file=sys.stderr)
print("I: _diff23 end   <<<", file=sys.stderr)

diff23("12345", "12345", "12345", "same")

diff23("a12345z", "1245", "1245", "add a side")

diff23("a12345z", "1245", "a12345z", "add same")

diff23("1245", "1245", "a12345z", "add c side")

diff23("24", "12345", "12345", "delete a side")

diff23("24", "12345", "24", "delete same")

diff23("12345", "12345", "24", "delete c side")

diff23("a2b4c", "12345", "x2y4z", "conflict both ends")

diff23("1a2b4c", "12345", "x2y45z", "conflict skewed")
