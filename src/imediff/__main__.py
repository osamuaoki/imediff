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

import argparse
import configparser
import logging
import gettext
import curses
import locale
import io
import os
import sys
import shutil
import traceback

# utility diff functions
from imediff.utils import *
from imediff.config import *
from imediff.cli import *
from imediff.tui import *

VERSION = "2.4"
PACKAGE = "imediff"

_version = (
    """\
{p} (version {v})
""".format(
        p=PACKAGE, v=VERSION
    )
    + __doc__
)

_opening = """\
===============================================================================
                               {p}                         (version {v})

The imediff command helps you to merge 2 slightly different files with an
optional base file interactively using the in-place alternating display of
the changed content on a single-pane full screen terminal user interface.

The source of line is clearly identified by the color of the line or the
identifier character at the first column.

From the console command line prompt, type:
 * "imediff" to read the tutorial,
 * "imediff -h" to get all the command line options,
 * "imediff -o output older newer" to merge 2 files, and
 * "imediff -o output yours base theirs" to merge 3 files.

For usage instructions, type "h" and "H" in the interactive screen.

 * Copyright (C) 2003, 2004 Jarno Elonen <elonen@iki.fi>
 * Copyright (C) 2018       Osamu Aoki <osamu@debian.org>

License: GPL 2.0+
===============================================================================
""".format(
    p=PACKAGE, v=VERSION
)


