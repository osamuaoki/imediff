#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

import argparse

# This allows different reporting style for TUI/CLI
pa = argparse.ArgumentParser(
    description="SIMPLE example",
    epilog="See README.md for more",
)
group = pa.add_mutually_exclusive_group()
group.add_argument(
    "-a", action="store_true", help="Start with all chunks to use file_a"
)
group.add_argument(
    "-b", action="store_true", help="Start with all chunks to use file_b"
)
group.add_argument(
    "-c",
    action="store_true",
    help="Start with all chunks to use file_c (only for diff3)",
)
pa.add_argument(
    "--rule-filter",
    "-r",
    action="store",
    default=2,
    help="Fuzzy match line filtering rule (0,1,2,3,10,11,12,13)",
)
args = pa.parse_args()

print("a={}, b={}, c={}".format(args.a, args.b, args.c))
print("rule-filter={}".format(args.rule_filter))
