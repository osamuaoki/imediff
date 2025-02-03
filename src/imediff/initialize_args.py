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
import argparse

# NO LOGGING YET


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
        "-f", action="store_true", help="Start with all chunks to use wdiff"
    )
    group.add_argument(
        "-g", action="store_true", help="Start with good merge mode (only for diff3)"
    )
    pa.add_argument(
        "-o",
        "--output",
        help="Write output to the given file.  If this is missing, STDERR is used",
    )
    pa.add_argument(
        "-l",
        "--force-logging",
        action="store_true",
        help='Force LOGFILE="imediff.log" and LOGLEVEL="INFO"',
    )
    pa.add_argument(
        "-n",
        "--non-interactive",
        action="store_true",
        help="Use non-interactive CLI instead of normal TUI",
    )
    pa.add_argument(
        "-s",
        "--sloppy",
        action="store_true",
        help="Allow one to save unresolved contents",
    )
    pa.add_argument(
        "-t",
        "--template",
        action="store_true",
        help='Create a template configuration file "~/.imediff"',
    )
    pa.add_argument(
        "-v", "--version", action="store_true", help="Show version and license"
    )
    pa.add_argument(
        "-C",
        "--conf",
        default="~/.imediff",
        help='Specify configuration file to use.  (default="~/.imediff", set this to "none" to use internal configuration only)',
    )
    pa.add_argument("-M", "--macro", default="", help="Set MACRO string.  E.g.: Abw")
    pa.add_argument(
        "-F",
        "--logfile",
        default="/dev/null",
        help='Enable logging to LOGFILE (default logging disabled as LOGFILE="/dev/null").',
    )
    pa.add_argument(
        "-L",
        "--loglevel",
        default="WARNING",
        help='Set LOGLEVEL to "ERROR", "WARNING" (default), "INFO", or "DEBUG"',
    )
    pa.add_argument(
        "-J",
        "--isjunk",
        action="store_true",
        help="Force isjunk to None instead of the default list",
    )
    pa.add_argument(
        "-R",
        "--line-rule",
        action="store",
        default=2,
        help="Fuzzy match line filtering rule (0,1,2,3,10,11,12,13)",
    )
    pa.add_argument(
        "-I",
        "--line-min",
        action="store",
        default=3,
        help="Fuzzy match minimum partial line length",
    )
    pa.add_argument(
        "-A",
        "--line-max",
        action="store",
        default=80,
        help="Fuzzy match maximum partial line length",
    )
    pa.add_argument(
        "-X",
        "--line-factor",
        action="store",
        default=8,
        help="Fuzzy match (partial line length shortening factor/2-depth) x 10, default 8",
    )
    pa.add_argument("file_a", nargs="?", help="file for OLDER(diff2), MYFILE(diff3)")
    pa.add_argument(
        "file_b", nargs="?", help="file for NEWER(diff2), OLDFILE=BASE(diff3)"
    )
    pa.add_argument(
        "file_c",
        nargs="?",
        help="file for ------------, YOURFILE(diff3) (only for diff3)",
    )
    # pa.add_argument("--poke", "-p", nargs="?", default=None, help=argparse.SUPPRESS)
    args = pa.parse_args()
    args.macro_buffer = args.macro
    if args.file_c is not None:
        args.diff_mode = 3
    elif args.file_b is not None:
        args.diff_mode = 2
    elif args.file_a is not None:
        # undocumented help for diff3
        args.diff_mode = 1  # help for imediff for 3 files
    else:
        # undocumented help for diff2
        args.diff_mode = 0  # help for imediff for 2 files
    #
    # help for imediff for 3 files
    if args.a:
        args.default_action = "a"
    elif args.b:
        args.default_action = "b"
    elif args.c and args.diff_mode == 3:
        args.default_action = "c"
    elif args.d:
        args.default_action = "d"
    elif args.f:
        args.default_action = "f"
    elif args.g and args.diff_mode == 3:
        args.default_action = "g"
    elif args.diff_mode == 3:
        args.default_action = "g"
    else:  # diff2
        args.default_action = "d"
    #
    # override for logging
    if args.force_logging:
        if args.loglevel == "WARNING":
            args.loglevel = "INFO"
        if args.logfile == "/dev/null":
            args.logfile = "imediff.log"

    # if args.poke is not None:
    #     print("I: +++ hidden -p/--poke option is used with '{}' +++".format(args.poke))

    return args
