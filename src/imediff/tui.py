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

from difflib import SequenceMatcher
from imediff.diff3lib import SequenceMatcher3
from imediff.utils import write_file, s_number
from imediff.cli import TextData
from imediff.safe_curses import get_keyname, display_content

import curses
import sys
import logging

logger = logging.getLogger(__name__)

# Keep this under 74 char/line for better looks
# I need this hack to avoid translation of tutorial for now. XXX FIXME XXX
nonclean = """\
This requirement of the clean merge for 'save and exit' can be disabled by
specifying the "--sloppy" option to the imediff command.  Alternatively,
you can effectively evade this requirement by pressing "m" on all
non-clean merges to make them as the manually edited text data."""


# Keep this under 76 char/line to fit this in the 80 char terminal
tutorial = """\
Quick start:
  * Use cursor keys and h/j/k/l/n/p/0 to read this tutorial screen.
  * Type SPACE to exit this tutorial screen to the main screen.
  * Type "t" to get back to this tutorial screen.
  * Type "/" in the main screen to see the key bindings.

---------------------------------------------------------------------------
    Tutorial for imediff (Interactive Merge Editor)
                        Copyright (C) 2024 Osamu Aoki <osamu@debian.org>
---------------------------------------------------------------------------

The imediff command helps you to merge/pick contents from 2 slightly
different files with an optional base file interactively using the in-place
alternating display of the changed content on a single-pane full screen
terminal user interface.  (diff2: 2 files, diff3: 3 files)

(The original program by Jarno Elonen <elonen@iki.fi> was called "imediff2".
I changed its command name to imediff when I made major updates to handle
diff2-pick-operation for 2 files but also handle diff3-merge-operation for 3
files in version 2.0.)

Each minimal portion of "imediff" data lines for the merge/pick operation is
called as "chunk" in the "imediff" terminology.  Some chunks (internally
tracked as "usr_chunk") can accept user action (or MACRO) to change the
outcome of merge/pick operation.  User's "action_request" is recorded as
"action" in "chunk" data.

The focused chunk for the active merge/pick operation is clearly identified
with the reversed characters and always located at around the top 1/3
position whenever possible.  The source of the chunk is identified by the
color of the characters used or an optional identifier character at the
first column.

The advantage of this user interface is the minimal movement of the line of
sight for the user.  Other great tools such as vimdiff, xxdiff, meld and
kdiff3 require you to look at different points of display to find the exact
position of changes.  This makes imediff the most stress-free tool.

Merge with 2 files
==================

Let's try to merge 2 almost identical files, "file_a" (OLDER) and "file_b"
(NEWER), into an output file, "file_o".  You can do this with the following.

    $ imediff -o file_o file_a file_b

This mode starts with action "d" as the default behavior.  Initially all the
different lines in "file_a" and "file_b" are grouped them in "usr_chunk"
list and displayed as action "d" which combines the corresponding "file_a"
and "file_b" content separated by marker lines.

You can move focus to the next usr_chunk by pressing "Space", or "n" keys.
You can move focus to the previous usr_chunk by pressing "Back Space", or
"p" keys.

You can change the resulting output file "file_o" for the "usr_chunk" listed
portion by applying a single key action command.  Pressing "a" displays and
outputs the "file_a" content.  Pressing "b" displays and outputs the
"file_b" content.

By alternating "a" and "b" keys, you can see the difference in place which
is easy on you with the constant line of sight.  (This is the design feature
inherited from the original imediff2 program.)

You can display both the "file_a" content and the "file_b" content with 2
key commands.  Pressing "d" displays 2 blocks of lines organized somewhat
like "diff -u" (action "d").  Pressing "f" on a single line chunk displays
intermixed 1 block of lines organized somewhat like "wdiff" (action "f").

Pressing "m" starts an editor to edit the focused chunk from any modes to
create a manually merged content.  Upon exiting the editor, its result is
kept in the "merge_buffer".  Even after pressing "a", "b", "d", or "f", the
content of the "merge_buffer" can be recalled and displayed by pressing "e".

Pressing "M" in action "e" removes the editor result buffer.

When you press one of the upper case "A", "B", "D", "E", "F", this sets all
chunks to the corresponding lower case action.

All chunks with changed data must select "a", "b", or "e" (excluding "d" and
"f") before writing the merge result unless "--sloppy" is specified before
writing the result.  Type "w" or "x" to write the displayed content to
"file_o" and exit the imediff program.

This requirement of the clean merge for 'save and exit' can be disabled by
specifying the "--sloppy" option to the imediff command.  Alternatively, you
can effectively evade this requirement by pressing "m" on all non-clean
merges to make them as the manually merged data.

Although the imediff program is practically WYSIWYG, there are some
exceptions. The imediff program displays a place holder marker "???" line
for the deleted content of the action "a" or "b", and separator marker lines
for the action "d", and separator characters for the action "f".

The associated "git ime" command can help refactoring a squashed large git
commit into a nice hitory of multiple meaningful git commits by using
"imediff" as its split engine and optionally using "git rebase -i ...", and
"gitk" to organize them.

Merge with 3 files
==================

Let's try to merge 2 almost identical files, "file_a" (MYFILE) and "file_c"
(YOURFILE), both of which are based on the file, "file_b" (OLDFILE=BASE),
into an output file, "file_o".  You can do this with the following.

    $ imediff -o file_o file_a file_b file_c

This mode starts with "-g" as the default starting option and displays a
full screen of the content for the intended output "file_o".  Since this
uses extra "file_b" (OLDFILE), it can automatically megrge non-identical
chunks of "file_a" (MYFILE) and "file_c" (YOURFILE) using line.

Key actions and functionalities of "Merge with 3 files" are almost the same
as those for "Merge with 2 files".  One notable "action" is pressing "g".
This is also the default starting "action" for "Merge with 3 files" and
takes advantage of the extra BASE file to do auto-merge.  It
acts in the following order:
 * If the "merge_buffer" has a previously stored manually generated merge
   result, "action" is set to "e" to activate it.
 * If a chunk is auto-merged cleanly by line-by-line comparison or more fine
   grained character comparison, "action" is set to "=", "#", "A", "C", or
   "G". These chunks are already merged properly and excluded from the
   "usr_chunk" list.
 * The un-merged data is presented as action "d".

Please note that even for the non-overlapping changes on the same line,
imediff can yield the clean merge with action "G". (This is the great
feature of the imediff command over tools such as "diff3 -m ..." and "git
merge ..." which operate only by line-by-line comparison.)

Only really unresolved chunks are displayed in action "d".

The rests are mostly the same as "Merge with 2 files".

Terminal
========

The imediff program is compatible with any terminal window sizes.  It
supports both monochrome and color terminals.  For comfortable user
experience, terminal width of 80 characters/line or more and terminal height
of 24 lines or more are desirable.

The first column is used to indicate the source of the data displayed.

 * "=" means the displayed chunk underwent no changes for all sources and
   the merge is resolved:
   * diff2: a==b (merged)
   * diff3: a==b==c (merged)
 * "#" means the displayed chunk underwent the same set of changes from the
   base source to both updated sources and the merge is resolved:
   * diff2: N/A
   * diff3: a==c (merged)
 * Independent "A", "C", and "G" means a chunk from the corresponding
   source is displayed as auto-resolved. (only for diff3)
 * Independent "a", "b", "c" and "e" means a chunk from the corresponding
   source is displayed as manually resolved.
 * Diff-marker identified "a", "b", "c" means a chunk is un-resolved
 * Wdiff display line with "f" means a chunk is un-resolved
 * Deleted line is displayed as "??? (*)" on display

Focus jumping has 2 modes:
 * Jump to chunks available for changes: n, p, SPACE, BACKSPACE
 * Jump to only unresolved chunks: N, P, TAB, BTAB

Customization
=============

The imediff program can customize its key binding and its color setting with
the "~/.imediff" file in the ini file format.  You can create its template
file by the "imediff -t" command.

You can disable an existing "~/.imediff" file without renaming it by
specifying "none" as "imediff -C none ...". Only the internal default values
of the imediff program are used.

Custom starting and automatic processing with imediff can be enabled using
key macro featurs.  For example, git-ime uses "Abw" to dicect a single file
change commit to fine grained minimal commits.

Note
====

The version 3.0 is a major rewrite to address file size limitation caused by
the underlying curses library and to limit wdiff to operate only within a
single line."""

