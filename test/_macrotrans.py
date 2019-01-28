#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:
"""
Script to test imediff macro key translation in place.
"""
import sys

# Force to use in source modules over system installed ones
sys.path.insert(0, "..")

import imediff

args = imediff.initialize_args()
confs = imediff.initialize_confs(args.conf)
if args.diff_mode == 0 or args.diff_mode is None:
    args.diff_mode = 2
list_a = ["a", "b", "c", "d", "e", "f"]
list_b = ["a", "b", "c", "d", "e", "f"]
list_c = ["a", "b", "c", "d", "e", "f"]
macro = "".join([chr(i) for i in range(ord("a"), ord("z"))])
macro += "".join([chr(i) for i in range(ord("A"), ord("Z"))])
args.macro = macro  # override
args.edit_cmd = "DUMMY_EDITOR"
instance = imediff.TextData(list_a, list_b, list_c, args, confs)
for c in macro:
    k = instance.getch_translated()
    print("MACRO:{} --> TranslatedKey={}".format(c, chr(k)))
sys.exit(0)
