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

import curses
import gettext
import locale
import sys
import tempfile
import time

from imediff.utils import *
from imediff.config import *
from imediff.diff2lib import *
from imediff.diff3lib import *
from imediff.cli import *

# Format stings
_helptext2 = _(
    """\
    Interactive Merge Editor to merge 2 DIFFerent files

imediff merges 2 different input files using 5 modes:
 * mode a: display {file_a} (older) in {color_a}
 * mode b: display {file_b} (newer) in {color_b}
 * mode d: display diff2(a,b) by line       in {color_d}
 * mode e: display editor result buffer     in {color_e}
 * mode f: display wdiff2(a,b) by character in {color_f}

key commands          induced actions
{w:c},{x:c}                   save and exit
{q:c}                     quit without saving
{a:c}/{b:c}/{d:c}/{e:c}/{f:c}             set a chunk to a/b/d/e/f mode
1/2/4/5/6             set a chunk to a/b/d/e/f mode (alternative)
{A:c}/{B:c}/{D:c}/{E:c}/{F:c}             set all chunks to a/b/d/e/f mode
enter                 toggle mode of a chunk
{m:c}                     modify a chunk with editor: {edit_cmd}
{M:c}                     remove a editor result buffer
arrows/pgdn,{j:c}/pgup,{k:c}  move scope of the display
space,{n:c} /backspace,{p:c}  select the next/previous chunk
tab,{N:c}   /shift-tab,{P:c}  select the next/previous diff chunk
home,{t:c}  /end,{z:c}        select the first/last chunk
{T:c}       /{Z:c}            select the first/last diff chunk
?,{s:c}                   show the state of the merge
{h:c}                     show this help
{H:c}                     show tutorial"""
)

_helptext3 = _(
    """\
    Interactive Merge Editor to merge 3 DIFFerent files

imediff merges 3 different input files using 7 modes:
 * mode a: display {file_a} (yours) in {color_a}
 * mode b: display {file_b} (base)  in {color_b}
 * mode c: display {file_c} (their) in {color_c}
 * mode d: display diff3(a,b,c) by line       in {color_d}
 * mode e: display editor result buffer       in {color_e}
 * mode f: display wdiff3(a,b,c) by character in {color_f}
 * mode g: set good mode from (a,b,c,e,g) if merged cleanly, or
           set mode (df) in case of conflicts

key commands          induced actions
{w:c},{x:c}                   save and exit
{q:c}                     quit without saving
{a:c}/{b:c}/{c:c}/{d:c}/{e:c}/{f:c}/{g:c}         set a chunk to a/b/c/d/e/f/g mode
1/2/3/4/5/6/7         set a chunk to a/b/c/d/e/f/g mode (alternative)
{A:c}/{B:c}/{C:c}/{D:c}/{E:c}/{F:c}/{G:c}         set all chunks to a/b/c/d/e/f/g mode
enter                 toggle mode of a chunk
{m:c}                     modify a chunk with editor: {edit_cmd}
{M:c}                     remove a editor result buffer
arrows/pgdn,{j:c}/pgup,{k:c}  move scope of the display
space,{n:c} /backspace,{p:c}  select the next/previous chunk
tab,{N:c}   /shift-tab,{P:c}  select the next/previous diff chunk
home,{t:c}  /end,{z:c}        select the first/last chunk
{T:c}       /{Z:c}            select the first/last diff chunk
?,{s:c}                   show the state of the merge
{h:c}                     show this help
{H:c}                     show tutorial"""
)

_stattext0 = _(
    """\
Chunk index   = (all files are identical)
Line index    ={row: 5d} (total ={conth: 5d})
Column offset ={col: 5d}"""
)

_stattext1 = _(
    """\
Chunk index   ={active: 5d} (total ={total: 5d}, unresolved ={unresolved: 5d})
Line index    ={row: 5d} (total ={conth: 5d})
Column offset ={col: 5d}"""
)

# Keep this under 74 char/line for better looks
_nonclean = _(
    """\
This requirement of the clean merge for 'save and exit' can be disabled by
specifying the "--sloppy" option to the imediff command.  Alternatively,
you can effectively evade this requirement by pressing "m" on all
non-clean merges to make them as the manually edited text data."""
)

