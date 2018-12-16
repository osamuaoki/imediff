#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
IMEDIFF - an Interactive Merge Editor for DIFF2 and DIFF3
          Curses based single-pane fullscreen tool

Copyright (C) 2003, 2004 Jarno Elonen <elonen@iki.fi>
Copyright (C) 2018       Osamu Aoki <osamu@debian.org>

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
import gettext
import locale
import io
import sys
import traceback
import types
import curses

__all__ = ['_', 'logger', 'read_lines', 'error_exit', 'write_file']

# Utility functions

# gettext for i18n
gettext.bindtextdomain('imediff')
gettext.textdomain('imediff')
_ = gettext.gettext

# logger
logger = logging.getLogger(__name__)

# file read
def read_lines(filename):
    if filename is None or filename =="":
        lines = []
    else:
        try:
            with open(filename, buffering=io.DEFAULT_BUFFER_SIZE) as fp:
                lines = fp.readlines() # read into list
        except IOError as e:
            (error, message) = e.args
            if error == errno.ENOENT:
                lines = []
            else:
                error_exit(
"Could not read '{}': {}\n".format(filename, message))
        except:
            error_exit("read_lines: Unexpected error: {} {}".format(sys.exc_info()[0], sys.exc_info()[1]))
    return lines

# error exit
def error_exit(msg):
    #time.sleep(5.0)
    try:
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    except curses.error:
        pass
    except:
        error_exit("error_exit: Unexpected error: {} {}".format(sys.exc_info()[0], sys.exc_info()[1]))
    logger.error(msg)
    trace = traceback.format_exc()
    if trace != "NoneType: None\n":
        logger.error(trace)
    sys.exit(22)

# file output
def write_file(filename, output):
    if filename is None or filename == "-" or filename == "":
        sys.stderr.write(output)
    else:
        try:
            with open(filename, mode='w', buffering=io.DEFAULT_BUFFER_SIZE) as fp:
                fp.write(output)
        except IOError:
            error_exit("Error in creating output file: {}".format(filename))
    return