def initialize_args():
    """
    Parse command line options and arguments

    Input:
        commandline

    Return:
        args    argument values
    """
    pa = argparse.ArgumentParser(
        description="Interactive Merge Editor for 2 or 3 different files",
        epilog='Start "imediff" without any arguments to see the tutorial.',
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
    group.add_argument(
        "-d", action="store_true", help="Start with all chunks to use diff"
    )
    group.add_argument(
        "-u", action="store_true", help=argparse.SUPPRESS
    )  # Start with unresolved diff
    group.add_argument(
        "-f", action="store_true", help="Start with all chunks to use wdiff"
    )
    group.add_argument(
        "-g", action="store_true", help="Start with good merge mode (only for diff3)"
    )
    group.add_argument(
        "--isjunk",
        action="store_true",
        help="Force isjunk to None instead of the default list",
    )
    pa.add_argument("--mode", "-m", action="store_true", help="Display mode column")
    pa.add_argument("--mono", action="store_true", help="Force monochrome display")
    pa.add_argument(
        "--sloppy", action="store_true", help="Allow one to save unresolved contents"
    )
    pa.add_argument(
        "--version", "-V", action="store_true", help="Show version and license"
    )
    pa.add_argument(
        "--output",
        "-o",
        help="\
Write output to the given file.  If this is missing, use STDERR",
    )
    pa.add_argument(
        "--conf",
        "-C",
        default="~/.imediff",
        help='\
Specify configuration file to use.  (default="~/.imediff")',
    )
    # hidden option for debug: non-interactive diff/merge operation
    pa.add_argument(
        "--non-interactive", "-n", action="store_true", help="execution without curses"
    )
    pa.add_argument("--macro", "-M", default=":", help="set MACRO string")
    pa.add_argument(
        "--template",
        "-t",
        action="store_true",
        help='Create a template configuration file "~/.imediff"',
    )
    pa.add_argument(
        "--debug", "-D", action="store_true", help='Generate debug log in "imediff.log"'
    )
    pa.add_argument("file_a", nargs="?", help="file for OLDER(diff2), YOURS(diff3)")
    pa.add_argument("file_b", nargs="?", help="file for NEWER(diff2), BASE(diff3)")
    pa.add_argument(
        "file_c",
        nargs="?",
        help="file for ------------, THEIRS(diff3) (only for diff3)",
    )
    args = pa.parse_args()
    args.macro_buffer = args.macro
    if args.file_c is not None:
        args.diff_mode = 3
    elif args.file_b is not None:
        args.diff_mode = 2
    else:
        args.diff_mode = 0
    if args.a:
        args.default_mode = "a"
    elif args.b:
        args.default_mode = "b"
    elif args.c and args.diff_mode == 2:
        args.default_mode = "d"  # backward compatibility -c
    elif args.c and args.diff_mode == 3:
        args.default_mode = "c"
    elif args.d or args.u:
        args.default_mode = "d"  # hidden backward compatibility -u
    elif args.f:
        args.default_mode = "f"
    else:  # default=None or "g"
        if args.diff_mode == 2:
            args.default_mode = "d"  # default diff2
        else:
            args.default_mode = "g"  # default diff3
    return args


def initialize_confs(conf):
    """Process configuration file"""
    config_file = os.path.expanduser(conf)
    # Allow inline comment with #
    confs_i = configparser.ConfigParser(inline_comment_prefixes=("#"))
    confs_i.read_string(config_template)
    confs_f = configparser.ConfigParser(inline_comment_prefixes=("#"))
    if os.path.exists(config_file):
        confs_f.read(config_file)
        if (
            "version" in confs_f["config"].keys()
            and confs_f["config"]["version"] == confs_i["config"]["version"]
        ):
            confs = confs_f
        else:
            error_exit(
                '''\
Error in {0}: version mismatch
        the current version:  {1}
        the required version: {2}

Rename {0} to {0}.bkup and make the new {0} by
editing the template obtained by "imediff -t"'''.format(
                    conf, confs_f["config"]["version"], confs_i["config"]["version"]
                )
            )
    else:
        confs = confs_i
    return confs


##############################################################################
def main():
    """
    Entry point for imediff command

    Exit value
        0       program exits normally after saving data
        1       program quits without saving
        2       program terminates after an internal error
    """

    # preparation and arguments
    locale.setlocale(locale.LC_ALL, "")
    args = initialize_args()
    if args.template:
        create_template(args.conf)
        sys.exit(0)

    # logging
    logger.setLevel(logging.DEBUG)
    if args.debug:
        # create file handler which logs even debug messages
        fh = logging.FileHandler("imediff.log")
    else:
        # create file handler which doesn't log
        fh = logging.NullHandler()
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # configuration
    confs = initialize_confs(args.conf)
    editor = "editor"
    if "EDITOR" in os.environ:
        editor = os.environ["EDITOR"]
    if "editor" in confs["config"].keys():
        editor = confs["config"]["editor"]
    args.edit_cmd = shutil.which(editor)
    if args.edit_cmd is None:
        args.edit_cmd = "/usr/bin/editor"  # safe fall back
    logger.debug("external editor {} found as {}".format(editor, args.edit_cmd))

    # normalize and process non-standard situation
    if args.version:
        print(_version)
        sys.exit(0)
    if args.diff_mode == 0 and args.non_interactive:
        tutorial = True
    if args.diff_mode == 0:
        args.diff_mode = 3  # Fake input
        list_a = (_opening + '\n    Type "q" to quit this tutorial.').splitlines(
            keepends=True
        )
        list_b = [""]
        list_c = list_a
        confs["config"]["confirm_quit"] = "False"
        confs["config"]["confirm_exit"] = "False"
        tutorial = True
    elif args.diff_mode == 2:
        # diff2
        list_a = read_lines(args.file_a)
        list_b = read_lines(args.file_b)
        list_c = None
        tutorial = False
    elif args.diff_mode == 3:
        list_a = read_lines(args.file_a)
        list_b = read_lines(args.file_b)
        list_c = read_lines(args.file_c)
        tutorial = False
    else:
        error_exit("imediff normally takes 2 or 3 files")
    if args.isjunk:
        isjunk = None
    else:
        isjunk = lambda x: x in ["\n", "#\n", "//\n"]

    # call main routine
    if not args.non_interactive:
        display_instance = TextPad(list_a, list_b, list_c, args, confs, isjunk)
        display_instance.command_loop(tutorial=tutorial)
        del display_instance
    elif tutorial:
        print(_opening)
    else:
        text_instance = TextData(list_a, list_b, list_c, args, confs, isjunk)
        text_instance.command_loop()
        del text_instance
    sys.exit(0)
