#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:

"""
Script to test imediff initializing code
"""
import imediff.initialize_args
import imediff.initialize_confs
import imediff.config
import imediff.utils
import configparser
import os
import sys

print("\nI: _initialize start >>>", file=sys.stderr)
cwd_dir = os.getcwd()
print("I: cwd_dir     = '{}'".format(cwd_dir), file=sys.stderr)
print("I: test_file   = '{}' (active)".format(__file__), file=sys.stderr)
test_dir = os.path.dirname(os.path.abspath(__file__))
print("I: test_dir    = '{}' (active)".format(test_dir), file=sys.stderr)
if "PYTHONPATH" in os.environ:
    print("I: PYTHONPATH  = '{}'".format(os.environ["PYTHONPATH"]), file=sys.stderr)
else:
    print("I: PYTHONPATH  = <undefined>", file=sys.stderr)
print("I: _initialize end   <<<", file=sys.stderr)
# print("VERSION={}".format(imediff.version))
# print("PACKAGE={}".format(imediff.PACKAGE))
# print(">>> imediff >>>>>>> key -> value >>>>>>>>>>>>>>>>")
# for k, v in imediff.__dict__.items():
#    print(">>> '{}' -> '{}'".format(k, v))
##########################################################################
args = imediff.initialize_args.initialize_args()
print(">>> args >>>>>>> key -> value >>>>>>>>>>>>>>>>")
# for k, v in args.__dict__.items():
#    print(">>> args >>> '{}' -> '{}'".format(k, v))

##########################################################################
confs = imediff.initialize_confs.initialize_confs(args.conf)
print(">>> confs['section'] >>>>>>> 'key' = 'value' >>>>>>>>>>>>>>>>")
for section in confs.sections():
    for key, value in confs[section].items():
        print(">>> confs['{}'] >>> '{}' = '{}'".format(section, key, value))

##########################################################################
print(">>> confs_internal['section'] >>>>>>> 'key' = 'value' >>>>>>>>>>>>>>>>")
confs_internal = configparser.ConfigParser(inline_comment_prefixes=(";", "#"))
confs_internal.read_string(imediff.config.config_template)
for section in confs_internal.sections():
    for key, value in confs_internal[section].items():
        print(">>> confs['{}'] >>> '{}' = '{}'".format(section, key, value))

##########################################################################
list_a = imediff.utils.read_lines(args.file_a)
list_b = imediff.utils.read_lines(args.file_b)
list_c = imediff.utils.read_lines(args.file_c)
print(">>> list_a >>>>>>> key -> value >>>>>>>>>>>>>>>>")
for i, f in enumerate(list_a):
    print(">>> list_a[{}]='{}'".format(i, f[:-1]))
print(">>> list_b >>>>>>> key -> value >>>>>>>>>>>>>>>>")
for i, f in enumerate(list_b):
    print(">>> list_b[{}]='{}'".format(i, f[:-1]))
print(">>> list_c >>>>>>> key -> value >>>>>>>>>>>>>>>>")
for i, f in enumerate(list_c):
    print(">>> list_c[{}]='{}'".format(i, f[:-1]))
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
