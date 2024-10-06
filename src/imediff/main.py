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
import locale
import os
import sys
import shutil

# utility imediff functions
from imediff import __version__, __package__
from imediff.utils import error_preexit, logger, read_lines
from imediff.config import create_template
from imediff.cli import TextData
from imediff.tui import TextPad
from imediff.initialize_confs import initialize_confs
from imediff.initialize_args import initialize_args

PACKAGE = __package__
version = __version__

_version = "".join(
    filter(
        None,
        (
            """\
{p} (version {v})
""".format(
                p=PACKAGE, v=version
            ),
            __doc__,
        ),
    )
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
 * Copyright (C) 2018, 2024 Osamu Aoki <osamu@debian.org>

License: GPL 2.0+
===============================================================================
""".format(
    p=PACKAGE, v=version
)

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
    if os.path.isdir(".git"):
        logfile = ".git/imediff.log"
    else:
        logfile = "imediff.log"
    args = initialize_args(logfile)
    if args.template:
        create_template(args.conf)
        sys.exit(0)

    # logging
    logger.setLevel(logging.DEBUG)
    if args.debug:
        # create file handler which logs even debug messages
        fh = logging.FileHandler(logfile)
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
        print(__version__)
        sys.exit(0)
    logger.debug("diff_mode: {}".format(args.diff_mode))
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
        logger.debug("diff_mode == 2")
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
        error_preexit("imediff normally takes 2 or 3 files")
        sys.exit(2)

    logger.debug("tutorial: {}".format(tutorial))
    logger.debug("non_interactive: {}".format(args.non_interactive))
    # call main routine
    if not args.non_interactive:
        display_instance = TextPad(list_a, list_b, list_c, args, confs)
        display_instance.command_loop(tutorial=tutorial)
        del display_instance
    elif tutorial:
        print(_opening)
    else:
        text_instance = TextData(list_a, list_b, list_c, args, confs)
        text_instance.command_loop()
        del text_instance
    sys.exit(0)

