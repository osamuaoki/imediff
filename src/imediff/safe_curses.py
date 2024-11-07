#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
curses_pc: safe curses wrapper

Copyright (C) 2018--2024 Osamu Aoki <osamu@debian.org>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the Free
Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.
"""

import logging
import curses

logger = logging.getLogger(__name__)


def get_keycode(keyname):
    if len(keyname) == 1:
        keycode = ord(keyname)
    elif keyname == "TAB":
        keycode = 9
    elif keyname == "BTAB":
        keycode = curses.KEY_BTAB
    elif keyname == "ENTER":
        keycode = 10
    elif keyname == "ESCAPE":
        keycode = 27
    elif keyname == "SPACE":
        keycode = ord(" ")
    elif keyname == "HASH":
        keycode = ord("#")
    elif keyname == "COLON":
        keycode = ord(":")
    elif keyname == "EQUAL":
        keycode = ord("=")
    elif keyname == "LBRACKET":
        keycode = ord("[")
    elif keyname == "\\":
        keycode = ord("=")
    elif keyname == "BACKSLASH":
        keycode = ord("]")
    elif keyname == "RBRACKET":
        keycode = ord("=")
    elif keyname == "UP":
        keycode = curses.KEY_UP
    elif keyname == "DOWN":
        keycode = curses.KEY_DOWN
    elif keyname == "LEFT":
        keycode = curses.KEY_LEFT
    elif keyname == "RIGHT":
        keycode = curses.KEY_RIGHT
    elif keyname == "INSERT":
        keycode = curses.KEY_IC
    elif keyname == "DELETE":
        keycode = curses.KEY_DC
    elif keyname == "HOME":
        keycode = curses.KEY_HOME
    elif keyname == "END":
        keycode = curses.KEY_END
    elif keyname == "PAGEUP":
        keycode = curses.KEY_PPAGE
    elif keyname == "PAGEDOWN":
        keycode = curses.KEY_BACKSPACE
    elif keyname == "BACKSPACE":
        keycode = curses.KEY_NPAGE
    elif keyname == "F1":
        keycode = curses.KEY_F1
    elif keyname == "F2":
        keycode = curses.KEY_F2
    elif keyname == "F3":
        keycode = curses.KEY_F3
    elif keyname == "F4":
        keycode = curses.KEY_F4
    elif keyname == "F5":
        keycode = curses.KEY_F5
    elif keyname == "F6":
        keycode = curses.KEY_F6
    elif keyname == "F7":
        keycode = curses.KEY_F7
    elif keyname == "F8":
        keycode = curses.KEY_F8
    elif keyname == "F9":
        keycode = curses.KEY_F9
    elif keyname == "F10":
        keycode = curses.KEY_F10
    elif keyname == "F11":
        keycode = curses.KEY_F11
    elif keyname == "F12":
        keycode = curses.KEY_F12
    else:
        keycode = ord(" ")
    return keycode


def get_keyname(keycode):
    if keycode == 9:
        keyname = "TAB"
    elif keycode == curses.KEY_BTAB:
        keyname = "BTAB"
    elif keycode == 10:
        keyname = "ENTER"
    elif keycode == 27:
        keyname = "ESCAPE"
    elif keycode == ord(" "):
        keyname = "SPACE"
    elif keycode == ord("#"):
        keyname = "HASH"
    elif keycode == ord("%"):
        keyname = "PERCENT"
    elif keycode == ord(":"):
        keyname = "COLON"
    elif keycode == ord("="):
        keyname = "EQUAL"
    elif keycode == ord("["):
        keyname = "LBRACKET"
    elif keycode == ord("\\"):
        keyname = "BACKSLASH"
    elif keycode == ord("]"):
        keyname = "RBRACKET"
    elif keycode == curses.KEY_UP:
        keyname = "UP"
    elif keycode == curses.KEY_DOWN:
        keyname = "DOWN"
    elif keycode == curses.KEY_LEFT:
        keyname = "LEFT"
    elif keycode == curses.KEY_RIGHT:
        keyname = "RIGHT"
    elif keycode == curses.KEY_IC:
        keyname = "INSERT"
    elif keycode == curses.KEY_DC:
        keyname = "DELETE"
    elif keycode == curses.KEY_HOME:
        keyname = "HOME"
    elif keycode == curses.KEY_END:
        keyname = "END"
    elif keycode == curses.KEY_PPAGE:
        keyname = "PAGEUP"
    elif keycode == curses.KEY_NPAGE:
        keyname = "PAGEDOWN"
    elif keycode == curses.KEY_BACKSPACE:
        keyname = "BACKSPACE"
    elif keycode == curses.KEY_F1:
        keyname = "F1"
    elif keycode == curses.KEY_F2:
        keyname = "F2"
    elif keycode == curses.KEY_F3:
        keyname = "F3"
    elif keycode == curses.KEY_F4:
        keyname = "F4"
    elif keycode == curses.KEY_F5:
        keyname = "F5"
    elif keycode == curses.KEY_F6:
        keyname = "F6"
    elif keycode == curses.KEY_F7:
        keyname = "F7"
    elif keycode == curses.KEY_F8:
        keyname = "F8"
    elif keycode == curses.KEY_F9:
        keyname = "F9"
    elif keycode == curses.KEY_F10:
        keyname = "F10"
    elif keycode == curses.KEY_F11:
        keyname = "F11"
    elif keycode == curses.KEY_F12:
        keyname = "F12"
    elif keycode < ord(" "):
        logging.warning(
            "W: suspicous keycode below ASCII characters (control code?): {}".format(
                keycode
            )
        )
        keyname = "q"
    elif keycode >= 127:
        logging.warning(
            "W: suspicous keycode above ASCII characters (function keys?): {}".format(
                keycode
            )
        )
        keyname = "q"
    else:
        keyname = chr(keycode)
    return keyname


####################################################################
def display_content(win, row, col, content, clrtoeol=False):
    # win:   parent window (curses.stdscr for full screen)
    # row:   row to put starting cursor in parent window
    #        if negative or None, continue to use current cursor position
    # col:   col to put starting cursor in parent window
    #        if negative or None, continue to use current cursor position
    # content: [(line, i_b, i_e, attrib), ...]
    #     line:  input line (to be sliced)
    #     i_b:   input line begin point index (=)
    #     i_e:   input line end point index (<)
    #     attrib: curses attribute
    #
    # rationale behind not-doing line[i_b, i_e] on the calling side
    #   Python does slice-by-copy, meaning every time you slice (except for
    #   very trivial slices, such as a[:]), it copies all of the data into
    #   a new string object.
    # https://stackoverflow.com/questions/5722006/does-python-do-slice-by-reference-on-strings
    #
    win_row_max, win_col_max = win.getmaxyx()
    # win.leaveok(False)
    # set starting cursor position robustly
    if row is None or row < 0:
        try:
            row, _ = win.getyx()
        except curses.error as _:
            logger.warning("win.getyx() caused error")
            row = 0
    if col is None or col < 0:
        try:
            _, col = win.getyx()
        except curses.error as _:
            logger.warning("win.getyx() caused error")
            col = 0
    if row < win_row_max:
        try:
            win.move(row, 0)
        except curses.error as _:
            pass
        # single row window
        win1row = win.derwin(1, win_col_max, row, 0)
        if col is not None:
            try:
                win1row.move(0, col)
            except curses.error as _:
                pass
        for line, i_b, i_e, attrib in content:
            # use always positive reasonable index range to slice
            # line[i_b:i_e]
            if i_b is None:
                i_b = 0
            if i_b >= len(line):
                i_b = 0
                i_e = 0
            if i_e is None or i_e >= len(line):
                i_e = len(line)
            else:
                i_e = max(0, min(i_e, i_b + win_col_max, len(line)))
            try:
                win1row.addstr(line[i_b:i_e], attrib)
            except curses.error as _:
                pass
        try:
            _, col = win1row.getyx()
        except curses.error as _:
            col = 0
        if clrtoeol:
            win1row.clrtoeol()
        try:
            win.move(row, col)
        except curses.error as _:
            pass
    else:
        # not in writable cursor position
        pass


def test_key_input(stdscr):
    curses.start_color()
    stdscr.clear()
    while True:
        content0 = [
            (
                "Please type key for number:",
                0,
                None,
                curses.color_pair(0) | curses.A_BOLD,
            )
        ]
        display_content(stdscr, 0, 0, content0, clrtoeol=True)
        stdscr.refresh()
        code = stdscr.getch()
        content1 = [
            ("code={}".format(code), 0, None, curses.color_pair(0) | curses.A_REVERSE)
        ]
        display_content(stdscr, 1, 0, content1, clrtoeol=True)
        stdscr.refresh()
        content2 = [
            (
                "Please type key for string:",
                0,
                None,
                curses.color_pair(0) | curses.A_BOLD,
            )
        ]
        display_content(stdscr, 2, 0, content2, clrtoeol=True)
        stdscr.refresh()
        key = stdscr.getkey()
        content3 = [
            ("key='{}'".format(key), 0, None, curses.color_pair(0) | curses.A_REVERSE)
        ]
        display_content(stdscr, 3, 0, content3, clrtoeol=True)
        stdscr.refresh()
        content4 = [
            (
                "Please type key for PC keyname:",
                0,
                None,
                curses.color_pair(0) | curses.A_BOLD,
            )
        ]
        display_content(stdscr, 4, 0, content4, clrtoeol=True)
        stdscr.refresh()
        code = stdscr.getch()
        content5 = [
            # ("PC keyname={}".format(code), 0, None, curses.color_pair(0)|curses.A_REVERSE)
            (
                "PC keyname={}".format(get_keyname(code)),
                0,
                None,
                curses.color_pair(0) | curses.A_REVERSE,
            )
        ]
        display_content(stdscr, 5, 0, content5, clrtoeol=True)
        stdscr.refresh()
        content9 = [
            (
                "Type any key to start again, 'q' to quit. escape_delay={}".format(
                    curses.get_escdelay()
                ),
                0,
                None,
                curses.color_pair(0) | curses.A_REVERSE,
            )
        ]
        display_content(stdscr, 9, 0, content9, clrtoeol=True)
        code = stdscr.getch()
        stdscr.refresh()
        if code == ord("q"):
            break
    return


if __name__ == "__main__":
    import sys

    # stdscr = curses.initscr()
    curses.wrapper(test_key_input)
    sys.exit(0)
