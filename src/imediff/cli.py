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
from imediff.utils import read_lines, write_file
from imediff.lines2lib import LineMatcher
from imediff.diff3lib import SequenceMatcher3

import tempfile
import os
import sys
import io
import time
import logging

logger = logging.getLogger(__name__)


class TextData:  # Non-TUI data
    """
        Non curses class to handle diff data for 2 or 3 list of lines

        If args.diff_mode == 2, LineMatcher is used.
        * tag = 'E' or 'N' or 'F
          * action: '=" for tag == 'E'
          * action: 'd" for tag != 'E'

        If args.diff_mode == 3, SequenceMatcher3 is used.
        * tag = 'E' or 'A' or 'C' or 'e' or 'N'
        * tag = 'n' -- special TextData tag for clean wdiff3 merge

        But when -a, -b, -c (default_action == a/b/c) is specified.
        * tag = 'E' or 'N' ('N' includes A' or 'C' or 'e' or 'N')

    Here:
        * tag is static after initialization of TextData
        * action is dynamic for tag=N/F due to the user interaction
        * action =#AC are static since these are auto set only

        The main class data self.chunk_list and its associated data
        self.usr_chunk_list are shared between
          "args.diff_mode == 2" and
          "args.diff_mode == 3"
        cases to ease common handling of them under TUI.

            self.chunk_list[chunk_index] = (
                tag,             # diff opcode tag EeNACn / ENF
                i1,              # self.list_a (start)-index
                i2,              # self.list_a (end+1)-index
                j1,              # self.list_b (start)-index
                j2,              # self.list_b (end+1)-index
                k1,              # self.list_c (start)-index or 0 for diff_mode==2
                k2,              # self.list_c (end+1)-index or 0 for diff_mode==2
                action,          # data action abcdefgAC=# (self.default_action)
                merge_buffer,    # merge_buffer for editor ([])
            ) # 9-parameter tuple

        Internally, tag is extended to add 'n' which is 1-line clean wdiff3 merge.
        Merge result is automatically stored in merge_buffer.

            self.usr_chunk_list: list of user accessible chunk_index

            content = list of strings
    """

    ####################################################################
    # Externally exposed initializer method
    ####################################################################
    def __init__(self, list_a, list_b, list_c, args, confs):
        logger.debug("starting initialization ...")
        self.list_a = list_a
        self.list_b = list_b
        self.list_c = list_c
        self.init_args(args)
        self.init_config(confs)
        self.init_chunk_list()
        logger.debug("finished initialization")
        return

    def init_args(self, args):
        self.diff_mode = args.diff_mode
        self.file_a = args.file_a
        self.file_b = args.file_b
        self.file_c = args.file_c
        self.file_o = args.output
        self.sloppy = args.sloppy
        self.isjunk = args.isjunk
        self.line_rule = args.line_rule
        self.line_min = args.line_min
        self.line_max = args.line_max
        self.line_factor = args.line_factor
        self.edit_cmd = args.edit_cmd
        self.macro = args.macro
        self.default_action = args.default_action  # 2: abdf / 3:abcdfg

    def init_config(self, confs):
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
        # set up command key translation table
        # kc converts actual input command keyname to default key bindings command keyname
        # This affects terminal input only (MACRO uses system key map only)
        self.kc = dict()  # customized key code to original key code
        self.rkc = dict()  # original key chr to customized key char
        for select_key, effective_key in confs["key"].items():
            if select_key[:7] == "select_":
                typed_key = select_key[7:]
            else:
                logger.error("E: unknown select_key: {}".format(select_key))
                sys.exit(2)
            if typed_key == "":
                typed_key = " "
            if len(typed_key) > 1:
                typed_key = typed_key.upper()
            if effective_key == "":
                effective_key = " "
            self.kc[typed_key] = effective_key
            self.rkc[effective_key] = typed_key
            if (
                len(typed_key) == 1
                and len(effective_key) == 1
                and ord(typed_key) >= ord("a")
                and ord(typed_key) <= ord("z")
                and ord(effective_key) >= ord("a")
                and ord(effective_key) <= ord("z")
            ):
                cap_typed_key = typed_key.upper()
                cap_effective_key = effective_key.upper()
                self.kc[cap_typed_key] = cap_effective_key
                self.rkc[cap_effective_key] = cap_typed_key
        # Enable debug output of key remapping
        # for key, value in self.kc.items():
        #     logger.debug("kc['{}']='{}'".format(key, value))
        # for key, value in self.rkc.items():
        #     logger.debug("** rkc['{}']='{}'".format(key, value))

    def init_chunk_list(self):
        # update self.chunk_list and self.usr_chunk_list
        if self.diff_mode == 2:
            matcher_internal = LineMatcher(self.list_a, self.list_b)
            chunk_list_internal = matcher_internal.get_opcodes()
            # Set initial action to "a" or "d"
            self.chunk_list = [
                (
                    tag,
                    i1,
                    i2,
                    j1,
                    j2,
                    0,  # dummy
                    0,  # dummy
                    "",  # dummy
                    [],
                )  # chunk_list item tuple (9 param)
                for (tag, i1, i2, j1, j2) in chunk_list_internal
            ]
            # This set to "d"
            for chunk_index in range(len(self.chunk_list)):
                self.set_action(chunk_index, self.default_action)
            for chunk_index, (
                tag,
                i1,
                i2,
                j1,
                j2,
                _,
                _,
                action,
                merge_buffer,
            ) in enumerate(self.chunk_list):
                logger.debug(
                    "chunk[{}]: tag={} === a[{}:{}], b[{}:{}] === action='{}' len(merge_buffer)={}".format(
                        chunk_index,
                        tag,
                        i1,
                        i2,
                        j1,
                        j2,
                        action,
                        len(merge_buffer),
                    )
                )
        else:  # self.diff_mode == 3
            if self.default_action in ["a", "b", "c"]:
                check_same_ac = False
            else:  # "d", "f", "g"]
                check_same_ac = True
            use_LineMatcher = 1
            matcher_internal = SequenceMatcher3(
                self.list_a,
                self.list_b,
                self.list_c,
                use_LineMatcher,  # matcher
                None,  #  isjunk
                True,  # autojunk
                2,  # line_rule
                128,  # initial length to compare (upper limit)
                1,  # final   length to compare (lower limit)
                8,  # length shortening factor
                check_same_ac,  # check a vs c for tag == 'e'
            )
            chunk_list_internal = matcher_internal.get_opcodes()
            # Set initial action to "a" or "d"
            self.chunk_list = [
                (
                    tag,
                    i1,
                    i2,
                    j1,
                    j2,
                    k1,
                    k2,
                    "",  # dummy
                    [],
                )  # chunk_list item tuple (9 param)
                for (tag, i1, i2, j1, j2, k1, k2) in chunk_list_internal
            ]
            # This set to "g"
            for chunk_index in range(len(self.chunk_list)):
                self.set_action(chunk_index, self.default_action)
            for chunk_index, (
                tag,
                i1,
                i2,
                j1,
                j2,
                k1,
                k2,
                action,
                merge_buffer,
            ) in enumerate(self.chunk_list):
                logger.debug(
                    "chunk[{}]: tag={} === a[{}:{}], b[{}:{}], c[{}:{}] === action='{}' len(merge_buffer)={}".format(
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
                    )
                )
        if self.diff_mode == 2:
            self.usr_chunk_list = [
                chunk_index
                for chunk_index, (
                    tag,
                    _,
                    _,
                    _,
                    _,
                    _,
                    _,
                    _,
                    _,
                ) in enumerate(self.chunk_list)
                if tag != "E"
            ]
        else:  # diff_mode == 3
            if self.default_action in ["a", "b", "c"]:
                tag_resolved = ["E"]
            else:
                tag_resolved = ["E", "e", "n", "A", "C"]
            self.usr_chunk_list = [
                chunk_index
                for chunk_index, (
                    tag,
                    _,
                    _,
                    _,
                    _,
                    _,
                    _,
                    _,
                    _,
                ) in enumerate(self.chunk_list)
                if tag not in tag_resolved
            ]
        # debug
        for usr_chunk_index, chunk_index in enumerate(self.usr_chunk_list):
            logger.debug(
                "usr_chunk_index={} --> chunk[{}]".format(
                    usr_chunk_index,
                    chunk_index,
                )
            )
        if len(self.usr_chunk_list) == 0:
            self.focused_usr_chunk_index = None
        else:
            self.focused_usr_chunk_index = 0
        # save memory
        del chunk_list_internal
        del matcher_internal

    ####################################################################
    # Externally used main method
    ####################################################################
    def main(self):  # overridden for TUI by subclassing
        """Non-interactive driven by MACRO"""
        logger.debug("start with macro = '{}'".format(self.macro))
        # data update flag
        chunk_index = 0
        while True:
            ch = self.get_macro_command()
            logger.debug("macro ='{}' >> ch='{}')".format(self.macro, ch))
            if ch in ["QUIT", "q"]:
                # No prompt for CLI
                break
            elif ch in ["w", "x"] or len(self.macro) == 0:
                write_file(self.file_o, self.get_string_from_content_for_file())
                break
            else:
                # get user accessible chunk
                # Explicitly select chunk action
                chunk_index = self.get_chunk_index_from_usr_chunk_list(
                    self.focused_usr_chunk_index
                )
                logger.debug(
                    "usr_chunk_index = {}, chunk_index = {}, ch='{}'".format(
                        self.focused_usr_chunk_index, chunk_index, ch
                    ),
                )
                if ch in ["a", "b", "c", "d", "e", "f", "g"]:
                    self.set_action(chunk_index, ch)
                elif ch in ["1", "2", "3", "4", "5", "6", "7"]:
                    self.set_action(
                        chunk_index,
                        chr(ord(ch) - ord("1") + ord("a")),
                    )
                elif ch in ["A", "B", "C", "D", "E", "F", "G"]:
                    self.set_action_all(ch.lower())
                elif ch == "m":
                    self.set_updated_merge_buffer(chunk_index)
                elif ch == "M":
                    self.set_deleted_merge_buffer(chunk_index)
                elif ch == "n":
                    self.move_focus_to_any_resolvable_chunk_next()
                elif ch == "p":
                    self.move_focus_to_any_resolvable_chunk_prev()
                elif ch == "0":
                    self.move_focus_to_any_resolvable_chunk_home()
                elif ch == "9":
                    self.move_focus_to_any_resolvable_chunk_end()
                elif ch == "N":
                    self.move_focus_to_usr_chunk_next()
                elif ch == "P":
                    self.move_focus_to_usr_chunk_prev()
                elif ch == ")":
                    self.move_focus_to_usr_chunk_home()
                elif ch == "(":
                    self.move_focus_to_usr_chunk_end()
                else:
                    pass
        logger.debug("end")
        return

    ####################################################################
    # Internally used utility methods (class data get-access)
    ####################################################################
    def get_tag(self, chunk_index):
        (tag, _, _, _, _, _, _, _, _) = self.chunk_list[chunk_index]
        return tag

    def get_action(self, chunk_index):
        (_, _, _, _, _, _, _, action, _) = self.chunk_list[chunk_index]
        return action

    def get_merge_buffer(self, chunk_index):
        (_, _, _, _, _, _, _, _, merge_buffer) = self.chunk_list[chunk_index]
        return merge_buffer

    def get_content_for_chunk(self, chunk_index):
        """Return content as string based on action"""
        content = None
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
            "chunk[{}]: tag={} a[{}:{}]/b[{}:{}]/c[{}:{}] action='{}' len(merge_buffer)={}".format(
                chunk_index, tag, i1, i2, j1, j2, k1, k2, action, len(merge_buffer)
            ),
        )
        if action == "=" or action == "#":
            content = self.list_a[i1:i2]
        elif action == "a" or action == "A":
            content = self.list_a[i1:i2]
        elif action == "b" or action == "B":
            content = self.list_b[j1:j2]
        elif action == "c" or action == "C":
            content = self.list_c[k1:k2]
        elif action == "d":
            content = self.get_merge_diff(chunk_index)
        elif action == "e" or action == "G":
            if len(merge_buffer) != 0:
                content = merge_buffer
            else:
                logger.error(
                    "chunk[{}]: Bad action='{}' with missing edited merge_buffer".format(
                        chunk_index, action
                    )
                )
                sys.exit(2)
        elif action == "f" and self.diff_mode == 2 and i2 - i1 == 1 and j2 - j1 == 1:
            content = self.get_merge_wdiff2(chunk_index)
        elif (
            action == "f"
            and self.diff_mode == 3
            and i2 - i1 == 1
            and j2 - j1 == 1
            and k2 - k1 == 1
        ):  # wdiff
            (clean_merge, content) = self.get_merge_wdiff3(chunk_index)
            if clean_merge:
                logger.error(
                    "chunk[{}]: Bad action='f' for clean_merge".format(chunk_index)
                )
                sys.exit(2)
        elif (
            action == "g"
            and self.diff_mode == 3
            and i2 - i1 == 1
            and j2 - j1 == 1
            and k2 - k1 == 1
        ):
            (clean_merge, content) = self.get_merge_wdiff3(chunk_index)
            if not clean_merge:
                logger.error(
                    "chunk[{}]: Bad action='g' for unclean_merge".format(chunk_index)
                )
                sys.exit(2)
            if len(merge_buffer) != 0:
                content = merge_buffer
            else:
                logger.error(
                    "chunk[{}]: Bad action='g' with missing pre-loaded merge_buffer".format(
                        chunk_index
                    )
                )
                sys.exit(2)
        else:
            logger.error("chunk[{}]: Bad action='{}'".format(chunk_index, action))
            sys.exit(2)
        # content is at least [] (at least empty list)
        if content is None:
            logger.error("chunk[{}]: content can't be None".format(chunk_index))
            sys.exit(2)
        return content

    def get_chunk_index_from_usr_chunk_list(self, usr_chunk_index):
        if usr_chunk_index is None:
            chunk_index = None
        elif usr_chunk_index < 0:
            logger.debug(
                "underflow usr_chunk_index={}".format(usr_chunk_index),
            )
            chunk_index = None
        elif usr_chunk_index >= len(self.usr_chunk_list):
            logger.debug(
                "overflow usr_chunk_index={}".format(usr_chunk_index),
            )
            chunk_index = None
        elif len(self.usr_chunk_list) != 0:
            chunk_index = self.usr_chunk_list[usr_chunk_index]
            logger.debug(
                "usr_chunk_index={} >> chunk_index={}".format(
                    usr_chunk_index, chunk_index
                ),
            )
        else:
            chunk_index = None
        # always return valid index (including None)
        return chunk_index

    def get_merge_count(self, actions):
        """Count actions in user accessible chunk"""
        count = 0
        for usr_chunk_index in range(len(self.usr_chunk_list)):
            chunk_index = self.usr_chunk_list[usr_chunk_index]
            if self.get_action(chunk_index) in actions:
                count += 1
        return count

    def get_unresolved_count(self):
        """Count 'd' or 'f' action in user accessible chunk"""
        return self.get_merge_count("df")

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
            keyname = "QUIT"  # quit w/o saving for ^C
        logger.debug("key={}".format(keyname))
        return keyname

    def get_string_from_content_for_file(self):
        """Return output of all content"""
        output = ""
        for chunk_index in range(len(self.chunk_list)):
            content = self.get_content_for_chunk(chunk_index)
            output += "".join(content)
        return output

    ####################################################################
    # Internally used utility methods (class data merge get operation)
    ####################################################################
    def get_merge_diff(self, chunk_index):
        """Return content for diff by line"""
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
            "chunk[{}]: tag={} a[{}:{}]/b[{}:{}]/c[{}:{}] action='{}' len(merge_buffer)={}".format(
                chunk_index, tag, i1, i2, j1, j2, k1, k2, action, merge_buffer
            ),
        )
        # mark up for diff display
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

    def whitespace_is_junk(self, c):
        return c in " \t"

    def get_merge_wdiff2(self, chunk_index):
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
        if i2 - i1 != 1 or j2 - j1 != 1:
            logger.error(
                "chunk[{}]: tag={} a[{}:{}]/b[{}:{}] not for wdiff2".format(
                    chunk_index, tag, i1, i2, j1, j2
                ),
            )
            sys.exit(2)
        logger.debug(
            "chunk[{}]: tag={} === a[{}:{}]/b[{}:{}]/_[{}:{}] action='{}' len(merge_buffer)={}".format(
                chunk_index, tag, i1, i2, j1, j2, k1, k2, action, len(merge_buffer)
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
        line_string = ""
        for tag, i1, i2, j1, j2 in chunk_list_internal:
            if tag == "equal":
                line_string += line_a[i1:i2]
            else:  # other tags (mark up with word separator)
                line_string += self.ws0
                line_string += line_a[i1:i2]
                line_string += self.ws1
                line_string += line_b[j1:j2]
                line_string += self.ws3
        del chunk_list_internal
        del matcher_internal
        return [line_string]

    def get_merge_wdiff3(self, chunk_index):
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
            _,
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
            line_a,
            line_b,
            line_c,
            use_SequenceMatcher,  # matcher
            isjunk,  #  isjunk
            True,  # autojunk
            2,  # line_rule (NOT USED)
            128,  # initial length to compare (upper limit) (NOT USED)
            1,  # final   length to compare (lower limit) (NOT USED)
            8,  # length shortening factor (NOT USED)
            True,  # check a vs. c foe tag == 'e' (NOT USED)
        )
        chunk_list_internal = matcher_internal.get_opcodes()
        # logger.debug("wdiff3: \nwchunk_list_internal >>>>> {}".format(wchunk_list_internal))
        line_string = ""
        clean_merge = True
        for tag, i1, i2, j1, j2, k1, k2 in chunk_list_internal:
            if tag == "E" or tag == "e" or tag == "A":
                line_string += line_a[i1:i2]
            elif tag == "C":
                line_string += line_c[k1:k2]
            else:  # tag == "N" (mark up with word separator)
                clean_merge = False
                line_string += self.ws0
                line_string += line_a[i1:i2]
                line_string += self.ws1
                line_string += line_b[j1:j2]
                line_string += self.ws2
                line_string += line_c[k1:k2]
                line_string += self.ws3
        del matcher_internal
        del chunk_list_internal
        logger.debug(
            "chunk[{}]: clean_merge={} === tag={} a[{}:{}]/b[{}:{}]/c[{}:{}] action='{}'".format(
                chunk_index, clean_merge, tag, i1, i2, j1, j2, k1, k2, action
            ),
        )
        return (clean_merge, [line_string])

    ####################################################################
    # Internally used utility methods (class data set-access)
    ####################################################################
    # tag:            E e A C  n     N                       (data only)
    # action request:         (g/f)  a b c d e f g    m/M   (user input)
    # action:         = # A C  E     a b c d e f
    def set_action(self, chunk_index, action_request):
        (
            tag,
            i1,
            i2,
            j1,
            j2,
            k1,
            k2,
            action_old,
            merge_buffer,
        ) = self.chunk_list[
            chunk_index
        ]  # chunk_list item tuple (9 param)
        if self.diff_mode == 2:
            # for 2 file merge/pick
            #   incoming tag is E or N or F
            if tag == "E":
                action = "="
            # N F
            elif action_request == "a":
                action = "a"
            elif action_request == "b":
                action = "b"
            elif action_request == "f" and i2 - i1 == 1 and j2 - j1 == 1:
                action = "f"
            elif action_request == "f":
                action = "d"
            elif action_request == "d":
                action = "d"
            elif action_request == "e" and len(merge_buffer) != 0:
                action = "e"
            elif action_request == "e" and len(merge_buffer) == 0:
                logger.warning(
                    "chunk[{}]: diff_mode={} action_request='{}' len(merge_buffer)={} --> keep action_old='{}'".format(
                        chunk_index,
                        self.diff_mode,
                        action_request,
                        len(merge_buffer),
                        action_old,
                    ),
                )
                action = action_old
            else:
                logger.warning(
                    "chunk[{}]: diff_mode={} action_request='{}' len(merge_buffer)={} action_old='{}' (very odd) --> force action='d'".format(
                        chunk_index,
                        self.diff_mode,
                        action_request,
                        len(merge_buffer),
                        action_old,
                    ),
                )
                action = "d"
        else:  # self.diff_mode == 3
            # for 3 file merge
            #   incoming tag is E or A or C or N or e
            if tag == "E":
                action = "="
            elif tag == "e" and self.default_action not in ["a", "b", "c"]:
                action = "#"
            elif tag == "n" and self.default_action not in ["a", "b", "c"]:
                action = "G"
            elif tag == "A" and self.default_action not in ["a", "b", "c"]:
                action = "A"
            elif tag == "C" and self.default_action not in ["a", "b", "c"]:
                action = "C"
            elif action_request in ["a", "b", "c", "d"]:
                action = action_request
            elif action_request == "e" and len(merge_buffer) != 0:
                action = "e"
            elif action_request == "e" and len(merge_buffer) == 0:
                logger.warning(
                    "chunk[{}]: diff_mode={} action_request='{}' len(merge_buffer)={} --> keep action_old='{}'".format(
                        chunk_index,
                        self.diff_mode,
                        action_request,
                        len(merge_buffer),
                        action_old,
                    ),
                )
                action = action_old
            elif self.default_action in ["a", "b", "c"]:
                action = self.default_action
            elif (
                action_request == "f" and i2 - i1 == 1 and j2 - j1 == 1 and k2 - k1 == 1
            ):
                # all 1 line diff -> try wdiff
                (clean_merge, content) = self.get_merge_wdiff3(chunk_index)
                if clean_merge:
                    action = "G"  # clean merge
                    tag = "n"  # update
                    merge_buffer = content
                    if self.default_action == "d":
                        self.usr_chunk_list = [
                            chunk_index
                            for chunk_index, (
                                tag,
                                _,
                                _,
                                _,
                                _,
                                _,
                                _,
                                _,
                                _,
                            ) in enumerate(self.chunk_list)
                            if tag not in ["E", "e", "n", "A", "C"]
                        ]
                        # debug
                        if len(self.usr_chunk_list) == 0:
                            self.focused_usr_chunk_index = None
                            logger.debug(
                                "reindex(f) at chunk[{}] usr_chunk[*]".format(
                                    chunk_index
                                )
                            )
                        elif self.focused_usr_chunk_index == len(self.usr_chunk_list):
                            self.focused_usr_chunk_index = len(self.usr_chunk_list) - 1
                            logger.debug(
                                "reindex(f) at chunk[{}] usr_chunk[{} (avoid overflow)]".format(
                                    chunk_index, self.focused_usr_chunk_index
                                )
                            )
                        else:
                            logger.debug(
                                "reindex(f) at chunk[{}] usr_chunk[{}]".format(
                                    chunk_index, self.focused_usr_chunk_index
                                )
                            )
                else:
                    action = "f"  # non-clean merge
            elif action_request == "f":
                action = "d"  # non-clean merge
            elif (
                action_request == "g" and i2 - i1 == 1 and j2 - j1 == 1 and k2 - k1 == 1
            ):
                # all 1 line diff -> try wdiff
                (clean_merge, content) = self.get_merge_wdiff3(chunk_index)
                if clean_merge:
                    action = "G"  # clean merge
                    tag = "n"  # update
                    merge_buffer = content
                    if self.default_action == "d":
                        self.usr_chunk_list = [
                            chunk_index
                            for chunk_index, (
                                tag,
                                _,
                                _,
                                _,
                                _,
                                _,
                                _,
                                _,
                                _,
                            ) in enumerate(self.chunk_list)
                            if tag not in ["E", "e", "n", "A", "C"]
                        ]
                        # debug
                        if len(self.usr_chunk_list) == 0:
                            self.focused_usr_chunk_index = None
                            logger.debug(
                                "reindex(g) at chunk[{}] usr_chunk[*]".format(
                                    chunk_index
                                )
                            )
                        elif self.focused_usr_chunk_index == len(self.usr_chunk_list):
                            self.focused_usr_chunk_index = len(self.usr_chunk_list) - 1
                            logger.debug(
                                "reindex(g) at chunk[{}] usr_chunk[{} (avoid overflow)]".format(
                                    chunk_index, self.focused_usr_chunk_index
                                )
                            )
                        else:
                            logger.debug(
                                "reindex(g) at chunk[{}] usr_chunk[{}]".format(
                                    chunk_index, self.focused_usr_chunk_index
                                )
                            )
                else:
                    action = "d"  # non-clean merge
            elif action_request == "g":
                action = "d"  # non-clean merge
            elif action_request == "d":
                action = "d"
            else:  # N
                logger.warning(
                    "chunk[{}]: diff_mode={} action_request='{}' len(merge_buffer)={} action_old='{}' (very odd) --> force action='d'".format(
                        chunk_index,
                        self.diff_mode,
                        action_request,
                        len(merge_buffer),
                        action_old,
                    ),
                )
                action = "d"
        self.chunk_list[chunk_index] = (
            tag,
            i1,
            i2,
            j1,
            j2,
            k1,
            k2,
            action,
            merge_buffer,
        )  # chunk_list item tuple (9 param)
        return

    def set_action_all(self, action_request):
        for usr_chunk_index in range(len(self.usr_chunk_list)):
            chunk_index = self.usr_chunk_list[usr_chunk_index]
            logger.debug(
                "usr_chunk_index={} >> chunk_index={} >> action_request={}".format(
                    usr_chunk_index, chunk_index, action_request
                ),
            )
            self.set_action(chunk_index, action_request)
        return

    def set_merge_buffer(self, chunk_index, merge_buffer):
        (
            tag,
            i1,
            i2,
            j1,
            j2,
            k1,
            k2,
            action,
            _,
        ) = self.chunk_list[
            chunk_index
        ]  # chunk_list item tuple (9 param)
        self.chunk_list[chunk_index] = (
            tag,
            i1,
            i2,
            j1,
            j2,
            k1,
            k2,
            action,
            merge_buffer,
        )  # chunk_list item tuple (9 param)
        return

    def set_updated_merge_buffer(self, chunk_index):
        content = self.get_content_for_chunk(chunk_index)
        with tempfile.NamedTemporaryFile(
            mode="w",
            buffering=io.DEFAULT_BUFFER_SIZE,
            suffix=".tmp",
            prefix="imediff.",
            dir=".",
            delete=False,
        ) as fp:
            temp_file_name = fp.name
            if len(content):
                for line in content:
                    fp.write(line)
        time.sleep(0.1)  # make the change visible
        editor_ret = os.system("%s %s" % (self.edit_cmd, temp_file_name))
        time.sleep(0.1)  # make the change visible
        # time.sleep(5.0) # debug
        if editor_ret == 0:
            merge_buffer = read_lines(temp_file_name)
        else:
            merge_buffer = []  # Ignore editor errors
        os.unlink(temp_file_name)
        self.set_merge_buffer(chunk_index, merge_buffer)
        self.set_action(chunk_index, "e")
        return

    def set_deleted_merge_buffer(self, chunk_index):
        self.set_merge_buffer(chunk_index, [])
        self.set_action(chunk_index, "d")
        return

    ####################################################################
    # Internally used utility methods (active/cursor position)
    ####################################################################
    def move_focus_to_any_resolvable_chunk_next(self):
        """Jump to the next user accessible chunk"""
        if self.focused_usr_chunk_index is not None:
            usr_chunk_index_old = self.focused_usr_chunk_index
            self.focused_usr_chunk_index = min(
                self.focused_usr_chunk_index + 1,
                len(self.usr_chunk_list) - 1,
            )
            if usr_chunk_index_old == self.focused_usr_chunk_index:
                self.report("No next user accessible chunk (@end)")
        else:
            self.report("No user accessible chunk")
        return

    def move_focus_to_any_resolvable_chunk_prev(self):
        """Jump to the previous available unresolvable chunk"""
        if self.focused_usr_chunk_index is not None:
            usr_chunk_index_old = self.focused_usr_chunk_index
            self.focused_usr_chunk_index = max(self.focused_usr_chunk_index - 1, 0)
            if usr_chunk_index_old == self.focused_usr_chunk_index:
                self.report("No previous user accessible chunk (@home)")
        else:
            self.report("No user accessible chunk")
        return

    def move_focus_to_any_resolvable_chunk_home(self):
        """Jump to the first available unresolvable chunk"""
        if self.focused_usr_chunk_index is not None:
            usr_chunk_index_old = self.focused_usr_chunk_index
            self.focused_usr_chunk_index = 0
            if usr_chunk_index_old == self.focused_usr_chunk_index:
                self.report("No previous user accessible chunk (@home)")
        else:
            self.report("No user accessible chunk")
        return

    def move_focus_to_any_resolvable_chunk_end(self):
        """Jump to the last available unresolvable chunk"""
        if self.focused_usr_chunk_index is not None:
            usr_chunk_index_old = self.focused_usr_chunk_index
            self.focused_usr_chunk_index = len(self.usr_chunk_list) - 1
            if usr_chunk_index_old == self.focused_usr_chunk_index:
                self.report("No next user accessible chunk (@end)")
        else:
            self.report("No user accessible chunk")
        return

    def move_focus_to_usr_chunk_next(self):
        """Jump to the next unresolved chunk"""
        if self.focused_usr_chunk_index is not None:
            usr_chunk_index = None
            for usr_chunk_index in range(
                self.focused_usr_chunk_index + 1, len(self.usr_chunk_list)
            ):
                chunk_index = self.usr_chunk_list[usr_chunk_index]
                if self.get_action(chunk_index) in "df":
                    break
            if usr_chunk_index is not None:
                self.focused_usr_chunk_index = usr_chunk_index
            else:
                self.report("No next unselected unresolved chunk (@end)")
        else:
            self.report("No user accessible chunk")
        return

    def move_focus_to_usr_chunk_prev(self):
        """Jump to the previous unresolved chunk"""
        if self.focused_usr_chunk_index is not None:
            usr_chunk_index = None
            for usr_chunk_index in range(self.focused_usr_chunk_index - 1, -1, -1):
                chunk_index = self.usr_chunk_list[usr_chunk_index]
                if self.get_action(chunk_index) in "df":
                    break
            if usr_chunk_index is not None:
                self.focused_usr_chunk_index = usr_chunk_index
            else:
                self.report("No previous unselected unresolved chunk (@home)")
        else:
            self.report("No user accessible chunk")
        return

    def move_focus_to_usr_chunk_home(self):
        """Jump to the first unresolved chunk"""
        if self.focused_usr_chunk_index is not None:
            usr_chunk_index = None
            for usr_chunk_index in range(0, self.focused_usr_chunk_index):
                chunk_index = self.usr_chunk_list[usr_chunk_index]
                if self.get_action(chunk_index) in "df":
                    break
            if usr_chunk_index is not None:
                self.focused_usr_chunk_index = usr_chunk_index
            else:
                self.report("No previous unselected unresolved chunk (@home)")
        else:
            self.report("No user accessible chunk")
        return

    def move_focus_to_usr_chunk_end(self):
        """Jump to the last unselected unresolved chunk"""
        if self.focused_usr_chunk_index is not None:
            usr_chunk_index = None
            for usr_chunk_index in range(
                len(self.usr_chunk_list) - 1,
                self.focused_usr_chunk_index,
                -1,
            ):
                chunk_index = self.usr_chunk_list[usr_chunk_index]
                if self.get_action(chunk_index) in "df":
                    break
            if usr_chunk_index is not None:
                self.focused_usr_chunk_index = usr_chunk_index
            else:
                self.report("No next unselected unresolved chunk (@end)")
        else:
            self.report("No user accessible chunk")
        return

    ####################################################################
    # Internally used utility methods (user feedback)
    ####################################################################
    def report(self, message):  # override for TUI
        print(message, file=sys.stderr)
