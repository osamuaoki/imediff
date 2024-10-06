#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
IMEDIFF - Interactive Merge Editor for DIFF2 and DIFF3
          Curses based single-pane fullscreen interactive tool
          and CLI based non-interactive tool with --macro

Copyright (C) 2003, 2004 Jarno Elonen <elonen@iki.fi>
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
import errno
import io
import sys
import traceback
import curses
import unicodedata

# Explicit list needed for "_"
__all__ = ["_", "console_width", "logger", "read_lines", "error_preexit", "write_file"]

# Utility functions

# gettext for i18n (commented out since gettext is not used)
# gettext.bindtextdomain("imediff")
# gettext.textdomain("imediff")
# _ = gettext.gettext


# NOOP version of gettext: _ = lambda x : x
def _(x):
    return x


# Console width with Zenkaku=2, Hankaku=1 (Hankaku=ASCII etc.)
# Latin-1, CJK focus simplification applied.
# (For Arabic, Hebrew etc., we need some refinement)
def console_width(text):
    width = 0
    for c in text:
        if c == "\t":  # TAB = 8
            width += 8
        elif unicodedata.east_asian_width(c) in "FWA":  # Zenkaku
            width += 2
        else:
            width += 1
    return width


# logger
logger = logging.getLogger(__name__)


# file read
def read_lines(filename):
    logger.debug("read_lines: filename = '{}'".format(filename))
    if filename is None or filename == "":
        lines = []
    else:
        try:
            with open(filename, buffering=io.DEFAULT_BUFFER_SIZE) as fp:
                lines = fp.readlines()  # read into list
        except IOError as e:
            (error, message) = e.args
            if error == errno.ENOENT:
                lines = []
            else:
                error_preexit("Could not read '{}': {}\n".format(filename, message))
                sys.exit(2)
        except:
            error_preexit(
                "read_lines: Unexpected error: {} {}".format(
                    sys.exc_info()[0], sys.exc_info()[1]
                )
            )
            sys.exit(2)
    return lines


# error exit
def error_preexit(msg):
    # time.sleep(5.0)
    try:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    except curses.error:
        pass
    except:
        error_preexit(
            "error_preexit: Unexpected error: {} {}".format(
                sys.exc_info()[0], sys.exc_info()[1]
            )
        )
        sys.exit(2)
    logger.error(msg)
    trace = traceback.format_exc()
    if trace != "NoneType: None\n":
        logger.error(trace)
    sys.exit(2)


# file output
def write_file(filename, output):
    if filename is None or filename == "-" or filename == "":
        sys.stderr.write(output)
    else:
        try:
            with open(filename, mode="w", buffering=io.DEFAULT_BUFFER_SIZE) as fp:
                fp.write(output)
        except IOError:
            error_preexit("Error in creating output file: {}".format(filename))
            sys.exit(2)
    return