# The "diff3 -m" has an odd feature for the merge when "file_a" and "file_c"
# undergo identical changes from "file_b".  This imediff program results in a
# more intuitive merge result.


class TextPad(TextData):  # TUI data
    """Curses class to handle diff data for 2 or 3 lines"""

    ####################################################################
    # Externally exposed initializer method
    ####################################################################
    #  self.chunk_list[chunk_index] = (                # for CLI and TUI
    #      tag,             # diff opcode tag EeNFAC
    #      i1,              # self.list_a (start)-index
    #      i2,              # self.list_a (end+1)-index
    #      j1,              # self.list_b (start)-index
    #      j2,              # self.list_b (end+1)-index
    #      k1,              # self.list_c (start)-index
    #      k2,              # self.list_c (end+1)-index
    #      action,      # data action abcdefg (self.default_action)
    #      merge_buffer,    # merge_buffer for editor ([])
    #  ) # chunk_list item tuple (9 param)
    #
    #  self.usr_chunk_list: list of user accessible chunk_index
    #
    #  self.chunk_to_virt[chunk_index]: virt_row (TUI)
    #
    def __init__(self, list_a, list_b, list_c, args, confs):
        # Init from super class "TextData"
        super().__init__(list_a, list_b, list_c, args, confs)
        logger.debug("starting ...")
        self.init_args_confs_tui(args, confs)
        self.chunk_to_virt = list()
        self.virt_to_chunk = list()
        logger.debug("finished")
        return

    def init_args_confs_tui(self, args, confs):
        # Init from commandline/configuration parameters
        self.default_action = args.default_action  # display with action prefix
        self.tutorial = False
        self.mono = args.mono  # display in monochrome
        if self.diff_mode == 0:
            self.diff_mode = 2
            self.tutorial = True
        elif self.diff_mode == 1:
            self.diff_mode = 3
            self.tutorial = True
        self.attrib = confs["attrib"]
        # self.poke = args.poke  # display in monochrome

    ####################################################################
    # Externally used main method and effective main method
    ####################################################################
    # Design concept:
    #     * Use full terminal screen
    #     * Access them directly (no window nor pad)
    #     * String operation by pointers
    #
    # See https://docs.python.org/3/library/curses.html
    #     https://docs.python.org/3/howto/curses.html
    #
    # curses terminal screen absolute coordinate as (y,x):
    # +----------------------------------------------------------------+
    # | (0,0) top-left corner                        (stdscr_col_max-1)|
    # |  +--> x-axis                                                   |
    # |  |                                                             |
    # |  |                    TEXT DATA DISPLAY                        |
    # |  V y-axis                                                      |
    # |                                                                |
    # |                                                                |
    # | (stdscr_row_max-2,0)        (stdscr_row_max-2,stdscr_col_max-1)|
    # +----------------------------------------------------------------+
    # | (stdscr_row_max-1,0) STATUS (stdscr_row_max-1,stdscr_col_max-1)|
    # +----------------------------------------------------------------+
    #
    # Here:
    #     * stdscr_row_max, stdscr_col_max = stdscr.getmaxyx()
    #
    # Internal data:
    #   * CLI
    #     * chunk_list[chunk_index]: -> chunk_list item tuple
    #     * usr_chunk_list[usr_chunk_index]: -> chunk_index
    #   * TUI
    #     * chunk_to_virt[chunk_index] = virt_row
    #     * virt_to_row[virt_row] = (chunk_index, chunk_subindex, action)
    # Terminal size: 80 col x 24 row required
    #
    ####################################################################

    def main(self):  # for curses TUI (wrapper)
        """Interactive driven by CURSES-TUI"""
        logger.debug("start with macro = '{}'".format(self.macro))
        curses.wrapper(self.tui_loop)
        logger.debug("finished")
        return

    def tui_loop(self, stdscr):  # for curses TUI (core)
        logger.debug("start with macro = '{}'".format(self.macro))
        # initialize
        curses.curs_set(0)  # cursor off
        self.init_curses(stdscr)
        # display parameters
        flag_update_corner = True
        corner_virt_row = 0
        corner_virt_col = 0
        while True:
            self.remap_chunk_virt()
            if len(self.chunk_list) != len(self.chunk_to_virt):
                logger.error(
                    "E: insane: len(chunk_list) != len(chunk_to_virt): {} {}".format(
                        len(self.chunk_list), len(self.virt_to_chunk)
                    )
                )
                sys.exit(2)
            if flag_update_corner:
                if self.focused_usr_chunk_index is None:
                    logger.info(
                        "W: focused_usr_chunk_index=None (cleanly merged files?)"
                    )
                    corner_virt_row = 0
                else:
                    focused_chunk_index = self.get_chunk_index_from_usr_chunk_list(
                        self.focused_usr_chunk_index
                    )
                    if focused_chunk_index is not None:
                        stdscr_row_max, _ = self.stdscr.getmaxyx()
                        focused_virt_row = self.chunk_to_virt[focused_chunk_index]
                        corner_virt_row = max(
                            focused_virt_row - ((stdscr_row_max - 1) // 3), 0
                        )
                        logger.debug(
                            "focused_chunk_index={} >> focused_virt_row={} >> corner_virt_row={}".format(
                                focused_chunk_index, focused_virt_row, corner_virt_row
                            )
                        )
            flag_update_corner = False
            self.display_data(corner_virt_row, corner_virt_col)
            if self.tutorial:
                keyname = "t"
                self.tutorial = False
            else:
                keyname = self.get_macro_command()
            if keyname in ["IGNORE"]:
                logger.warning("W: ignore key/macro input")
                pass
            elif keyname in ["w", "x"]:
                if self.sloppy or (
                    not self.sloppy and self.get_unresolved_count() == 0
                ):
                    if not self.confirm_exit or self.display_popup_win(
                        "Do you 'save and exit'? (Press '{y:}' to exit)".format(
                            y=self.rkc["y"]
                        ),
                        ["y", "Y", "N", "n", "SPACE", "ESCAPE"],
                    ) in ["y", "Y"]:
                        write_file(self.file_o, self.get_string_from_content_for_file())
                        break
                else:
                    self.display_popup_win(
                        (
                            "Can't 'save and exit' due to the non-clean merge. (Press {SPACE:} or {y:} to continue)"
                            + "\n\n"
                            + nonclean
                        ).format(SPACE=self.rkc["SPACE"], y=self.rkc["y"]),
                        ["y", "Y", "SPACE"],
                    )
            elif keyname in ["QUIT", "q"]:
                if not self.confirm_exit or self.display_popup_win(
                    "Do you 'quit without saving'? (Press '{y:}' to quit)".format(
                        y=self.rkc["y"]
                    ),
                    ["y", "Y", "N", "n", "SPACE", "ESCAPE"],
                ) in ["y", "Y"]:
                    self.chunk_list = []
                    logger.error("Quit without saving by the user request")
                    sys.exit(2)
            elif keyname in ["?", "/", "F1"]:
                # Show help screen
                self.display_content_win(
                    self.get_helptext(), ["SPACE", "ESCAPE", "q", "Q"]
                )
            elif keyname == "t":
                # Show tutorial screen
                self.display_popup_win(
                    tutorial, ["SPACE", "ESCAPE", "q", "Q"], "color_white"
                )
            # Moves in document
            elif keyname in ["j", "DOWN"]:
                corner_virt_row += 1
            elif keyname in ["k", "UP"]:
                corner_virt_row -= 1
            elif keyname in ["l", "RIGHT"]:
                corner_virt_col += 8
            elif keyname in ["h", "LEFT"]:
                corner_virt_col -= 8
            elif keyname in ["PAGEDOWN"]:
                corner_virt_row += 20
            elif keyname in ["PAGEUP"]:
                corner_virt_row -= 20
            # Terminal resize signal
            else:
                pass
            # Following key-command updates TextPad
            if self.focused_usr_chunk_index is not None:
                chunk_index = self.usr_chunk_list[self.focused_usr_chunk_index]
                # record current action
                action = self.get_action(chunk_index)
                # Explicitly select chunk action
                if keyname in ["a", "b", "c", "d", "e", "f", "g"]:
                    self.set_action(chunk_index, keyname)
                    flag_update_corner = True
                elif keyname in ["1", "2", "3", "4", "5", "6", "7"]:
                    self.set_action(
                        chunk_index,
                        chr(ord(keyname) - ord("1") + ord("a")),
                    )
                    flag_update_corner = True
                elif keyname in ["", "A", "B", "C", "D", "E", "F", "G"]:
                    self.set_action_all(keyname.lower())
                    flag_update_corner = True
                elif keyname in ["ENTER"]:
                    # Enter key will rotate action setting
                    # 2: a -> b      -> d -> [e ->] f -> a
                    # 3: a -> b -> c -> d -> [e ->] f -> a
                    if action == "a":
                        self.set_action(chunk_index, "b")
                    elif action == "b" and self.diff_mode == 2:
                        self.set_action(chunk_index, "d")
                    elif action == "b" and self.diff_mode == 3:
                        self.set_action(chunk_index, "c")
                    elif action == "c":
                        self.set_action(chunk_index, "d")
                    elif (
                        action == "d" and self.get_merge_buffer(chunk_index) is not None
                    ):
                        self.set_action(chunk_index, "e")
                    elif action == "d":
                        self.set_action(chunk_index, "f")
                    elif action == "e":
                        self.set_action(chunk_index, "f")
                    else:  # f
                        self.set_action(chunk_index, "a")
                    flag_update_corner = True
                elif keyname in ["m"]:
                    self.set_updated_merge_buffer(chunk_index)
                    flag_update_corner = True
                elif keyname in ["M"]:
                    self.set_deleted_merge_buffer(chunk_index)
                    flag_update_corner = True
                elif keyname in ["n", "SPACE"]:
                    self.move_focus_to_any_resolvable_chunk_next()
                    flag_update_corner = True
                elif keyname in ["p", "BACKSPACE"]:
                    self.move_focus_to_any_resolvable_chunk_prev()
                    flag_update_corner = True
                elif keyname in ["HOME"]:
                    self.move_focus_to_any_resolvable_chunk_home()
                    flag_update_corner = True
                elif keyname in ["END"]:
                    self.move_focus_to_any_resolvable_chunk_end()
                    flag_update_corner = True
                elif keyname in ["N", "TAB"]:
                    self.move_focus_to_usr_chunk_next()
                    flag_update_corner = True
                elif keyname in ["P", "BTAB"]:
                    self.move_focus_to_usr_chunk_prev()
                    flag_update_corner = True
                elif keyname in ["0"]:
                    self.move_focus_to_usr_chunk_home()
                    flag_update_corner = True
                elif keyname in ["9"]:
                    self.move_focus_to_usr_chunk_end()
                    flag_update_corner = True
                else:
                    pass
            # lower boundary check
            corner_virt_col = max(0, corner_virt_col)
            corner_virt_row = max(0, corner_virt_row)
            # TODO: upper boundary check
        logger.debug("finished")
        return

    ####################################################################
    # Internally used utility methods (update internal data)
    ####################################################################
    # This is brute force update of all the internal data
    # This may be updated to update only data affected

    def remap_chunk_virt(self):
        virt_row_next = 0
        self.chunk_to_virt = list()
        # [ virt_row, ...]
        self.virt_to_chunk = list()
        # [(chunk_index, chunk_subindex, action), ...]
        for chunk_index in range(len(self.chunk_list)):
            virt_row = virt_row_next
            self.chunk_to_virt.append(virt_row)
            (
                tag,
                i1,
                i2,
                j1,
                j2,
                k1,
                k2,
                action,
                merge_buffer,
            ) = self.chunk_list[chunk_index]
            # virt_range
            if action == "=" or action == "#":
                virt_range = i2 - i1
                if virt_range > 0:
                    for virt_row_index in range(virt_row, virt_row + virt_range):
                        chunk_subindex = virt_row_index - virt_row
                        self.virt_to_chunk.append((chunk_index, chunk_subindex, action))
                else:
                    # no content consumes 1 line for "???"
                    virt_range = 1
                    self.virt_to_chunk.append((chunk_index, 0, action))
            elif action == "a" or action == "A":
                virt_range = i2 - i1
                if virt_range > 0:
                    for virt_row_index in range(virt_row, virt_row + virt_range):
                        chunk_subindex = virt_row_index - virt_row
                        self.virt_to_chunk.append((chunk_index, chunk_subindex, action))
                else:
                    # no content consumes 1 line for "???"
                    virt_range = 1
                    self.virt_to_chunk.append((chunk_index, 0, action))
            elif action == "b":
                virt_range = j2 - j1
                if virt_range > 0:
                    for virt_row_index in range(virt_row, virt_row + virt_range):
                        chunk_subindex = virt_row_index - virt_row
                        self.virt_to_chunk.append((chunk_index, chunk_subindex, action))
                else:
                    # no content consumes 1 line for "???"
                    virt_range = 1
                    self.virt_to_chunk.append((chunk_index, 0, action))
            elif action == "B":
                virt_range = j2 - j1
                if virt_range > 0:
                    for virt_row_index in range(virt_row, virt_row + virt_range):
                        chunk_subindex = virt_row_index - virt_row
                        self.virt_to_chunk.append((chunk_index, chunk_subindex, action))
                else:
                    # no content consumes 1 line for "???"
                    virt_range = 1
                    self.virt_to_chunk.append((chunk_index, 0, action))
            elif action == "c" or action == "C":
                virt_range = k2 - k1
                if virt_range > 0:
                    for virt_row_index in range(virt_row, virt_row + virt_range):
                        chunk_subindex = virt_row_index - virt_row
                        self.virt_to_chunk.append((chunk_index, chunk_subindex, action))
                else:
                    # no content consumes 1 line for "???"
                    virt_range = 1
                    self.virt_to_chunk.append((chunk_index, 0, action))
            elif action == "d" and self.diff_mode == 2:
                self.virt_to_chunk.append((chunk_index, 0, "d20"))
                virt_range_a = i2 - i1
                for virt_row_index in range(virt_row, virt_row + virt_range_a):
                    chunk_subindex = virt_row_index - virt_row
                    self.virt_to_chunk.append((chunk_index, chunk_subindex, "a"))
                self.virt_to_chunk.append((chunk_index, 0, "d21"))
                virt_range_b = j2 - j1
                for virt_row_index in range(virt_row, virt_row + virt_range_b):
                    chunk_subindex = virt_row_index - virt_row
                    self.virt_to_chunk.append((chunk_index, chunk_subindex, "b"))
                self.virt_to_chunk.append((chunk_index, 0, "d22"))
                # diff2 consumes 3 extra lines as separators
                virt_range = virt_range_a + virt_range_b + 3
            elif action == "d" and self.diff_mode == 3:
                self.virt_to_chunk.append((chunk_index, 0, "d30"))
                virt_range_a = i2 - i1
                for virt_row_index in range(virt_row, virt_row + virt_range_a):
                    chunk_subindex = virt_row_index - virt_row
                    self.virt_to_chunk.append((chunk_index, chunk_subindex, "a"))
                self.virt_to_chunk.append((chunk_index, 0, "d31"))
                virt_range_b = j2 - j1
                for virt_row_index in range(virt_row, virt_row + virt_range_b):
                    chunk_subindex = virt_row_index - virt_row
                    self.virt_to_chunk.append((chunk_index, chunk_subindex, "b"))
                self.virt_to_chunk.append((chunk_index, 0, "d32"))
                virt_range_c = k2 - k1
                for virt_row_index in range(virt_row, virt_row + virt_range_c):
                    chunk_subindex = virt_row_index - virt_row
                    self.virt_to_chunk.append((chunk_index, chunk_subindex, "c"))
                self.virt_to_chunk.append((chunk_index, 0, "d33"))
                # diff2 consumes 3 extra lines as separators
                virt_range = virt_range_a + virt_range_b + virt_range_c + 4
            elif action == "e" and len(merge_buffer) > 0:
                virt_range = len(merge_buffer)
                for chunk_subindex in range(virt_range):
                    self.virt_to_chunk.append((chunk_index, chunk_subindex, action))
            elif action == "G" and len(merge_buffer) > 0:
                virt_range = len(merge_buffer)
                for chunk_subindex in range(virt_range):
                    self.virt_to_chunk.append((chunk_index, chunk_subindex, action))
            elif (
                action == "f" and i2 - i1 == 1 and j2 - j1 == 1 and self.diff_mode == 2
            ):
                virt_range = 1
                self.virt_to_chunk.append((chunk_index, 0, action))
            elif (
                action == "f"
                and i2 - i1 == 1
                and j2 - j1 == 1
                and k2 - k1 == 1
                and self.diff_mode == 3
            ):
                virt_range = 1
                self.virt_to_chunk.append((chunk_index, 0, "f"))
            else:
                logger.error(
                    "E: bad combination - diff{} action: {}, tag: {}, a[{}:{}] b[{}:{}] c[{}:{}] len[e]={}".format(
                        self.diff_mode,
                        action,
                        tag,
                        i1,
                        i2,
                        j1,
                        j2,
                        k1,
                        k2,
                        len(merge_buffer),
                    )
                )
                sys.exit(2)
            # This increments virt_row for virt_range per loop
            virt_row_next = virt_row + virt_range
        # debug
        for chunk_index, virt_row in enumerate(self.chunk_to_virt):
            logger.debug("chunk[{}] --> virt_row[{}]".format(chunk_index, virt_row))

        for virt_row, (chunk_index, chunk_subindex, action) in enumerate(
            self.virt_to_chunk
        ):
            logger.debug(
                "virt_row[{}] --> (chunk[{}], chunk_subindex={}, action:{})".format(
                    virt_row, chunk_index, chunk_subindex, action
                )
            )
        logger.debug(
            "len(chunk_list)={}, len(usr_chunk_list)={}, len(virt_to_chunk)={}, len(chunk_to_virt)={}".format(
                len(self.chunk_list),
                len(self.usr_chunk_list),
                len(self.virt_to_chunk),
                len(self.chunk_to_virt),
            )
        )
        return

    ####################################################################
    # Internally used utility methods (initializer within tui_main)
    ####################################################################
    def init_curses(self, stdscr):
        self.stdscr = stdscr
        stdscr_row_max, stdscr_col_max = self.stdscr.getmaxyx()
        if stdscr_row_max < 20 or stdscr_col_max < 60:
            logger.error(
                "E: terminal size too small: {} {}".format(
                    stdscr_row_max, stdscr_col_max
                )
            )
            sys.exit(2)
        self.stdscr.clear()
        self.stdscr.refresh()
        # set up color
        curses.start_color()

        # C-library
        # COLOR_BLACK   0
        # COLOR_RED     1
        # COLOR_GREEN   2
        # COLOR_YELLOW  3
        # COLOR_BLUE    4
        # COLOR_MAGENTA 5
        # COLOR_CYAN    6
        # COLOR_WHITE   7

        # curses.init_pair(0, curses.COLOR_WHITE,   curses.COLOR_BLACK)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

        self.curses_value = dict()
        self.curses_value["WHITE"] = curses.color_pair(0)
        self.curses_value["RED"] = curses.color_pair(1)
        self.curses_value["GREEN"] = curses.color_pair(2)
        self.curses_value["YELLOW"] = curses.color_pair(3)
        self.curses_value["BLUE"] = curses.color_pair(4)
        self.curses_value["MAGENTA"] = curses.color_pair(5)
        self.curses_value["CYAN"] = curses.color_pair(6)
        # self.curses_value["WHITE"] = curses.color_pair(7)
        self.curses_value["DIM"] = curses.A_DIM
        self.curses_value["NORMAL"] = curses.A_NORMAL
        self.curses_value["BOLD"] = curses.A_BOLD
        self.curses_value["REVERSE"] = curses.A_REVERSE

        if not curses.has_colors():
            self.mono = True  # display in monochrome
            self.curses_value["WHITE"] = curses.color_pair(0)
            self.curses_value["RED"] = curses.color_pair(0)
            self.curses_value["GREEN"] = curses.color_pair(0)
            self.curses_value["YELLOW"] = curses.color_pair(0)
            self.curses_value["BLUE"] = curses.color_pair(0)
            self.curses_value["MAGENTA"] = curses.color_pair(0)
            self.curses_value["CYAN"] = curses.color_pair(0)

    ####################################################################
    # Color
    ####################################################################

    def get_attr(self, data_type, focus):
        #
        if focus:
            attrib_key = data_type + "_" + "focus"
        else:
            attrib_key = data_type
        value = self.attrib.get(attrib_key, "WHITE,NORMAL").split(",")
        attrib = 0
        for a in value:
            attrib |= self.curses_value[a]
        return attrib

    def get_color(self, data_type):
        color = self.attrib.get(data_type, "WHITE,NORMAL").split(",")[0]
        return color

    def get_macro_command(self):  # overriding for TUI
        """Macro parsing instead of curses getch"""
        if len(self.macro) == 0:
            keyname = ""  # end of MACRO and exit
        else:
            keyname = self.macro[:1]
            self.macro = self.macro[1:]
            if keyname == "[":
                pos = self.macro.find("]")
                if pos >= 0:
                    # look for ]
                    keyname = self.macro[:pos]
                    self.macro = self.macro[1 + pos :]
        if keyname == "":  # interactive
            try:
                keyname = get_keyname(self.stdscr.getch())
            except Exception as _:
                keyname = ""  # quit w/o saving for ^C
            keyname = self.kc.get(keyname, "IGNORE")
        logger.debug("key={}".format(keyname))
        return keyname

    def get_helptext(self):
        if self.diff_mode == 2:
            content = [
                (
                    "    Interactive Merge Editor to merge 2 DIFFerent files",
                    self.get_attr("color_white_bold", False),
                ),
                ("", self.get_attr("color_white", False)),
                (
                    "imediff processes 2 different input files using one of 5 actions:",
                    self.get_attr("color_white", False),
                ),
                (
                    " * action a: display {file_a} (older) in {color_a}".format(
                        file_a=self.file_a, color_a=self.get_color("color_a")
                    ),
                    self.get_attr("color_a", False),
                ),
                (
                    " * action b: display {file_b} (newer) in {color_b}".format(
                        file_b=self.file_b,
                        color_b=self.get_color("color_b2"),
                    ),
                    self.get_attr("color_b2", False),
                ),
                (
                    " * action d: display diff2(a,b) with marker",
                    self.get_attr("color_diff_marker", False),
                ),
                (
                    " * action e: display editor result buffer in {color_editor}".format(
                        color_editor=self.get_color("color_editor")
                    ),
                    self.get_attr("color_editor", False),
                ),
                (
                    " * action f: display wdiff2(a,b) with marker",
                    self.get_attr("color_wdiff_marker", False),
                ),
                ("", self.get_attr("color_white", False)),
            ]
            for item in """\
key commands          induced actions
{w},{x}                   write and exit
{q}                     quit without saving
{a}/{b}/{d}/{e}/{f}             set a chunk to a/b/d/e/f action
1/2/4/5/6             set a chunk to a/b/d/e/f action (alternative)
{A}/{B}/{D}/{E}/{F}             set all chunks to a/b/d/e/f action
enter                 toggle action of a chunk
{m}                     modify a chunk with editor: {edit_cmd}
{M}                     remove a editor result buffer
arrows/pgdn,{j}/pgup,{k}  move scope of the display
space,{n} /backspace,{p}  select the next/previous available chunk
tab,{N}   /shift-tab,{P}  select the next/previous unresolved chunk
{home}    /{end}          select the first/last available chunk
{zero}       /{nine}            select the first/last unresolved chunk
{question},{slash}                   show this help
{t}                     show tutorial""".format(
                w=self.rkc["w"],
                x=self.rkc["x"],
                q=self.rkc["q"],
                a=self.rkc["a"],
                b=self.rkc["b"],
                d=self.rkc["d"],
                e=self.rkc["e"],
                f=self.rkc["f"],
                A=self.rkc["A"],
                B=self.rkc["B"],
                D=self.rkc["D"],
                E=self.rkc["E"],
                F=self.rkc["F"],
                m=self.rkc["m"],
                edit_cmd=self.edit_cmd,
                M=self.rkc["M"],
                j=self.rkc["j"],
                k=self.rkc["k"],
                n=self.rkc["n"],
                p=self.rkc["p"],
                N=self.rkc["N"],
                P=self.rkc["P"],
                zero=self.rkc["0"],
                nine=self.rkc["9"],
                home=self.rkc["HOME"],
                end=self.rkc["END"],
                t=self.rkc["t"],
                question=self.rkc["?"],
                slash=self.rkc["/"],
            ).split(
                "\n"
            ):
                content.append((item, self.get_attr("color_white", False)))
        else:
            content = [
                (
                    "    Interactive Merge Editor to merge 3 DIFFerent files",
                    self.get_attr("color_white_bold", False),
                ),
                ("", self.get_attr("color_white", False)),
                (
                    "imediff processes 3 different input files using one of 7 actions:",
                    self.get_attr("color_white", False),
                ),
                (
                    " * action a: display {file_a} (MYFILE) in {color_a}".format(
                        file_a=self.file_a, color_a=self.get_color("color_a")
                    ),
                    self.get_attr("color_a", False),
                ),
                (
                    " * action b: display {file_b} (OLDER) in {color_b}".format(
                        file_b=self.file_b,
                        color_b=self.get_color("color_b3"),
                    ),
                    self.get_attr("color_b3", False),
                ),
                (
                    " * action c: display {file_c} (YOURFILE) in {color_c}".format(
                        file_c=self.file_c,
                        color_c=self.get_color("color_c"),
                    ),
                    self.get_attr("color_c", False),
                ),
                (
                    " * action d: display diff3(a,b,c) with marker",
                    self.get_attr("color_diff_marker", False),
                ),
                (
                    " * action e: display editor result buffer in {color_editor}".format(
                        color_editor=self.get_color("color_editor")
                    ),
                    self.get_attr("color_editor", False),
                ),
                (
                    " * action f: display wdiff3(a,b,c) with marker",
                    self.get_attr("color_wdiff_marker", False),
                ),
                ("", self.get_attr("color_white", False)),
            ]
            for item in """\
key commands          induced actions
{w},{x}                   write and exit
{q}                     quit without saving
{a}/{b}/{c}/{d}/{e}/{f}/{g}         set a chunk to a/b/c/d/e/f/g action
1/2/3/4/5/6/7         set a chunk to a/b/c/d/e/f/g action (alternative)
{A}/{B}/{C}/{D}/{E}/{F}/{G}         set all chunks to a/b/c/d/e/f/g action
enter                 toggle action of a chunk
{m}                     modify a chunk with editor: {edit_cmd}
{M}                     remove a editor result buffer
arrows/pgdn,{j}/pgup,{k}  move scope of the display
space,{n} /backspace,{p}  select the next/previous available chunk
tab,{N}   /shift-tab,{P}  select the next/previous unresolved chunk
{home}    /{end}          select the first/last available chunk
{zero}       /{nine}            select the first/last unresolved chunk
{question},{slash}                   show this help
{t}                     show tutorial""".format(
                w=self.rkc["w"],
                x=self.rkc["x"],
                q=self.rkc["q"],
                a=self.rkc["a"],
                b=self.rkc["b"],
                c=self.rkc["c"],
                d=self.rkc["d"],
                e=self.rkc["e"],
                f=self.rkc["f"],
                g=self.rkc["g"],
                A=self.rkc["A"],
                B=self.rkc["B"],
                C=self.rkc["C"],
                D=self.rkc["D"],
                E=self.rkc["E"],
                F=self.rkc["F"],
                G=self.rkc["G"],
                m=self.rkc["m"],
                edit_cmd=self.edit_cmd,
                M=self.rkc["M"],
                j=self.rkc["j"],
                k=self.rkc["k"],
                n=self.rkc["n"],
                p=self.rkc["p"],
                N=self.rkc["N"],
                P=self.rkc["P"],
                zero=self.rkc["0"],
                nine=self.rkc["9"],
                home=self.rkc["HOME"],
                end=self.rkc["END"],
                t=self.rkc["t"],
                question=self.rkc["?"],
                slash=self.rkc["/"],
            ).split(
                "\n"
            ):
                content.append((item, self.get_attr("color_white", False)))
        return content

    ####################################################################
    # focus off
    # action["="]       "color_merge_abc"        # diff3
    # action["="]       "color_merge_ab"         # diff2
    # action["#"]       "color_merge_ac"         # diff3
    # action["A"]       "color_merge_a"          # diff3
    # action["C"]       "color_merge_c"          # diff3
    # action["G"]       "color_merge_wdiff"      # diff3
    # focus on/off
    # action["a"]       "color_a"                # diff2, diff3
    # action["b"]       "color_b2"               # diff2
    # action["b"]       "color_b3"               # diff3
    # action["c"]       "color_c"                # diff3
    # action["e"]       "color_editor"           # diif2, diff3
    # action["d"]       "color_diff_marker"             # diff2, diff3
    # action["f"]       "color_wdiff"            # diff2, diff3
    # TBD
    #                   "color_marker"
    #                   "color_status"
    #                   "color_type"
    #                   "color_zero"

    def display_data(self, corner_virt_row, corner_virt_col):
        stdscr_row_max, stdscr_col_max = self.stdscr.getmaxyx()
        # text_data 0 ................... < stdscr_row_max - 1
        # stat_data stdscr_row_max -1 ... < stdscr_row_max
        for row_index in range(stdscr_row_max - 1):
            virt_row_index = row_index + corner_virt_row
            if virt_row_index < len(self.virt_to_chunk):
                chunk_index, chunk_subindex, action = self.virt_to_chunk[virt_row_index]
                logger.debug(
                    "virt_row_index={} row_index={} chunk_index={} chunk_subindex={} action:{}".format(
                        virt_row_index, row_index, chunk_index, chunk_subindex, action
                    )
                )
                (
                    tag,  # tag
                    i1,
                    i2,
                    j1,
                    j2,
                    k1,
                    k2,
                    _,  # action
                    merge_buffer,
                ) = self.chunk_list[chunk_index]
                #
                if self.focused_usr_chunk_index is None:
                    focus = False
                elif chunk_index == self.get_chunk_index_from_usr_chunk_list(
                    self.focused_usr_chunk_index
                ):
                    focus = True
                else:
                    focus = False
                if action == "=" and self.diff_mode == 2:
                    logger.debug(
                        "action:{} row_index={} with i1={}".format(
                            action, row_index, i1
                        )
                    )
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        [
                            (
                                self.list_a[i1],
                                corner_virt_col,
                                corner_virt_col + stdscr_col_max,
                                self.get_attr("color_merge_ab", focus),
                            )
                        ],
                        action,
                    )
                #
                elif action == "=" and self.diff_mode == 3:
                    if i1 < i2:
                        logger.debug(
                            "action:{} row_index={} with i1={}".format(
                                action, row_index, i1
                            )
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    self.list_a[i1],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_merge_abc", focus),
                                )
                            ],
                            action,
                        )
                    else:  # i1 == i2
                        logger.debug(
                            "row_index={} with i1={} i2={}".format(row_index, i1, i2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_merge_a", focus),
                                )
                            ],
                            action,
                        )
                #
                elif action == "#" and self.diff_mode == 3:
                    if i1 < i2:
                        logger.debug(
                            "action:{} row_index={} with i1={}".format(
                                action, row_index, i1
                            )
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    self.list_a[i1],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_merge_ac", focus),
                                )
                            ],
                            action,
                        )
                    else:  # i1 == i2
                        logger.debug(
                            "row_index={} with i1={} i2={}".format(row_index, i1, i2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_merge_a", focus),
                                )
                            ],
                            action,
                        )
                #
                elif action == "A":
                    if i1 < i2:
                        logger.debug(
                            "row_index={} with i1={} i2={}".format(row_index, i1, i2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    self.list_a[i1 + chunk_subindex],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_merge_a", focus),
                                )
                            ],
                            action,
                        )
                    else:  # i1 == i2
                        logger.debug(
                            "row_index={} with i1={} i2={}".format(row_index, i1, i2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_merge_a", focus),
                                )
                            ],
                            action,
                        )
                #
                elif action == "C" and self.diff_mode == 3:
                    if k1 < k2:
                        logger.debug(
                            "row_index={} with k1={} k2={}".format(row_index, k1, k2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    self.list_c[k1 + chunk_subindex],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_merge_c", focus),
                                )
                            ],
                            action,
                        )
                    else:  # i1 == i2
                        logger.debug(
                            "row_index={} with k1={} k2={}".format(row_index, k1, k2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_c", focus),
                                )
                            ],
                            action,
                        )
                #
                elif action == "G" and self.diff_mode == 3:
                    if len(merge_buffer) > 0:
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    merge_buffer[chunk_subindex],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_merge_wdiff", focus),
                                )
                            ],
                            action,
                            clrtoeol=True,
                        )
                    else:  #
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_merge_wdiff", focus),
                                )
                            ],
                            action,
                            clrtoeol=True,
                        )
                #
                elif action == "a":
                    if i1 < i2:
                        logger.debug(
                            "row_index={} with i1={} i2={}".format(row_index, i1, i2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    self.list_a[i1 + chunk_subindex],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_a", focus),
                                )
                            ],
                            action,
                        )
                    else:  # i1 == i2
                        logger.debug(
                            "row_index={} with i1={} i2={}".format(row_index, i1, i2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_a", focus),
                                )
                            ],
                            action,
                        )
                #
                elif action == "b" and self.diff_mode == 2:  #
                    if j1 < j2:
                        logger.debug(
                            "row_index={} with j1={} j2={}".format(row_index, j1, j2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    self.list_b[j1 + chunk_subindex],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_b2", focus),
                                )
                            ],
                            action,
                        )
                    else:  # i1 == i2
                        logger.debug(
                            "row_index={} with j1={} j2={}".format(row_index, j1, j2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_b2", focus),
                                )
                            ],
                            action,
                        )
                #
                elif action == "b" and self.diff_mode == 3:  #
                    if j1 < j2:
                        logger.debug(
                            "row_index={} with j1={} j2={}".format(row_index, j1, j2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    self.list_b[j1 + chunk_subindex],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_b3", focus),
                                )
                            ],
                            action,
                        )
                    else:  # i1 == i2
                        logger.debug(
                            "row_index={} with j1={} j2={}".format(row_index, j1, j2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_b3", focus),
                                )
                            ],
                            action,
                        )
                #
                elif action == "c" and self.diff_mode == 3:
                    if k1 < k2:
                        logger.debug(
                            "row_index={} with k1={} k2={}".format(row_index, k1, k2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    self.list_c[k1 + chunk_subindex],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_c", focus),
                                )
                            ],
                            action,
                        )
                    else:  # i1 == i2
                        logger.debug(
                            "row_index={} with k1={} k2={}".format(row_index, k1, k2)
                        )
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_c", focus),
                                )
                            ],
                            "c",
                        )
                #
                elif action == "e":
                    if len(merge_buffer) > 0:
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    merge_buffer[chunk_subindex],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_editor", focus),
                                )
                            ],
                            action,
                            clrtoeol=True,
                        )
                    else:  #
                        self.display_imediff_content(
                            self.stdscr,
                            row_index,
                            [
                                (
                                    "??? (" + action + ")",
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_editor", focus),
                                )
                            ],
                            action,
                            clrtoeol=True,
                        )
                #
                elif action == "d20" and self.diff_mode == 2:
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        [
                            (
                                self.ls0 % self.file_a,
                                corner_virt_col,
                                corner_virt_col + stdscr_col_max,
                                self.get_attr("color_diff_marker", focus),
                            )
                        ],
                        action,
                        clrtoeol=True,
                    )
                elif action == "d21" and self.diff_mode == 2:
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        [
                            (
                                self.ls2,
                                corner_virt_col,
                                corner_virt_col + stdscr_col_max,
                                self.get_attr("color_diff_marker", focus),
                            )
                        ],
                        action,
                        clrtoeol=True,
                    )
                elif action == "d22" and self.diff_mode == 2:
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        [
                            (
                                self.ls3 % self.file_b,
                                corner_virt_col,
                                corner_virt_col + stdscr_col_max,
                                self.get_attr("color_diff_marker", focus),
                            )
                        ],
                        action,
                        clrtoeol=True,
                    )
                #
                elif action == "d30" and self.diff_mode == 3:
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        [
                            (
                                self.ls0 % self.file_a,
                                corner_virt_col,
                                corner_virt_col + stdscr_col_max,
                                self.get_attr("color_diff_marker", focus),
                            )
                        ],
                        action,
                        clrtoeol=True,
                    )
                elif action == "d31" and self.diff_mode == 3:
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        [
                            (
                                self.ls1 % self.file_b,
                                corner_virt_col,
                                corner_virt_col + stdscr_col_max,
                                self.get_attr("color_diff_marker", focus),
                            )
                        ],
                        action,
                        clrtoeol=True,
                    )
                elif action == "d32" and self.diff_mode == 3:
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        [
                            (
                                self.ls2,
                                corner_virt_col,
                                corner_virt_col + stdscr_col_max,
                                self.get_attr("color_diff_marker", focus),
                            )
                        ],
                        action,
                        clrtoeol=True,
                    )
                elif action == "d33" and self.diff_mode == 3:
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        [
                            (
                                self.ls3 % self.file_c,
                                corner_virt_col,
                                corner_virt_col + stdscr_col_max,
                                self.get_attr("color_diff_marker", focus),
                            )
                        ],
                        action,
                        clrtoeol=True,
                    )
                #
                elif (
                    action == "f"
                    and self.diff_mode == 2
                    and i2 - i1 == 1
                    and j2 - j1 == 1
                ):
                    # logic is from get_merge_wdiff2(chunk_index)
                    """Return content for wdiff by line (2 files)"""
                    (
                        tag,
                        i1,
                        i2,
                        j1,
                        j2,
                        k1,
                        k2,
                        action,
                        merge_buffer,
                    ) = self.chunk_list[
                        chunk_index
                    ]  # chunk_list item tuple (9 param)
                    logger.debug(
                        "chunk[{}]: tag={} === a[{}:{}]/b[{}:{}]/_[{}:{}] action='{}' len(merge_buffer)={}".format(
                            chunk_index,
                            tag,
                            i1,
                            i2,
                            j1,
                            j2,
                            k1,
                            k2,
                            action,
                            len(merge_buffer),
                        ),
                    )
                    line_a = self.list_a[i1]
                    line_b = self.list_b[j1]
                    if self.isjunk:
                        isjunk = None
                    else:
                        isjunk = self.whitespace_is_junk
                    matcher_internal = SequenceMatcher(isjunk, line_a, line_b, False)
                    chunk_list_internal = matcher_internal.get_opcodes()
                    content = list()
                    for tag, i1, i2, j1, j2 in chunk_list_internal:
                        if tag == "equal":
                            # wdiff-clean
                            content.append(
                                (
                                    line_a[i1:i2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_ab", focus),
                                )
                            )
                        else:  # other tags (mark up with word separator)
                            content.append(
                                (
                                    self.ws0,
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_marker", focus),
                                )
                            )
                            content.append(
                                (
                                    line_a[i1:i2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_a", focus),
                                )
                            )
                            content.append(
                                (
                                    self.ws1,
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_marker", focus),
                                )
                            )
                            content.append(
                                (
                                    line_b[j1:j2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_b2", focus),
                                )
                            )
                            content.append(
                                (
                                    self.ws3,
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_marker", focus),
                                )
                            )
                    del chunk_list_internal
                    del matcher_internal
                    # content = basically list of attribute added text of get_merge_wdiff2(chunk_index)
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        content,
                        "f",
                        clrtoeol=True,
                    )
                elif (
                    action == "f"
                    and self.diff_mode == 3
                    and i2 - i1 == 1
                    and j2 - j1 == 1
                    and k2 - k1 == 1
                ):
                    # always non-clean merge (clean merge is in e for merge_buffer)
                    # logic is from get_merge_wdiff3(chunk_index)
                    """Return content for wdiff by line (3 files)"""
                    (
                        tag,
                        i1,
                        i2,
                        j1,
                        j2,
                        k1,
                        k2,
                        action,
                        merge_buffer,
                    ) = self.chunk_list[
                        chunk_index
                    ]  # chunk_list item tuple (9 param)
                    if i2 - i1 != 1 or j2 - j1 != 1 or k2 - k1 != 1:
                        logger.error(
                            "chunk[{}]: tag={} === a[{}:{}]/b[{}:{}]/c[{}:{}] not for wdiff3".format(
                                chunk_index, tag, i1, i2, j1, j2, k1, k2
                            ),
                        )
                        sys.exit(2)
                    logger.debug(
                        "chunk[{}]: tag={} a[{}:{}]/b[{}:{}]/c[{}:{}] action='{}' wdiff3-merge-try".format(
                            chunk_index, tag, i1, i2, j1, j2, k1, k2, action
                        ),
                    )
                    line_a = self.list_a[i1]
                    line_b = self.list_b[j1]
                    line_c = self.list_c[k1]
                    if self.isjunk:
                        isjunk = None
                    else:
                        isjunk = self.whitespace_is_junk
                    # wdiff uses SequenceMatcher
                    use_SequenceMatcher = 0
                    matcher_internal = SequenceMatcher3(
                        line_a, line_b, line_c, use_SequenceMatcher, isjunk, True
                    )
                    chunk_list_internal = matcher_internal.get_opcodes()
                    # logger.debug("wdiff3: \nwchunk_list_internal >>>>> {}".format(wchunk_list_internal))
                    content = list()
                    clean_merge = True
                    for tag, i1, i2, j1, j2, k1, k2 in chunk_list_internal:
                        if tag == "A":
                            content.append(
                                (
                                    line_a[i1:i2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_a", focus),
                                )
                            )
                        elif tag == "C":
                            content.append(
                                (
                                    line_c[k1:k2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_c", focus),
                                )
                            )
                        elif tag == "E":
                            content.append(
                                (
                                    line_c[k1:k2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_abc", focus),
                                )
                            )
                        elif tag == "e":
                            content.append(
                                (
                                    line_c[k1:k2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_ac", focus),
                                )
                            )
                        else:  # tag == "N" (mark up with word separator)
                            content.append(
                                (
                                    self.ws0,
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_marker", focus),
                                )
                            )
                            content.append(
                                (
                                    line_a[i1:i2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_a", focus),
                                )
                            )
                            content.append(
                                (
                                    self.ws1,
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_marker", focus),
                                )
                            )
                            content.append(
                                (
                                    line_b[j1:j2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_b3", focus),
                                )
                            )
                            content.append(
                                (
                                    self.ws2,
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_marker", focus),
                                )
                            )
                            content.append(
                                (
                                    line_c[k1:k2],
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_c", focus),
                                )
                            )
                            content.append(
                                (
                                    self.ws3,
                                    corner_virt_col,
                                    corner_virt_col + stdscr_col_max,
                                    self.get_attr("color_wdiff_marker", focus),
                                )
                            )
                    del matcher_internal
                    del chunk_list_internal
                    logger.debug(
                        "chunk[{}]: clean_merge={} === tag={} a[{}:{}]/b[{}:{}]/c[{}:{}] action='{}'".format(
                            chunk_index,
                            clean_merge,
                            tag,
                            i1,
                            i2,
                            j1,
                            j2,
                            k1,
                            k2,
                            action,
                        ),
                    )
                    # (clean_merge, content) = self.get_merge_wdiff3(chunk_index)
                    self.display_imediff_content(
                        self.stdscr,
                        row_index,
                        content,
                        "f",
                        clrtoeol=True,
                    )
                else:
                    pass  # but error
                    # TODO: add log error
            else:
                display_content(
                    self.stdscr,
                    row_index,
                    0,
                    [
                        ("  ", 0, 2, self.get_attr("color_white", False)),
                        (
                            "...[EOF]...",
                            0,
                            stdscr_col_max,
                            self.get_attr("color_eof", False),
                        ),
                    ],
                    clrtoeol=True,
                )
            #
        #
        # STATISTICS
        # * s_chunk_index
        # * len(chunk_list)
        # * self.focused_usr_chunk_index
        n_merge_E = 0  # = =
        n_merge_e = 0  #   #
        n_merge_n = 0  #   G
        n_merge_A = 0  #   A
        n_merge_C = 0  #   C
        n_merge_N = 0  # includes F for diff2
        n_manual_a = 0
        n_manual_b = 0
        n_manual_c = 0
        n_manual_e = 0
        n_unresolved = 0
        if self.focused_usr_chunk_index is not None:
            focused_chunk_index = self.get_chunk_index_from_usr_chunk_list(
                self.focused_usr_chunk_index
            )
            s_focused_chunk_index = s_number(focused_chunk_index)
            s_focused_usr_chunk_index = s_number(self.focused_usr_chunk_index)
            if focused_chunk_index is None:
                s_virt_row = "*"
            else:
                s_virt_row = s_number(self.chunk_to_virt[focused_chunk_index])
            for chunk_index in range(len(self.chunk_list)):
                tag = self.get_tag(chunk_index)
                action = self.get_action(chunk_index)
                if tag == "E":
                    n_merge_E += 1
                elif tag == "e":
                    n_merge_e += 1
                elif tag == "n":
                    n_merge_n += 1
                elif tag == "A":
                    n_merge_A += 1
                elif tag == "C":
                    n_merge_C += 1
                else:  # N or F
                    n_merge_N += 1
                    if action == "a":
                        n_manual_a += 1
                    elif action == "b":
                        n_manual_b += 1
                    elif action == "c":
                        n_manual_c += 1
                    elif action == "e":
                        n_manual_e += 1
                    else:
                        n_unresolved += 1
            s_merge_E = s_number(n_merge_E)
            s_merge_e = s_number(n_merge_e)
            s_merge_n = s_number(n_merge_n)
            s_merge_A = s_number(n_merge_A)
            s_merge_C = s_number(n_merge_C)
            s_merge_N = s_number(n_merge_N)
            s_manual_a = s_number(n_manual_a)
            s_manual_b = s_number(n_manual_b)
            s_manual_c = s_number(n_manual_c)
            s_manual_e = s_number(n_manual_e)
            s_unresolved = s_number(n_unresolved)
        else:
            s_focused_chunk_index = "*"
            s_focused_usr_chunk_index = "*"
            for chunk_index in range(len(self.chunk_list)):
                tag = self.get_tag(chunk_index)
                action = self.get_action(chunk_index)
                if tag == "E":
                    n_merge_E += 1
                elif tag == "e":
                    n_merge_e += 1
                elif tag == "n":
                    n_merge_n += 1
                elif tag == "A":
                    n_merge_A += 1
                elif tag == "C":
                    n_merge_C += 1
                else:  # N or F
                    n_merge_N += 1
            s_merge_E = s_number(n_merge_E)
            s_merge_e = s_number(n_merge_e)
            s_merge_n = s_number(n_merge_n)
            s_merge_A = s_number(n_merge_A)
            s_merge_C = s_number(n_merge_C)
            s_merge_N = s_number(n_merge_N)
            s_virt_row = "*"
            s_manual_a = "*"
            s_manual_b = "*"
            s_manual_c = "*"
            s_manual_e = "*"
            s_unresolved = "*"

        # len(self.usr_chunk_list)
        #
        if self.diff_mode == 2:
            status_line = "row[{}/{}] chunk[{}/{}] usr_chunk[{}/{}] / =:{} / N:{}=(a:{},b:{},e:{},u:{}) / @[{}:{}]".format(
                s_virt_row,
                len(self.virt_to_chunk),
                s_focused_chunk_index,
                len(self.chunk_list),
                s_focused_usr_chunk_index,
                len(self.usr_chunk_list),
                s_merge_E,
                s_merge_N,
                s_manual_a,
                s_manual_b,
                s_manual_e,
                s_unresolved,
                corner_virt_row,
                corner_virt_col,
            )
        else:
            status_line = "row[{}/{}] chunk[{}/{}] usr_chunk[{}/{}] / =:{},#:{},G:{},A:{},C:{} / N:{}=(a:{},b:{},c:{},e:{},u:{}) / @[{}:{}]".format(
                s_virt_row,
                len(self.virt_to_chunk),
                s_focused_chunk_index,
                len(self.chunk_list),
                s_focused_usr_chunk_index,
                len(self.usr_chunk_list),
                s_merge_E,
                s_merge_e,
                s_merge_n,
                s_merge_A,
                s_merge_C,
                s_merge_N,
                s_manual_a,
                s_manual_b,
                s_manual_c,
                s_manual_e,
                s_unresolved,
                corner_virt_row,
                corner_virt_col,
            )
        display_content(
            self.stdscr,
            stdscr_row_max - 1,
            0,
            [(status_line, 0, None, self.get_attr("color_white_reverse", False))],
            clrtoeol=True,
        )
        self.stdscr.refresh()

    ####################################################################
    def display_imediff_content(self, win, row, content, data_source, clrtoeol=True):
        # data_source = "a", "b", "c", "=", "#", "f", "d??", "G", "e", "A", "C"
        col = 0
        if data_source[:1] == "d":
            data_source_id = " "
            color = "color_status_focus"
        elif data_source in "GeAC=#":
            data_source_id = data_source
            color = "color_status"
        else:
            data_source_id = data_source
            color = "color_status_focus"
        if True:  # self.data_source_column:
            display_content(
                win,
                row,
                col,
                [
                    (
                        data_source_id,
                        0,
                        1,
                        self.get_attr(color, False),
                    ),
                    (" ", 0, 1, self.get_attr("color_white", False)),
                ],
                False,
            )
            col = None
        for line, i_b, i_e, attrib in content:
            display_content(
                win,
                row,
                col,
                [(line, i_b, i_e, attrib)],
                clrtoeol,
            )
            col = None

    ####################################################################
    # Internally used utility methods (class data set-access)
    ####################################################################

    def set_updated_merge_buffer(self, chunk_index):  # override
        logger.debug(
            "chunk[{}]: exit the curses UI and to invoke editor session".format(
                chunk_index
            )
        )
        self.stdscr.keypad(False)  # keys not-processed by curses
        curses.savetty()
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        super().set_updated_merge_buffer(chunk_index)
        curses.cbreak()
        curses.noecho()
        curses.resetty()
        self.stdscr.keypad(True)  # keys processed by curses (again)
        self.stdscr.clear()
        self.stdscr.refresh()
        logger.debug(
            "chunk[{}]: finish editor session and return to the curses UI".format(
                chunk_index
            )
        )
        return

    def display_popup_win(
        self,
        msg,
        keyname_list=["SPACE"],
        color="color_warn",
        msg_row_max=0,
        msg_col_max=0,
        margin_row=1,
        margin_col=2,
    ):
        msg_content = list()
        for line in msg.split("\n"):  # no trailing \n
            msg_content.append((line, self.get_attr(color, False)))

        keyname = self.display_content_win(
            msg_content, keyname_list, msg_row_max, msg_col_max, margin_row, margin_col
        )
        return keyname

    def display_content_win(
        self,
        msg_content,
        keyname_list=["SPACE"],
        msg_row_max=0,
        msg_col_max=0,
        margin_row=1,
        margin_col=2,
    ):
        # A pop-up centered window with specified window size and border box
        # drawing.  The text are drawn in the box and has 1 space before and after
        # for readability.
        #
        # get msg display size for virt_msg
        virt_row_max = len(msg_content)
        virt_col_max = msg_col_max
        for line, _ in msg_content:
            virt_col_max = max(virt_col_max, len(line))
        # set up centered box_win
        stdscr_row_max, stdscr_col_max = self.stdscr.getmaxyx()
        # usable msg display span
        span_col = stdscr_col_max - 2 * margin_col
        span_row = stdscr_row_max - 2 * margin_row
        logger.debug(
            "stdscr={}:{} virt={}:{} span={}:{}".format(
                stdscr_row_max,
                stdscr_col_max,
                virt_row_max,
                virt_col_max,
                span_row,
                span_col,
            )
        )
        if msg_row_max == 0 and (virt_row_max + 2 * margin_row) <= stdscr_row_max:
            msg_row_max = virt_row_max
        elif msg_row_max == 0 or msg_row_max >= span_row:
            # force reasonable msg_row_max
            msg_row_max = stdscr_row_max - 2 * margin_row
        if msg_col_max == 0 and (virt_col_max + 2 * margin_col) <= stdscr_col_max:
            msg_col_max = virt_col_max
        elif msg_col_max == 0 or msg_col_max >= span_col:
            # force reasonable msg_col_max
            msg_col_max = stdscr_col_max - 2 * margin_col
        box_margin_row = (stdscr_row_max - (msg_row_max + 2 * margin_row)) // 2
        box_margin_col = (stdscr_col_max - (msg_col_max + 2 * margin_col)) // 2
        self.box_win = self.stdscr.derwin(
            msg_row_max + 2 * margin_row,
            msg_col_max + 2 * margin_col,
            box_margin_row,
            box_margin_col,
        )
        self.box_win.clear()
        self.box_win.border()
        self.box_win.refresh()
        # set up centered msg_win
        self.msg_win = self.box_win.derwin(
            msg_row_max, msg_col_max, margin_row, margin_col
        )
        corner_popup_row = 0
        corner_popup_col = 0
        while True:
            msg_row_max, msg_col_max = self.msg_win.getmaxyx()
            corner_popup_row = max(0, corner_popup_row)
            corner_popup_col = max(0, corner_popup_col)
            self.msg_win.move(0, 0)
            for row_index in range(msg_row_max):
                virt_row_index = row_index + corner_popup_row
                if virt_row_index < len(msg_content):
                    line, attr = msg_content[virt_row_index]
                    display_content(
                        self.msg_win,
                        row_index,
                        0,
                        [(line[corner_popup_col:], 0, None, attr)],
                        clrtoeol=True,
                    )
                else:
                    display_content(
                        self.msg_win,
                        row_index,
                        0,
                        [
                            (
                                "...[EOF]...",
                                0,
                                msg_col_max,
                                self.get_attr("color_eof", False),
                            )
                        ],
                        clrtoeol=True,
                    )
            self.msg_win.refresh()
            c = self.stdscr.getch()  # c : integer (stdscr! here)
            keyname = get_keyname(c)
            if keyname in keyname_list:
                break
            # Moves in document
            elif keyname in ["0", "HOME"]:
                corner_popup_row = 0
                corner_popup_col = 0
            elif keyname in ["j", "DOWN"]:
                corner_popup_row += 1
            elif keyname in ["k", "UP"]:
                corner_popup_row -= 1
            elif keyname in ["l", "RIGHT"]:
                corner_popup_col += 8
            elif keyname in ["h", "LEFT"]:
                corner_popup_col -= 8
            elif keyname in ["n", "PAGEDOWN", "ENTER"]:
                corner_popup_row += 20
            elif keyname in ["p", "PAGEUP", "BACKSPACE"]:
                corner_popup_row -= 20
            else:
                pass
        return keyname

    ####################################################################
    # Internally used utility methods (user feedback)
    ####################################################################
    def report(self, message):  # override for TUI
        self.display_popup_win(message)
