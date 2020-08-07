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

# configuration

VERSION = "2.0"
PACKAGE = "imediff"

config_template = """\
# imediff configuration file
# Please edit right side of assignment to customize
# ini-type syntax where # starts comment
# Don't create duplicate definition
# Key side is case insensitive.

[config]
version = 2.0       # DON'T EDIT THIS.  This is for future upgrade tracking.
confirm_exit = True # Set as "False" to save and exit without pause
confirm_quit = True # Set as "False" to quit without pause
#editor = vim       # Set this to override /usr/bin/editor and $EDITOR

[key]               # key assignment for the single key command
select_a = a        # set mode a to select 'a' buffer
select_b = b        # set mode b to select 'b' buffer
select_c = c        # set mode c to select 'c' buffer (diff3)
select_d = d        # set mode d to select diff content
select_e = e        # set mode e to select editor buffer
select_f = f        # set mode f to select wdiff content
select_g = g        # set _g_ood default mode (diff3)
select_h = h        # show _h_elp screen
select_j = j        # move down display scope
select_k = k        # move up display scope
select_m = m        # start editor to _m_odify content
select_n = n        # move active selection to _n_ext
select_p = p        # move active selection to _p_revious
select_q = q        # _q_uit imediff without saving the result
select_s = s        # show merge status
select_t = t        # move active selection to home
select_x = x        # save result and _e_xit program
select_y = y        # key for "_Y_es" answer
select_z = z        # move active selection to end

[color_diff2]       # color assignment for imediff with 2 files
color_a = BLUE      # color for mode a  (OLDER)
color_b = RED       # color for mode b  (NEWER)
color_c = MAGENTA   #                   (not used with diff2)
color_d = GREEN     # color for mode d  (DIFF)
color_e = YELLOW    # color for mode e  (EDITOR)
color_f = CYAN      # color for mode f  (WDIFF)

[color_diff3]       # color assignment for imediff with 3 files
color_a = BLUE      # color for mode a  (YOURS)
color_b = MAGENTA   # color for mode b  (OLD COMMON)
color_c = RED       # color for mode c  (THEIRS)
color_d = GREEN     # color for mode d  (DIFF)
color_e = YELLOW    # color for mode e  (EDITOR)
color_f = CYAN      # color for mode f  (WDIFF)

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

cc = dict()
cc["BLUE"] = curses.COLOR_BLUE
cc["RED"] = curses.COLOR_RED
cc["YELLOW"] = curses.COLOR_YELLOW
cc["GREEN"] = curses.COLOR_GREEN
cc["CYAN"] = curses.COLOR_CYAN
cc["MAGENTA"] = curses.COLOR_MAGENTA
cc["WHITE"] = curses.COLOR_WHITE
cc["BLACK"] = curses.COLOR_BLACK

def create_template(config_file):
    if not os.path.exists(config_file):
        # logger.debug("create configuration file: {}".format(args.conf))
        try:
            with open(
                config_file, mode="w", buffering=io.DEFAULT_BUFFER_SIZE
            ) as ofp:
                ofp.write(config_template)
        except IOError:
            error_exit(
                "Error in creating configuration file: {}".format(config_file)
            )
    else:
        error_exit("Erase {} before 'imediff -t'".format(args.conf))
    return

# Generate template file: TEMPLATE.imediff
if __name__ == "__main__":
    import os
    import io
    create_template("TEMPLATE.imediff")

