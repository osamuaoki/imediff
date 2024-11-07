#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :
fp = open("report.py", "r")
line_list = fp.readlines()
#
# list of string containing \n at the end of each item
# for line in range(len(line_list)):
for line in line_list:
    print("line='{}'".format(line))

bigline = "".join(line_list)
print("================================================")
print(bigline)
print("================================================")

FOOLINE = "a\nb\nc\n"
print(FOOLINE.split())
print("================================================")
print(FOOLINE.splitlines(keepends=True))
