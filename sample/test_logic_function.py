#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

import sys
import termios


def getch():
    old_settings = termios.tcgetattr(0)
    new_settings = old_settings[:]
    # Enable canonical mode. See termios(3)
    new_settings[3] &= ~termios.ICANON
    try:
        # Change attributes immediately.
        termios.tcsetattr(0, termios.TCSANOW, new_settings)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(0, termios.TCSANOW, old_settings)
    return ch


def yn0():
    print("\n0: enter 'y' or 'n': ", end="")
    ch = getch()
    if ch == "y":
        r = True
    else:
        r = False
    return r


def yn1():
    print("\n1: enter 'y' or 'n': ", end="")
    ch = getch()
    r = ch == "y"
    return r


# NO `return ch == "y"` like C

if yn0():
    print("\nTRUE\n")
else:
    print("\nFALSE\n")

if yn1():
    print("\nTRUE\n")
else:
    print("\nFALSE\n")
