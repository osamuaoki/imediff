#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
IMEDIFF - an Interactive Merge Editor for DIFF2 and DIFF3
          Curses based single-pane fullscreen tool

Copyright (C) 2003, 2004 Jarno Elonen <elonen@iki.fi>
Copyright (C) 2018-2021  Osamu Aoki <osamu@debian.org>

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
import tempfile
import os
import io
import time

from difflib import SequenceMatcher
from imediff.utils import error_exit, logger, read_lines, write_file
from imediff.lines2lib import LineMatcher
from imediff.diff3lib import SequenceMatcher3


class TextData:  # Non-TUI data
    """Non curses class to handle diff data for 2 or 3 lines"""

    #     i: index for self.opcodes
    #     j: index for self.actives (non-persistent)
    #     self.active: index for self.actives (persistent)
    def __init__(self, list_a, list_b, list_c, args, confs):
        self.diff_mode = args.diff_mode
        self.default_mode = args.default_mode
        self.file_a = args.file_a
        self.file_b = args.file_b
        self.file_c = args.file_c
        self.file_o = args.output
        self.list_a = list_a
        self.list_b = list_b
        self.list_c = list_c
        self.sloppy = args.sloppy
        self.isjunk = args.isjunk
        self.linerule = args.linerule
        self.edit_cmd = args.edit_cmd
        self.macro = args.macro
        new_mode = self.default_mode
        row = None  # used only by TUI to match index of opcodes to textpad row
        bf = None  # used only by TUI to store the editor result
        # set from confs
        if confs["config"]["confirm_exit"] != "False":
            self.confirm_exit = True
        else:
            self.confirm_exit = False
        if confs["config"]["confirm_quit"] != "False":
            self.confirm_quit = True
        else:
            self.confirm_quit = False
        self.ls0 = confs["line_separator"]["ls0"] + " %s\n"
        self.ls1 = confs["line_separator"]["ls1"] + " %s\n"
        self.ls2 = confs["line_separator"]["ls2"] + "\n"
        self.ls3 = confs["line_separator"]["ls3"] + " %s\n"
        self.ws0 = confs["word_separator"]["ws0"]
        self.ws1 = confs["word_separator"]["ws1"]
        self.ws2 = confs["word_separator"]["ws2"]
        self.ws3 = confs["word_separator"]["ws3"]
        # command key translation
        self.kc = dict()  # customized key code to original key code
        self.rkc = dict()  # original key chr to customized key chr
        for cmd_name, key_char in confs["key"].items():
            self.kc[ord(key_char[:1])] = ord(cmd_name[-1:])
            self.rkc[cmd_name[-1:]] = ord(key_char[:1])
            logger.debug(
                "[key] section: left_side='{}' right_side='{}' : self.krc[{}] = '{}'".format(
                    cmd_name, key_char, cmd_name[-1:], self.rkc[cmd_name[-1:]]
                )
            )
        # parse input data
        if self.diff_mode == 2:
            sequence = LineMatcher(list_a, list_b)
            opcodes = sequence.get_opcodes()
            k1 = k2 = None
            # Set initial mode to "a" or "d"
            self.opcodes = [
                (tag, i1, i2, j1, j2, k1, k2, "a" if tag == "E" else "d", row, bf)
                for (tag, i1, i2, j1, j2) in opcodes
            ]
            self.actives = [
                j for j, (tag, i1, i2, j1, j2) in enumerate(opcodes) if tag != "E"
            ]
        else:
            sequence = SequenceMatcher3(list_a, list_b, list_c, 1)
            opcodes = sequence.get_opcodes()
            # Set initial mode to "a" or "d"
            self.opcodes = [
                (tag, i1, i2, j1, j2, k1, k2, "a" if tag in "Ee" else "d", row, bf)
                for (tag, i1, i2, j1, j2, k1, k2) in opcodes
            ]
            self.actives = [
                j
                for j, (tag, i1, i2, j1, j2, k1, k2) in enumerate(opcodes)
                if tag not in "Ee"
            ]
        # self.actives[i] = j -> self.rev_actives[j] = i
        self.rev_actives = dict()
        for i, j in enumerate(self.actives):
            if new_mode != "d":
                self.set_mode(j, new_mode)
            self.rev_actives[j] = i
        if len(self.actives) == 0:
            self.active = None
        else:
            self.active = 0
        self.active_old = self.active
        self.update_active = True
        self.update_textpad = True
        # save memory
        del opcodes  # this is not "self.opcodes"
        del sequence
        return

    def merge_diff(self, i):
        """Return content for diff by line"""
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        logger.debug(
            "merge_wdiff: tag={} a[{}:{}]/b[{}:{}]/c[{}:{}] mode={}, row={}, bf='{}'".format(
                tag, i1, i2, j1, j2, k1, k2, mode, row, bf
            )
        )
        content = list()
        content += [self.ls0 % self.file_a]
        content += self.list_a[i1:i2]
        if self.diff_mode == 2:
            content += [self.ls2]
            content += self.list_b[j1:j2]
            content += [self.ls3 % self.file_b]
        else:  # self.diff_mode == 3
            content += [self.ls1 % self.file_b]
            content += self.list_b[j1:j2]
            content += [self.ls2]
            content += self.list_c[k1:k2]
            content += [self.ls3 % self.file_c]
        return content

    def merge_wdiff2(self, i):
        """Return content for wdiff by line (2 files)"""
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        logger.debug(
            "merge_wdiff2: tag={} a[{}:{}]/b[{}:{}]/c[{}:{}] mode={}, row={}, bf='{}'".format(
                tag, i1, i2, j1, j2, k1, k2, mode, row, bf
            )
        )
        line_a = "".join(self.list_a[i1:i2])
        line_b = "".join(self.list_b[j1:j2])
        if self.isjunk:
            isjunk = None
        else:
            isjunk = lambda x: x in " \t"
        seq = SequenceMatcher(isjunk, line_a, line_b, None)
        opcodes = seq.get_opcodes()
        line = ""
        for tag, wi1, wi2, wj1, wj2 in opcodes:
            if tag == "equal":
                line += line_a[wi1:wi2]
            else:  # other tags
                line += self.ws0
                line += line_a[wi1:wi2]
                line += self.ws1
                line += line_b[wj1:wj2]
                line += self.ws3
        content = line.splitlines(keepends=True)
        return content

    def merge_wdiff3(self, i):
        """Return content for wdiff by line (3 files)"""
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        logger.debug(
            "merge_wdiff3: tag={} a[{}:{}]/b[{}:{}]/c[{}:{}] mode={}, row={}, bf='{}'".format(
                tag, i1, i2, j1, j2, k1, k2, mode, row, bf
            )
        )
        line_a = "".join(self.list_a[i1:i2])
        line_b = "".join(self.list_b[j1:j2])
        line_c = "".join(self.list_c[k1:k2])
        if self.isjunk:
            isjunk = None
        else:
            isjunk = lambda x: x in " \t"
        wseq = SequenceMatcher3(line_a, line_b, line_c, 0, isjunk, True)
        wopcodes = wseq.get_opcodes()
        # logger.debug("wdiff3: \nwopcodesc >>>>> {}".format(wopcodes))
        line = ""
        clean_merge = True
        for tag, wi1, wi2, wj1, wj2, wk1, wk2 in wopcodes:
            if tag == "E" or tag == "e" or tag == "A":
                line += line_a[wi1:wi2]
            elif tag == "C":
                line += line_c[wk1:wk2]
            else:  # tag == "N"
                clean_merge = False
                line += self.ws0
                line += line_a[wi1:wi2]
                line += self.ws1
                line += line_b[wj1:wj2]
                line += self.ws2
                line += line_c[wk1:wk2]
                line += self.ws3
        content = line.splitlines(keepends=True)
        return (clean_merge, content)

    def get_tag(self, i):
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        return tag

    def get_mode(self, i):
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        return mode

    def get_row(self, i):
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        return row

    def get_bf(self, i):
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        return bf

    def get_content(self, i):
        """Return content based on mode"""
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        if tag == "E" or tag == "e":
            content = self.list_a[i1:i2]
        elif mode == "a":
            content = self.list_a[i1:i2]
        elif mode == "b":
            content = self.list_b[j1:j2]
        elif mode == "c":
            content = self.list_c[k1:k2]
        elif mode == "d":
            content = self.merge_diff(i)
        elif mode == "e":
            if bf is not None:
                content = bf
            else:
                error_exit("Bad mode='e' with missing edited buffer text\n")
        elif mode == "f":
            if self.diff_mode == 2:
                content = self.merge_wdiff2(i)
            else:  # self.diff_mode == 3
                (clean_merge, content) = self.merge_wdiff3(i)
        elif mode == "g":
            if self.diff_mode == 2:
                content = self.merge_diff(i)
            else:  # self.diff_mode == 3
                (clean_merge, content) = self.merge_wdiff3(i)
        else:
            error_exit("Bad mode='{}'\n".format(mode))
        # content is at least [] (at least empty list)
        if content is None:
            error_exit("content can't be None")
        return content

    def set_mode(self, i, new_mode):
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        if new_mode in "abd":
            mode = new_mode
        elif self.diff_mode == 2:  # mode is always in "abdef"
            if new_mode == "c":
                mode = "d"  # hidden alias
            elif new_mode == "f":
                mode = "f"
            else:  # for new_mode in "eg"
                if bf is not None:
                    mode = "e"
                else:  #  for mode in "abdef"
                    pass
        else:  # self.diff_mode == 3
            if new_mode == "c":
                mode = "c"
            elif new_mode == "f":
                (clean_merge, content) = self.merge_wdiff3(i)
                if clean_merge:
                    mode = "g"
                else:
                    mode = "f"
            elif new_mode == "e":
                if bf is not None:
                    mode = "e"
                else:  # for mode in "abcdefg"
                    pass
            else:  # new_mode == "g":
                if bf is not None:
                    mode = "e"
                elif tag == "A":
                    mode = "a"
                elif tag == "C":
                    mode = "c"
                elif mode in "abceg":
                    pass
                else:  # for mode in "df" and tag == "N"
                    (clean_merge, content) = self.merge_wdiff3(i)
                    if clean_merge:
                        mode = "g"
                    else:
                        pass  # mode to "d" or "f"
        self.opcodes[i] = (tag, i1, i2, j1, j2, k1, k2, mode, row, bf)
        self.update_textpad = True
        return

    def set_all_mode(self, new_mode):
        for i in range(len(self.opcodes)):
            logger.debug("set_all_mode: i={} {}".format(i, new_mode))
            self.set_mode(i, new_mode)
        return

    def set_row(self, i, new_row):  # used by TUI
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        # row is passed by value but chunk is passed by reference !
        self.opcodes[i] = (tag, i1, i2, j1, j2, k1, k2, mode, new_row, bf)
        return

    def set_bf(self, i, new_bf):
        (tag, i1, i2, j1, j2, k1, k2, mode, row, bf) = self.opcodes[i]
        self.opcodes[i] = (tag, i1, i2, j1, j2, k1, k2, mode, row, new_bf)
        return

    def editor(self, i):
        content = self.get_content(i)
        linebuf = self.ext_editor(content)
        self.set_bf(i, linebuf)
        self.set_mode(i, "e")
        return

    def del_editor(self, i):
        self.set_bf(i, None)
        self.set_mode(i, "d")
        return

    def ext_editor(self, content):
        with tempfile.NamedTemporaryFile(
            mode="w",
            buffering=io.DEFAULT_BUFFER_SIZE,
            suffix=".tmp",
            prefix="imediff.",
            dir=".",
            delete=False,
        ) as fp:
            tmpfname = fp.name
            if len(content):
                for line in content:
                    fp.write(line)
        time.sleep(0.1)  # make the change visible
        editor_ret = os.system("%s %s" % (self.edit_cmd, tmpfname))
        time.sleep(0.1)  # make the change visible
        # time.sleep(5.0) # debug
        if editor_ret == 0:
            linebuf = read_lines(tmpfname)
        else:
            linebuf = [""]  # Ignore editor errors
        os.unlink(tmpfname)
        return linebuf

    def get_output(self):
        """Return output of all content"""
        output = ""
        for i in range(len(self.opcodes)):
            content = self.get_content(i)
            output += "".join(content)
        return output

    def active_next(self):
        """Jump to the next active chunk"""
        self.active_old = self.active
        if self.active is not None:
            self.active = min(self.active + 1, len(self.actives) - 1)
        if self.active_old != self.active:
            self.update_active = True
        else:
            self.row += 1
        return

    def active_prev(self):
        """Jump to the previous active chunk"""
        self.active_old = self.active
        if self.active is not None:
            self.active = max(self.active - 1, 0)
        if self.active_old != self.active:
            self.update_active = True
        return

    def active_home(self):
        """Jump to the first active chunk"""
        self.active_old = self.active
        if self.active is not None:
            self.active = 0
        if self.active_old != self.active:
            self.update_active = True
        return

    def active_end(self):
        """Jump to the last active chunk"""
        self.active_old = self.active
        if self.active is not None:
            self.active = len(self.actives) - 1
        if self.active_old != self.active:
            self.update_active = True
        else:
            self.row += 1
        return

    def get_unresolved_count(self):
        """Count 'd' or 'f' mode in active chunk"""
        count = 0
        for j, i in enumerate(self.actives):
            if self.get_mode(i) in "df":
                count += 1
        return count

    def diff_next(self):
        """Jump to the next diff chunk"""
        self.active_old = self.active
        active = None
        for j in range(self.active + 1, len(self.actives)):
            i = self.actives[j]
            if self.get_mode(i) in "df":
                active = j
                break
        if active is not None:
            self.active = active
        if self.active_old != self.active:
            self.update_active = True
        else:
            self.row += 1
        return

    def diff_prev(self):
        """Jump to the previous diff chunk"""
        self.active_old = self.active
        active = None
        for j in range(self.active - 1, -1, -1):
            i = self.actives[j]
            if self.get_mode(i) in "df":
                active = j
                break
        if active is not None:
            self.active = active
        if self.active_old != self.active:
            self.update_active = True
        return

    def diff_home(self):
        """Jump to the first diff chunk"""
        self.active_old = self.active
        active = None
        for j in range(0, self.active):
            i = self.actives[j]
            if self.get_mode(i) in "df":
                active = j
                break
        if active is not None:
            self.active = active
        if self.active_old != self.active:
            self.update_active = True
        return

    def diff_end(self):
        """Jump to the last diff chunk"""
        self.active_old = self.active
        active = None
        for j in range(len(self.actives) - 1, self.active, -1):
            i = self.actives[j]
            if self.get_mode(i) in "df":
                active = j
                break
        if active is not None:
            self.active = active
        if self.active_old != self.active:
            self.update_active = True
        else:
            self.row += 1
        return

    def c_translated(self, c):
        """translate keys in (' '...'~') according to ~/.imediff"""
        if c >= ord("A") and c <= ord("Z"):
            # special handling of upper case letters
            if c + 32 in list(self.kc.keys()):
                c = self.kc[c + 32] - 32
            logger.debug("c_translated chr = '{}'".format(chr(c)))
        elif c >= ord(" ") and c <= ord("~"):
            if c in list(self.kc.keys()):
                c = self.kc[c]
            logger.debug("c_translated chr = '{}'".format(chr(c)))
        else:
            logger.debug("c_translated num = '{}'".format(c))
        return c

    def getch_translated(self):  # overridden for TUI by subclassing
        """Macro parsing instead of curses getch"""
        if len(self.macro):
            c = ord(self.macro[:1])
            c = self.c_translated(c)
            self.macro = self.macro[1:]
        else:
            c = 0  # End of MACRO
        return c

    def command_loop(self):  # overridden for TUI by subclassing
        """Non-interactive driven by MACRO"""
        logger.debug("command-loop start - macro")
        while True:
            # reset flags
            self.update_textpad = False  # TUI
            self.update_active = False
            c = self.getch_translated()
            if c > ord(" ") and c < 127:
                ch = chr(c)
            else:
                ch = " "

            if c == 0 or ch == "w" or ch == "x":
                output = self.get_output()
                write_file(self.file_o, output)
                break
            elif ch == "q":
                # No prompt for CLI
                break
            if self.active is not None:
                # get active chunk
                # Explicitly select chunk mode
                if ch in "abcdefg":
                    self.set_mode(self.actives[self.active], ch)
                elif ch in "1234567":
                    self.set_mode(
                        self.actives[self.active], chr(ord(ch) - ord("1") + ord("a"))
                    )
                elif ch in "ABCDEFG":
                    self.set_all_mode(ch.lower())
                elif ch == "m":
                    self.editor(self.actives[self.active])
                elif ch == "M":
                    self.del_editor(self.actives[self.active])
                elif ch == "n":
                    self.active_next()
                elif ch == "p":
                    self.active_prev()
                elif ch == "t":
                    self.active_home()
                elif ch == "z":
                    self.active_end()
                elif ch == "N":
                    self.diff_next()
                elif ch == "P":
                    self.diff_prev()
                elif ch == "T":
                    self.diff_home()
                elif ch == "Z":
                    self.diff_end()
                else:
                    pass
            else:
                pass
        logger.debug("command-loop")
        return
