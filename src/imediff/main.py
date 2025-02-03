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
# utility imediff functions
from imediff import __version__, __package__
from imediff.utils import read_lines
from imediff.config import create_template
from imediff.cli import TextData
from imediff.tui import TextPad
from imediff.initialize_confs import initialize_confs
from imediff.initialize_args import initialize_args

import locale
import os
import sys
import shutil
import logging

logger = logging.getLogger(__name__)

PACKAGE = __package__
version = __version__

version_string = "".join(
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

opening = """\
===============================================================================
                               {p}                         (version {v})

The imediff command interactively merges 2 slightly different files with an
optional base file using the in-place alternating display of the changed
content on a single-pane full screen terminal user interface (TUI).

Start this command from the shell command prompt as:
 * "imediff" to read the tutorial,
 * "imediff -h" to get all the command line options,
 * "imediff -o output OLDER NEWER" to merge 2 files, and
 * "imediff -o output MYFILE OLDFILE YOURFILE" to merge 3 files.

In the interactive TUI, you can also type "t" to read the tutorial and type "/"
to display the list of key commands.

 * Copyright (C) 2003,2004 Jarno Elonen <elonen@iki.fi>
 * Copyright (C) 2018-2025 Osamu Aoki <osamu@debian.org>

License: GPL 2.0+
===============================================================================

Type "q" to quit this program.
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
    args = initialize_args()
    logging.basicConfig(
        format="%(levelname)s: %(filename)s: %(funcName)s: %(message)s",
        filename=args.logfile,
        level=getattr(logging, args.loglevel.upper(), logging.WARNING),
    )
    logger.debug(
        "============================== start of main =============================="
    )
    if args.template:
        create_template(args.conf)
        sys.exit(0)

    # configuration
    confs = initialize_confs(args.conf)
    for section in confs.sections():
        for key, value in confs[section].items():
            logger.debug(
                "confs['{}'] >>> key='{}' value='{}'".format(section, key, value)
            )
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
        print(version_string)
        sys.exit(0)

    if args.diff_mode == 0:  # argument contains only zero file
        list_a = (opening).splitlines(keepends=True)
        list_b = list_a
        list_c = []
        args.file_a = ""
        args.file_b = ""
        args.diff_mode = 2
        args.macro = "t"
        confs["config"]["confirm_quit"] = "False"
        confs["config"]["confirm_exit"] = "False"
        logger.debug("=== diff0 === Tutorial for diff2 ===")
    elif args.diff_mode == 1:  # argument contains only 1 file
        list_a = (opening).splitlines(keepends=True)
        list_b = list_a
        list_c = list_a
        args.file_a = ""
        args.file_b = ""
        args.file_c = ""
        args.diff_mode = 3
        args.macro = "t"
        confs["config"]["confirm_quit"] = "False"
        confs["config"]["confirm_exit"] = "False"
        logger.debug("=== diff1 === Tutorial for diff3 ===")
    elif args.diff_mode == 2:
        # diff2
        list_a = read_lines(args.file_a)
        list_b = read_lines(args.file_b)
        list_c = None
        logger.debug(
            "=== diff2 === default_action='{}' non_interactive={} ===".format(
                args.default_action, args.non_interactive
            ),
        )
    elif args.diff_mode == 3:
        list_a = read_lines(args.file_a)
        list_b = read_lines(args.file_b)
        list_c = read_lines(args.file_c)
        logger.debug(
            "=== diff3 === default_action='{}' non_interactive={} ===".format(
                args.default_action, args.non_interactive
            ),
        )
    else:
        logger.error("imediff normally takes 2 or 3 files")
        sys.exit(2)

    if not args.non_interactive:
        display_instance = TextPad(list_a, list_b, list_c, args, confs)
        # set textpad size
        display_instance.main()
        del display_instance
    else:  # non-interactive
        text_instance = TextData(list_a, list_b, list_c, args, confs)
        text_instance.main()
        del text_instance
    logger.debug("end of main")
    sys.exit(0)
