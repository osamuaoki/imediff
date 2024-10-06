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

def initialize_args(logfile="imediff.log"):
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
    pa.add_argument(
        "--linerule",
        "-l",
        action="store",
        default=2,
        help="Line alignment matching rule (0,1,2,3,10,11,12,13)",
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
        "--debug",
        "-D",
        action="store_true",
        help='Generate debug log in "' + logfile + '"',
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