# Keep this under 74 char/line for better looks
# I need this hack to avoid translation of tutorial for now. XXX FIXME XXX
nonclean = """\
This requirement of the clean merge for 'save and exit' can be disabled by
specifying the "--sloppy" option to the imediff command.  Alternatively,
you can effectively evade this requirement by pressing "m" on all
non-clean merges to make them as the manually edited text data."""


# Keep this under 76 char/line to fit this in the 80 char terminal
_tutorial = """\
Quick start:
    In this tutorial screen, use pgdn/pgup/arrows keys to read it, or
    type other keys to return to the main imediff screen.

---------------------------------------------------------------------------
    Tutorial for imediff (Interactive Merge Editor)
                        Copyright (C) 2018 Osamu Aoki <osamu@debian.org>
---------------------------------------------------------------------------

The imediff command helps you to merge 2 slightly different files with an
optional base file interactively using the in-place alternating display of
the changed content on a single-pane full screen terminal user interface.

The source of line is clearly identified by the color of the line or the
identifier character at the first column.

The advantage of this user interface is the minimal movement of the line of
sight for the user.  Other great tools such as vimdiff, xxdiff, meld and
kdiff3 require you to look at different points of display to find the exact
position of changes.  This makes imediff the most stress-free tool.  (I
realized this when I first used the original imediff2 program by Jarno
Elonen <elonen@iki.fi>.  Please note that the command name is changed from
imediff2 to imediff now.)

Other great tools for merge such as "diff3 -m ..." and "git merge ..."
operate only on the difference by line.  So even for the non-overlapping
changes, they yield the merge conflict if changes happen on the same line.

The automatic merge logic of the imediff command operates not only on the
difference by line but on the difference by character.  This is another
great feature of the imediff command. So for the non-overlapping changes, it
always yields the clean merge (mode "g").

Merge with 2 files
==================

Let's try to merge 2 almost identical files, "file_a" and "file_b", into an
output file, "file_o".  You can do this with the following.

    $ imediff -o file_o file_a file_b

This starts a full screen display of the content of the intended output
"file_o".  Initially all the different lines in "file_a" and "file_b" are
grouped in chunks and displayed in mode "d" which combines the corresponding
"file_a" and "file_b" content by line.

You can move the focused chunk to the next chunk by pressing "Space", or "n"
keys.  You can move the focused chunk to the previous chunk by pressing
"Back Space", or "p" keys.

You can set the display mode of the focused chunk with the corresponding
single key command.  Pressing "a" displays the "file_a" content.  Pressing
"b" displays the "file_b" content.

By alternating "a" and "b" keys, you can see the difference in place which
is easy on you with the constant line of sight.  (This is the same great
feature inherited from the original imediff2 program.)

You can display both the "file_a" content and the "file_b" content with 2
key commands.  Pressing "d" displays 2 blocks of lines organized somewhat
like "diff -u" (mode "d").  Pressing "f" displays intermixed 1 block of
lines organized somewhat like "wdiff" (mode "f").

Pressing "m" starts an editor to edit the focused chunk from any modes to
create a manually merged content.  Upon exiting the editor, its result is
kept in the editor result buffer.  Even after pressing "a", "b", "d", or
"f", the content of the editor result buffer can be recalled and displayed
by pressing "e".

Pressing "M" in mode "e" removes the editor result buffer.

When you press one of the upper case "A", "B", "D", "E", "F", this sets
all chunks to the corresponding lower case mode.

All parts of imediff data normally need to select "a", "b", or "e" (excluding
"d" and "f") before writing the merge result unless "--sloppy" is specified
before writing the result.  Type "w" or "x" to write the displayed content to
"file_o" and exit the imediff program.

{}

Although the imediff program is practically WYSIWYG, there is one notable
exception.  For the deleted content in mode "a" or "b", the imediff program
displays "???" in reverse mode as a placeholder.  This "???" is not included
in the output file.

Merge with 3 files
==================

Let's try to merge 2 almost identical files, "file_a" and "file_c", both of
which are based on the file, "file_b", into an output file, "file_o".  You
can do this with the following.

    $ imediff -o file_o file_a file_b file_c

This starts a full screen display of the intended merged output content
"file_o".  Unlike "Merge with 2 files", the existence of the common base
file "file_b" allows the imediff program to chose desirable chunks
automatically from the corresponding "file_a" or "file_c" contents like
"diff3 -m" or "git merge".

Actually, this imediff program does more.  This imediff program merges not
only with comparison by the line like other tools but also comparison by the
character.  This allows the clean automatic merge even when changes happen
on different positions of the same line of "file_a" and "file_c" derived
from "file_b".

Only really unresolved chunks are displayed in mode "d".  You can move the
focused chunk to the next unresolved chunk by pressing "Tab", or "N" keys.
Pressing "m" starts an editor to create a manually merged content.  You can
move the focused chunk to the previous unresolved chunk by pressing
"Shift-Tab", or "P" keys.

The key binding for "Merge with 3 files" is almost the same as that for
"Merge with 2 files".  There are 2 notable extensions.  Pressing "c"
displays the "file_c" content.  Pressing "g" causes automatic merge efforts
on a chunk for 3 files in the following order:
 * If the editor result buffer has content, mode is set to "e".
 * If a chunk is resolved cleanly, mode is set to "a", "c", or "g".
   This overrides previous manual settings such as "a", "b", or "c".
 * If a chunk isn't resolved cleanly, mode is left as mode "d" or "f".

By alternating "a" and "c" keys, you can see the difference in place.

All parts of imediff data normally need to select "a", "b", "c", "g" or "e"
(excluding "d" and "f") before writing the merge result unless "--sloppy" is
specified before writing the result.

The rests are mostly the same as "Merge with 2 files".

Terminal
========

The imediff program is compatible with any terminal window sizes.  It
supports both monochrome and color terminals.  For comfortable user
experience, terminal width of 80 characters/line or more and terminal height
of 24 lines or more are desirable.

When mode column is enabled by "-m" option or monochrome terminal is used,
the first column is used to indicate the match type of each un-selectable
matched section or display mode of each selectable unmatched chunk.
 * "=" for a un-selectable section means unchanged source files: a==b==c.
   (Under the color terminal, this is displayed in white/normal.)
 * "#" for a un-selectable section means matched and changed files: a==c and
   a!=b.  (Under the color terminal, this is displayed in white/bold.)
 * "a", "b", "c", "d", "e", "f", and "g" for selectable unmatched chunk are
   the display mode of each chunk.  (Under the color terminal, these are
   displayed in different colors.)

Customization
=============

The imediff program can customize its key binding and its color setting with
the "~/.imediff" file in the ini file format.  You can create its template
file by the "imediff -t" command.

You can disable an existing "~/.imediff" file without renaming it by
specifying a non-existing file, e.g., "BOGUS" as "imediff -C BOGUS ...".
The internal default values of the imediff program are used.

Note
====

Some keys are aliased for "Merge with 2 files" for your convenience:
 * "c" works as "d"
 * "g" works as "e"

The "diff3 -m" has an odd feature for the merge when "file_a" and "file_c"
undergo identical changes from "file_b".  This imediff program results in a
more intuitive merge result.""".format(
    nonclean
)


