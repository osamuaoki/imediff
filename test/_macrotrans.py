#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:
"""
Script to test imediff macro key translation
"""
import imediff.initialize_args
import imediff.initialize_confs
import imediff.cli
import os
import sys

print("\nI: _microtrans start >>>", file=sys.stderr)
cwd_dir = os.getcwd()
print("I: cwd_dir     = '{}'".format(cwd_dir), file=sys.stderr)
print("I: test_file   = '{}' (active)".format(__file__), file=sys.stderr)
test_dir = os.path.dirname(os.path.abspath(__file__))
print("I: test_dir    = '{}' (active)".format(test_dir), file=sys.stderr)
if "PYTHONPATH" in os.environ:
    print("I: PYTHONPATH  = '{}'".format(os.environ["PYTHONPATH"]), file=sys.stderr)
else:
    print("I: PYTHONPATH  = <undefined>", file=sys.stderr)
print("I: _microtrans end   <<<", file=sys.stderr)

args = imediff.initialize_args.initialize_args()
confs = imediff.initialize_confs.initialize_confs(args.conf)
if args.diff_mode == 0 or args.diff_mode is None:
    args.diff_mode = 2
list_a = ["a", "b", "c", "d", "e", "f"]
list_b = ["a", "b", "c", "d", "e", "f"]
list_c = ["a", "b", "c", "d", "e", "f"]
macro = "".join([chr(i) for i in range(ord("a"), ord("z"))])
macro += "".join([chr(i) for i in range(ord("A"), ord("Z"))])
args.macro = macro  # override
args.edit_cmd = "DUMMY_EDITOR"
instance = imediff.cli.TextData(list_a, list_b, list_c, args, confs)
for c in macro:
    k = instance.getch_translated()
    print("MACRO:{} --> TranslatedKey={}".format(c, chr(k)))
