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

import os
import sys
import io
import logging

logger = logging.getLogger(__name__)

# Update version below only when configuration API changes

config_template = """\
# imediff configuration file
# Please edit right side of assignment to customize
# ini-type syntax where # starts comment
# Don't create duplicate definition
# Key side is case insensitive.

[config]
version = 3.0       # DON'T EDIT THIS.  This is for future upgrade tracking.
confirm_exit = True # Set as "False" to save and exit without pause
confirm_quit = True # Set as "False" to quit without pause
#editor = vim       # Set this to override /usr/bin/editor and $EDITOR

# key remapping is used only for TUI user input.  MACRO need to use the
# original bindings.
[key]               # action invoked by the selected key
select_a = a        # set mode a to select 'a' buffer
select_b = b        # set mode b to select 'b' buffer
select_c = c        # set mode c to select 'c' buffer (diff3)
select_d = d        # set mode d to select diff content if possible
select_e = e        # set mode e to select editor buffer if possible
select_f = f        # set mode f to select wdiff content if possible
select_g = g        # set good merge (diff3/wdiff3) if possible
select_h = h        # move left for the display scope
select_i = i
select_j = j        # move down for the display scope
select_k = k        # move up for the display scope
select_l = l        # move right for the display scope
select_m = m        # start editor to modify content / M reset
select_n = n        # move active selection to _n_ext
select_o = o
select_p = p        # move active selection to _p_revious
select_q = q        # _q_uit imediff without saving the result
select_r = r
select_s = s
select_t = t        # display tutorial
select_u = u
select_v = v
select_w = w        # _w_rite result and e_x_it program
select_x = x        # _w_rite result and e_x_it program
select_y = y        # key for "_Y_es" answer
select_z = z
select_SPACE = SPACE
select_! = !
select_" = "
select_HASH = HASH
select_$ = $
select_PERCENT = PERCENT
select_& = &
select_' = '
select_( = (
select_) = )
select_* = *
select_+ = +
select_, = ,
select_- = -
select_. = .
select_/ = /
select_0 = 0
select_1 = 1
select_2 = 2
select_3 = 3
select_4 = 4
select_5 = 5
select_6 = 6
select_7 = 7
select_8 = 8
select_9 = 9
select_COLON = COLON
select_; = ;
select_< = >
select_EQUAL = EQUAL
select_> = >
select_? = ?
select_@ = @
select_LBRACKET = LBRACKET        # MACRO block start
select_BACKSLASH = BACKSLASH
select_RBRACKET = RBRACKET        # MACRO block end
select_^ = ^
select__ = _
select_` = `
select_{ = {
select_| = |
select_} = }
select_~ = ~
select_DEL = DEL
select_TAB = TAB
select_BTAB = BTAB
select_ENTER = ENTER
select_UP = UP
select_DOWN = DOWN
select_LEFT = LEFT
select_RIGHT = RIGHT
select_INSERT = INSERT
select_DELETE = DELETE
select_HOME = HOME
select_END = END
select_PAGEUP = PAGEUP
select_PAGEDOWN = PAGEDOWN
select_BACKSPACE = BACKSPACE
select_F1 = F1
select_F2 = F2
select_F3 = F3
select_F4 = F4
select_F5 = F5
select_F6 = F6
select_F7 = F7
select_F8 = F8
select_F9 = F9
select_F10 = F10
select_F11 = F11
select_F12 = F11
#          = ^--------- customized key setting
# ^--------- reference key setting
# Upper case ASCII-keys are mapped following lower case keys

[attrib]
color_merge_ab           = WHITE,NORMAL         # diff2  =
color_merge_abc          = WHITE,NORMAL         # diff3  =
color_merge_ac           = WHITE,NORMAL         # diff 3 #
color_merge_a            = GREEN,NORMAL         # diff 3 A
color_merge_c            = YELLOW,NORMAL        # diff 3 C
color_merge_wdiff        = WHITE,NORMAL         # diff 3 G wdiff
color_a                  = GREEN,BOLD           # diff23 a
color_a_focus            = GREEN,BOLD,REVERSE
color_b2                 = YELLOW,BOLD          # diff2  b (wdiff2)
color_b2_focus           = YELLOW,BOLD,REVERSE
color_b3                 = MAGENTA,BOLD         # diff 3 b (wdiff3)
color_b3_focus           = MAGENTA,BOLD,REVERSE
color_c                  = YELLOW,BOLD          # diff 3 c
color_c_focus            = YELLOW,BOLD,REVERSE
color_editor             = CYAN,BOLD            # editor-buffer-line
color_editor_focus       = CYAN,BOLD,REVERSE
color_diff_marker        = BLUE,NORMAL          # marker-diff-line
color_diff_marker_focus  = BLUE,NORMAL,REVERSE
color_wdiff_abc          = WHITE,NORMAL         # wdiff3
color_wdiff_abc_focus    = WHITE,BOLD,REVERSE
color_wdiff_ac           = WHITE,DIM            # wdiff3
color_wdiff_ac_focus     = WHITE,BOLD,REVERSE
color_wdiff_ab           = WHITE,NORMAL         # wdiff2
color_wdiff_ab_focus     = WHITE,BOLD,REVERSE
color_wdiff_marker       = BLUE,NORMAL
color_wdiff_marker_focus = BLUE,NORMAL,REVERSE

color_status             = WHITE,NORMAL
color_status_focus       = WHITE,BOLD,REVERSE
color_white_bold         = WHITE,BOLD
color_white              = WHITE,NORMAL
color_white_reverse      = WHITE,BOLD,REVERSE
color_warn               = RED,BOLD
color_eof                = BLUE,DIM,REVERSE
color_mono               = WHITE,NORMAL


[line_separator]    # diff output formatting strings
                    # diff2 uses       ls0,      ls2, ls3
                    # diff3 uses       ls0, ls1, ls2, ls3
                    # File name  added ls0, ls1,      ls3
ls0 = <<<<<<<
ls1 = |||||||
ls2 = =======
ls3 = >>>>>>>

[word_separator]    # wdiff output formatting strings
                    # wdiff2 uses       ws0, ws1,      ws3
                    # wdiff3 uses       ws0, ws1, ws2, ws3
ws0 = {
ws1 = |
ws2 = |
ws3 = }
# alternative1 for UTF-8 terminal
#ws0 = «🅐
#ws1 = 🅑
#ws2 = 🅒
#ws3 = »
# alternative2 for UTF-8 terminal
#ws0 = «
#ws1 = ╪
#ws2 = ╫
#ws3 = »
"""


def create_template(conf):
    config_file = os.path.expanduser(conf)
    if not os.path.exists(config_file):
        logger.debug("create configuration file: {}".format(conf))
        try:
            with open(config_file, mode="w", buffering=io.DEFAULT_BUFFER_SIZE) as ofp:
                ofp.write(config_template)
        except IOError:
            logger.error("Error in creating configuration file: {}".format(conf))
            sys.exit(2)
    else:
        logger.error("Erase {} before 'imediff -t'".format(conf))
        sys.exit(2)
    return


# Generate template file: TEMPLATE.imediff
if __name__ == "__main__":
    create_template("TEMPLATE.imediff")