class TextPad(TextData):  # TUI data
    """Curses class to handle diff data for 2 or 3 lines"""

    # persistent variables: self.*
    #     stdscr: display object
    #     winh, winw: Window height and width from stdscr.getmaxyx()
    #     conth, contw: Content height and width of textpad
    #     row, col: window top left position in textpad
    #     active: index for self.actives
    # non-persistent running variables
    #     i: index as self.chunks[i]
    #     j: index as self.actives[j]
    def __init__(self, list_a, list_b, list_c, args, confs, isjunk=None):
        # Init from super class "TextData"
        super().__init__(list_a, list_b, list_c, args, confs, isjunk)
        # Init from commandline/configuration parameters
        self.mode = args.mode
        self.mono = args.mono
        if self.diff_mode == 2:
            self.color = confs["color_diff2"]
        else:
            self.color = confs["color_diff3"]
        return

    def command_loop(self, tutorial=False):  # for curses TUI (wrapper)
        self.tutorial = tutorial
        curses.wrapper(self.gui_loop)
        return

    def gui_loop(self, stdscr):  # for curses TUI (core)
        # initialize
        self.stdscr = stdscr
        color = self.color  # shorthand
        self.winh, self.winw = self.stdscr.getmaxyx()  # window size
        curses.start_color()
        self.stdscr.clear()
        self.stdscr.refresh()
        # set color pair_number as (pair_number, fg, bg)
        curses.init_pair(1, cc[color["color_a"]], cc["BLACK"])
        curses.init_pair(2, cc[color["color_b"]], cc["BLACK"])
        curses.init_pair(3, cc[color["color_c"]], cc["BLACK"])
        curses.init_pair(4, cc[color["color_d"]], cc["BLACK"])
        curses.init_pair(5, cc[color["color_e"]], cc["BLACK"])
        curses.init_pair(6, cc[color["color_f"]], cc["BLACK"])
        #
        # +6: active cc
        self.active_color = 6
        curses.init_pair(7, cc["WHITE"], cc[color["color_a"]])
        curses.init_pair(8, cc["WHITE"], cc[color["color_b"]])
        curses.init_pair(9, cc["WHITE"], cc[color["color_c"]])
        curses.init_pair(10, cc["WHITE"], cc[color["color_d"]])
        curses.init_pair(11, cc["WHITE"], cc[color["color_e"]])
        curses.init_pair(12, cc["WHITE"], cc[color["color_f"]])
        #
        # +12: deleted cc
        self.deleted_color = 12
        curses.init_pair(13, cc[color["color_a"]], cc["WHITE"])
        curses.init_pair(14, cc[color["color_b"]], cc["WHITE"])
        curses.init_pair(15, cc[color["color_c"]], cc["WHITE"])
        curses.init_pair(16, cc[color["color_d"]], cc["WHITE"])
        curses.init_pair(17, cc[color["color_e"]], cc["WHITE"])
        curses.init_pair(18, cc[color["color_f"]], cc["WHITE"])
        #
        # +6+12
        curses.init_pair(19, cc["BLACK"], cc[color["color_a"]])
        curses.init_pair(20, cc["BLACK"], cc[color["color_b"]])
        curses.init_pair(21, cc["BLACK"], cc[color["color_c"]])
        curses.init_pair(22, cc["BLACK"], cc[color["color_d"]])
        curses.init_pair(23, cc["BLACK"], cc[color["color_e"]])
        curses.init_pair(24, cc["BLACK"], cc[color["color_f"]])
        #
        if curses.has_colors() == False:
            self.mono = True
        if self.mono:
            self.mode = True
            self.color_a = "WHITE"
            self.color_b = "WHITE"
            self.color_c = "WHITE"
            self.color_d = "WHITE"
            self.color_e = "WHITE"
            self.color_f = "WHITE"
        else:
            if self.diff_mode == 2:
                self.color_a = color["color_a"]
                self.color_b = color["color_b"]
                # self.color_c = color['color_c'] # never used
                self.color_d = color["color_d"]
                self.color_e = color["color_e"]
                self.color_f = color["color_f"]
            else:
                self.color_a = color["color_a"]
                self.color_b = color["color_b"]
                self.color_c = color["color_c"]
                self.color_d = color["color_d"]
                self.color_e = color["color_e"]
                self.color_f = color["color_f"]
        # display parameters
        self.col = 0  # the column coordinate of textpad (left most=0)
        self.row = 0  # the row coordinate of textpad    (top most=0)
        self.update_textpad = True  # update textpad content
        while True:
            if self.active is not None:
                logger.debug(
                    "command loop: active = {} active_index = {} row = {} col = {}".format(
                        self.active, self.actives[self.active], self.row, self.col
                    )
                )
            else:
                logger.debug(
                    "command loop: active = ***None*** row = {} col = {}".format(
                        self.row, self.col
                    )
                )
            curses.curs_set(0)
            if self.update_textpad:
                self.new_textpad()
            # clear to remove garbage outside of textpad
            self.winh, self.winw = self.stdscr.getmaxyx()
            self.adjust_window()
            for icol in range(self.contw - self.col, self.winw):
                self.stdscr.vline(0, icol, " ", self.winh)
            ##self.stdscr.vline(0, self.contw - self.col, '@', self.winh)
            ##self.stdscr.vline(0, self.winw-1, '*', self.winh)
            # clear rows downward to remove garbage characters
            for irow in range(self.conth - self.row, self.winh):
                self.stdscr.hline(irow, 0, " ", self.winw)
            ##if (self.conth - self.row) <= self.winh -1 and (self.conth - self.row) >= 0:
            ##    self.stdscr.hline(self.conth - self.row , 0, '@', self.winw)
            if self.update_textpad or self.update_active:
                self.highlight()
            self.textpad.refresh(self.row, self.col, 0, 0, self.winh - 1, self.winw - 1)
            if self.active is not None:
                row = self.get_row(self.actives[self.active]) - self.row
                if row >= 0 and row < self.winh:
                    self.stdscr.move(row, 0)
                    curses.curs_set(1)
                else:
                    curses.curs_set(0)
            self.stdscr.refresh()
            # reset flags
            self.update_textpad = False
            self.update_active = False
            if self.tutorial:
                c = ord("H")
                self.tutorial = False
            else:
                c = self.getch_translated()
            ch = chr(c)
            if ch == "w" or ch == "x" or c == curses.KEY_EXIT or c == curses.KEY_SAVE:
                if self.sloppy or (
                    not self.sloppy and self.get_unresolved_count() == 0
                ):
                    if not self.confirm_exit or self.popup(
                        _("Do you 'save and exit'? (Press '{y:c}' to exit)").format(
                            y=self.rkc["y"]
                        )
                    ):
                        output = self.get_output()
                        write_file(self.file_o, output)
                        break
                else:
                    self.popup(
                        _(
                            "Can't 'save and exit' due to the non-clean merge. (Press '{y:c}' to continue)"
                            + "\n\n"
                            + _nonclean
                        ).format(y=self.rkc["y"])
                    )
            elif ch == "q":
                if not self.confirm_exit or self.popup(
                    _("Do you 'quit without saving'? (Press '{y:c}' to quit)").format(
                        y=self.rkc["y"]
                    )
                ):
                    self.chunks = []
                    sys.exit(1)
            elif ch == "h" or c == curses.KEY_HELP:
                # Show help screen
                self.popup(self.helptext())
            elif ch == "H":
                # Show tutorial screen
                self.popup(_tutorial)
            elif ch == "s" or ch == "?":
                # Show location
                if len(self.actives) == 0:
                    self.popup(
                        _stattext0.format(row=self.row, conth=self.conth, col=self.col)
                    )
                else:
                    self.popup(
                        _stattext1.format(
                            active=self.active,
                            total=len(self.actives),
                            unresolved=self.get_unresolved_count(),
                            row=self.row,
                            conth=self.conth,
                            col=self.col,
                        )
                    )
            # Moves in document
            elif c == curses.KEY_SR or c == curses.KEY_UP or ch == "k":
                self.row -= 1
            elif c == curses.KEY_SF or c == curses.KEY_DOWN or ch == "j":
                self.row += 1
            elif c == curses.KEY_LEFT:
                self.col -= 8
            elif c == curses.KEY_RIGHT:
                self.col += 8
            elif c == curses.KEY_PPAGE:
                self.row -= self.winh
            elif c == curses.KEY_NPAGE:
                self.row += self.winh
            # Terminal resize signal
            elif c == curses.KEY_RESIZE:
                self.winh, self.winw = self.stdscr.getmaxyx()
            else:
                pass
            # Following key-command updates TextPad
            if self.active is not None:
                # get active chunk
                # Explicitly select chunk mode
                if ch in "abdef":
                    self.set_mode(self.actives[self.active], ch)
                elif ch in "12456":
                    self.set_mode(
                        self.actives[self.active], chr(ord(ch) - ord("1") + ord("a"))
                    )
                elif ch in "ABDEF":
                    self.set_all_mode(ch.lower())
                elif ch in "cg" and self.diff_mode == 3:
                    self.set_mode(self.actives[self.active], ch)
                elif ch in "37" and self.diff_mode == 3:
                    self.set_mode(
                        self.actives[self.active], chr(ord(ch) - ord("1") + ord("a"))
                    )
                elif ch in "CG" and self.diff_mode == 3:
                    self.set_all_mode(ch.lower())
                elif c == 10 or c == curses.KEY_COMMAND:
                    mode = self.get_mode(self.actives[self.active])
                    if mode == "a":
                        self.set_mode(self.actives[self.active], "b")
                    elif mode == "b" and self.diff_mode == 2:
                        self.set_mode(self.actives[self.active], "d")
                    elif mode == "b" and self.diff_mode == 3:
                        self.set_mode(self.actives[self.active], "c")
                    elif mode == "c":
                        self.set_mode(self.actives[self.active], "d")
                    elif (
                        mode == "d"
                        and self.get_bf(self.actives[self.active]) is not None
                    ):
                        self.set_mode(self.actives[self.active], "e")
                    elif mode == "d":
                        self.set_mode(self.actives[self.active], "f")
                    elif mode == "e":
                        self.set_mode(self.actives[self.active], "f")
                    else:  # f
                        self.set_mode(self.actives[self.active], "a")
                elif ch == "m":
                    self.editor(self.actives[self.active])
                elif ch == "M" and mode == "e":
                    self.del_editor(self.actives[self.active])
                elif ch == "n" or c == curses.KEY_NEXT or ch == " ":
                    self.active_next()
                elif ch == "p" or c == curses.KEY_PREVIOUS or c == curses.KEY_BACKSPACE:
                    self.active_prev()
                elif ch == "t" or c == curses.KEY_HOME:
                    self.active_home()
                elif ch == "z" or c == curses.KEY_END:
                    self.active_end()
                elif ch == "N" or ch == "\t":
                    self.diff_next()
                elif ch == "P" or c == curses.KEY_BTAB:
                    self.diff_prev()
                elif ch == "T":
                    self.diff_home()
                elif ch == "Z":
                    self.diff_end()
                else:
                    pass
            logger.debug("command-loop")
        return

    def new_textpad(self):
        """Create new curses textpad"""
        # pre-scan content to get big enough textpad size
        conth = 0  # content height
        contw = 0  # content width
        for i in range(len(self.chunks)):
            self.set_row(i, conth)  # record textpad row position in chunk
            tag = self.get_tag(i)
            content = self.get_content(i)  # list()
            conth += len(content)
            if tag == "E" or tag == "e":
                pass
            else:
                if len(content) == 0:
                    conth += 1
            for line in content:
                contw = max(contw, console_width(line))
        if self.mode:  # Add mode column
            contw += 2  # for the tag indicator + ' '
        self.conth = conth
        self.contw = contw
        # actual textpad size slightly bigger for safety margin
        self.textpad = curses.newpad(conth + 1, max(80, contw + 1))
        for i in range(len(self.chunks)):
            self.textpad_addstr(i, False)
        if self.active is not None:
            logger.debug(
                "gui init: active={} chunk_index={} row={} col={} conth={} contw={}".format(
                    self.active,
                    self.actives[self.active],
                    self.row,
                    self.col,
                    self.conth,
                    self.contw,
                )
            )
        return

    def textpad_addstr(self, i, selected=False):
        tag = self.get_tag(i)
        mode = self.get_mode(i)
        if tag == "E":  # Same a = b = c
            decor = curses.A_DIM
            color_pair = 0
            prefix = "= "
        elif tag == "e":  # Same a = c
            decor = curses.A_BOLD
            color_pair = 0
            prefix = "# "
        elif mode == "a":  # diff2 OLD  /diff3: YOURS NEW
            decor = curses.A_BOLD
            color_pair = 1
            prefix = mode + " "
        elif mode == "b":  # diff2 NEW  /diff3: common OLD
            decor = curses.A_BOLD
            color_pair = 2
            prefix = mode + " "
        elif mode == "c":  # diff2 ---  /diff3: THEIRS NEW
            decor = curses.A_BOLD
            color_pair = 3
            prefix = mode + " "
        elif mode == "d":  # diff
            decor = curses.A_BOLD
            color_pair = 4
            prefix = mode + " "
        elif mode == "e":  # edit buffer
            decor = curses.A_BOLD
            color_pair = 5
            prefix = mode + " "
        elif mode == "f":  # wdiff
            decor = curses.A_BOLD
            color_pair = 6
            prefix = mode + " "
        else:  # 'g': # wdiff, cleanly merged
            decor = curses.A_BOLD
            decor |= curses.A_REVERSE
            color_pair = 6
            prefix = mode + " "
        row = self.get_row(i)
        content = self.get_content(i)  # list()
        # Decorative "???" for deleted lines only for display
        if len(content) == 0 and tag not in "Ee":
            content = ["???"]  # override []
            if self.mono:
                decor |= curses.A_REVERSE
            else:
                color_pair += self.deleted_color
        if selected:
            color_pair += self.active_color
            decor |= curses.A_REVERSE
        for line in content:
            # logger.debug("textpad.addstr, >>>  row={} line={} decor={} color_pair={}".format(row, line[:-1], decor , color_pair))
            if self.mono:
                self.textpad.addstr(row, 0, prefix + line, decor)
            elif self.mode:
                self.textpad.addstr(
                    row, 0, prefix + line, decor | curses.color_pair(color_pair)
                )
            else:
                self.textpad.addstr(row, 0, line, decor | curses.color_pair(color_pair))
            row += 1
        return

    def adjust_window(self):
        """Clamp window scope to have cursor within window and content"""
        # row,   col   -> index:  first column/line = 0
        # winh,  winw  -> number: first column/line = 1
        # conth, contw -> number: first column/line = 1
        context_length = 10
        self.winh, self.winw = self.stdscr.getmaxyx()
        if self.update_active and self.active is not None:
            selected_row = self.get_row(self.actives[self.active])
            if self.row >= selected_row - context_length:
                self.row = selected_row - context_length
            if self.row <= selected_row - self.winh + context_length:
                self.row = selected_row - self.winh + context_length
        # clamp cursor col/row within data
        if self.row >= self.conth - self.winh:
            self.row = self.conth - self.winh
        if self.row < 0:
            self.row = 0
        if self.col >= self.contw - 1:
            self.col = self.contw - 1
        if self.col < 0:
            self.col = 0
        logger.debug(
            "adjust_window: conth={} contw={} winh={} winw={} row={}, col={}".format(
                self.conth, self.contw, self.winh, self.winw, self.row, self.col
            )
        )
        return

    def highlight(self):
        """Update textpad by repainting active highlight"""
        if self.active is None:
            # No diff --> No highlight action
            # Avoid out of range for self.active, self.active_old
            # This makes highlight more robust and easy to use
            pass
        else:
            if self.active != self.active_old and self.active_old is not None:
                # Repaint old selection without highlighting
                self.textpad_addstr(self.actives[self.active_old], selected=False)
            self.textpad_addstr(self.actives[self.active], selected=True)
        return

    def set_mode(self, i, new_mode):
        super().set_mode(i, new_mode)
        self.update_textpad = True
        return

    def getch_translated(self):
        """Macro parsing instead of curses getch"""
        if len(self.macro):
            c = ord(self.macro[:1])
            c = self.c_translated(c)
            if c == ord(":"):
                try:
                    c = self.stdscr.getch()
                except:
                    c = ord("q")  # quit w/o saving for ^C
                c = self.c_translated(c)
            else:
                self.macro = self.macro[1:]
        else:
            c = 0  # End of MACRO
        return c

    def popup(self, text):
        self.winh, self.winw = self.stdscr.getmaxyx()
        popupw = 0
        popuph = 0
        for l in text.split("\n"):
            popupw = max(popupw, console_width(l))
            popuph += 1
        popuph = popuph + 2  # top/bottom border
        popupw = popupw + 4  # left/right (border + space)
        popuppad = curses.newpad(popuph, popupw)
        for i, line in enumerate(text.split("\n")):
            popuppad.addstr(1 + i, 2, line, curses.A_BOLD)
        popuppad.border()
        poprow = 0
        popcol = 0
        curses.curs_set(0)
        while True:
            self.winh, self.winw = self.stdscr.getmaxyx()
            popwinh = min(popuph, self.winh)
            popwinw = min(popupw, self.winw)
            self.textpad.refresh(self.row, self.col, 0, 0, self.winh - 1, self.winw - 1)
            # logger.debug("popup before >>>  poprow={} popcol={} popupw={} popwinw={}".format(poprow, popcol, popupw, popwinw))
            if poprow <= 0:
                poprow = 0
            if poprow >= popuph - popwinh:
                poprow = popuph - popwinh
            if popcol <= 0:
                popcol = 0
            if popcol >= popupw - popwinw:
                popcol = popupw - popwinw
            popuppad.refresh(
                poprow,
                popcol,
                max((self.winh - popwinh) // 2, 0),
                max((self.winw - popwinw) // 2, 0),
                min((self.winh + popwinh + 1) // 2 - 1, self.winh - 1),
                min((self.winw + popwinw + 1) // 2 - 1, self.winw - 1),
            )
            self.stdscr.refresh()
            c = self.getch_translated()
            ch = chr(c)
            # Moves in document
            if c == curses.KEY_SR or c == curses.KEY_UP or ch == "k":
                poprow -= 1
            elif c == curses.KEY_SF or c == curses.KEY_DOWN or ch == "j":
                poprow += 1
            elif c == curses.KEY_LEFT:
                popcol -= 1
            elif c == curses.KEY_RIGHT:
                popcol += 1
            elif c == curses.KEY_PPAGE:
                poprow -= popwinh
            elif c == curses.KEY_NPAGE:
                poprow += popwinh
            # Terminal resize signal
            elif c == curses.KEY_RESIZE:
                self.winh, self.winw = self.stdscr.getmaxyx()
            elif c == ord("y") or c == ord("y") - 32:
                result = True
                break
            else:
                result = False
                break
            self.stdscr.refresh()
        return result

    def editor(self, i):
        # logger.debug("Before invoking editor")
        self.stdscr.keypad(0)
        curses.savetty()
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        super().editor(i)
        curses.cbreak()
        curses.noecho()
        curses.resetty()
        self.stdscr.keypad(True)  # keys processed by curses (again)
        self.stdscr.clear()
        self.stdscr.refresh()
        # logger.debug("After invoking editor")
        return

    def helptext(self):
        if self.diff_mode == 2:
            text = _helptext2.format(
                file_a=self.file_a,
                color_a=self.color_a,
                file_b=self.file_b,
                color_b=self.color_b,
                color_d=self.color_d,
                color_e=self.color_e,
                color_f=self.color_f,
                w=self.rkc["w"],
                x=self.rkc["x"],
                q=self.rkc["q"],
                a=self.rkc["a"],
                b=self.rkc["b"],
                d=self.rkc["d"],
                e=self.rkc["e"],
                f=self.rkc["f"],
                A=self.rkc["a"] - 32,
                B=self.rkc["b"] - 32,
                D=self.rkc["d"] - 32,
                E=self.rkc["e"] - 32,
                F=self.rkc["f"] - 32,
                m=self.rkc["m"],
                edit_cmd=self.edit_cmd,
                M=self.rkc["m"] - 32,
                j=self.rkc["j"],
                k=self.rkc["k"],
                n=self.rkc["n"],
                p=self.rkc["p"],
                N=self.rkc["n"] - 32,
                P=self.rkc["p"] - 32,
                t=self.rkc["t"],
                z=self.rkc["z"],
                T=self.rkc["t"] - 32,
                Z=self.rkc["z"] - 32,
                s=self.rkc["s"],
                h=self.rkc["h"],
                H=self.rkc["h"] - 32,
            )
        else:
            text = _helptext3.format(
                file_a=self.file_a,
                color_a=self.color_a,
                file_b=self.file_b,
                color_b=self.color_b,
                file_c=self.file_c,
                color_c=self.color_c,
                color_d=self.color_d,
                color_e=self.color_e,
                color_f=self.color_f,
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
                A=self.rkc["a"] - 32,
                B=self.rkc["b"] - 32,
                C=self.rkc["c"] - 32,
                D=self.rkc["d"] - 32,
                E=self.rkc["e"] - 32,
                F=self.rkc["f"] - 32,
                G=self.rkc["g"] - 32,
                m=self.rkc["m"],
                edit_cmd=self.edit_cmd,
                M=self.rkc["m"] - 32,
                j=self.rkc["j"],
                k=self.rkc["k"],
                n=self.rkc["n"],
                p=self.rkc["p"],
                N=self.rkc["n"] - 32,
                P=self.rkc["p"] - 32,
                t=self.rkc["t"],
                z=self.rkc["z"],
                T=self.rkc["t"] - 32,
                Z=self.rkc["z"] - 32,
                s=self.rkc["s"],
                h=self.rkc["h"],
                H=self.rkc["h"] - 32,
            )
        return text
