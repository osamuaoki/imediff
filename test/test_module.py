#!/usr/bin/python3
# vim:se tw=0 sts=4 ts=4 et ai:

"""
Simple configuration reader
"""
import sys
# force PYTHONPATH for testing
sys.path.insert(0, '..')
import imediff
import configparser

print("VERSION={}".format(imediff.VERSION))
print("PACKAGE={}".format(imediff.PACKAGE))
print(">>> imediff >>>>>>> key -> value >>>>>>>>>>>>>>>>")
for k, v in imediff.__dict__.items():
    print(">>> '{}' -> '{}'".format(k, v))
##########################################################################
args = imediff.initialize_args()
print(">>> args >>>>>>> key -> value >>>>>>>>>>>>>>>>")
for k, v in args.__dict__.items():
    print(">>> args >>> '{}' -> '{}'".format(k, v))

##########################################################################
confs = imediff.initialize_confs(args.conf)
print(">>> confs['section'] >>>>>>> 'key' = 'value' >>>>>>>>>>>>>>>>")
for section in confs.sections():
    for key, value in confs[section].items():
        print(">>> confs['{}'] >>> '{}' = '{}'".format(section, key, value))

##########################################################################
print(">>> confs_internal['section'] >>>>>>> 'key' = 'value' >>>>>>>>>>>>>>>>")
confs_internal = configparser.ConfigParser(inline_comment_prefixes=(';','#'))
confs_internal.read_string(imediff.config_template)
for section in confs_internal.sections():
    for key, value in confs_internal[section].items():
        print(">>> confs['{}'] >>> '{}' = '{}'".format(section, key, value))

##########################################################################
list_a, list_b, list_c = imediff.read_files(args)
print(">>> list_a >>>>>>> key -> value >>>>>>>>>>>>>>>>")
for i, f in enumerate(list_a):
    print (">>> list_a[{}]='{}'".format(i,f))
print(">>> list_b >>>>>>> key -> value >>>>>>>>>>>>>>>>")
for i, f in enumerate(list_b):
    print (">>> list_b[{}]='{}'".format(i,f))
print(">>> list_c >>>>>>> key -> value >>>>>>>>>>>>>>>>")
for i, f in enumerate(list_c):
    print (">>> list_c[{}]='{}'".format(i,f))
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
sys.exit(0)
