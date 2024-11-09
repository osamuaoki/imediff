#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

import curses
import sys
import io
import logging

logger = logging.getLogger(__name__)

help_msg = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF\n" * 30 + "ZZZZ"

text_example = """\
What IS lOREM Ipsum? lOREM Ipsum IS simply dummy text of the printing and
typesetting industry. lOREM Ipsum has been the industry's standard dummy text
ever since the 1500s, when an unknown printer took a galley of type and
scrambled it to make a type specimen book. It has survived not only five
centuries, but also the leap into electronic typesetting, remaining essentially
unchanged. It was popularISed in the 1960s with the release of Letraset sheets
containing lOREM Ipsum passages, and more recently with desktop publIShing
software like Aldus PageMaker including versions of lOREM Ipsum.

EOF_LINE
"""


class TUI:
    """Curses class to handle text"""

    def __init__(self, text):
        self.virt_lines = text.splitlines(keepends=True)
        return

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
    #     curses terminal screen absolute coordinate as (y,x):
    #     +----------------------------------------------------------+
    #     | (0,0) top-left corner                    (term_col_max-1)|
    #     |  +--> x-axis                                             |
    #     |  |                                                       |
    #     |  |                 TEXT DATA DISPLAY                     |
    #     |  V y-axis                                                |
    #     |                                                          |
    #     |                                                          |
    #     | (term_row_max-2,0)        (term_row_max-2,term_col_max-1)|
    #     +----------------------------------------------------------+
    #     | (term_row_max-1,0) STATUS (term_row_max-1,term_col_max-1)|
    #     +----------------------------------------------------------+
    #
    # Here:
    #     * term_row_max, term_col_max = stdscr.getmaxyx()
    #
    # Internal data:
    #   * TUI
    #     * virt_to_row[virt_row] = (chunk_index, chunk_subindex)
    # Terminal size: 80 col x 24 row required
    #
    ####################################################################

    def main(self):  # for curses TUI (wrapper)
        """CURSES TUI program"""
        logger.debug("tui-main start")
        curses.wrapper(self.tui_loop)
        logger.debug("tui-main end")
        return

    def tui_loop(self, stdscr):  # for curses TUI (core)
        """wrapped CURSES TUI loop"""
        self.stdscr = stdscr
        curses.curs_set(0)  # cursor off
        # create text_win and status_win
        self.init_curses()
        # initial display parameters
        # flag_update_text_win_corner = True
        self.text_win_corner_virt_row = 0
        while True:
            # enforce sanity
            self.text_win_corner_virt_row = max(0, self.text_win_corner_virt_row)
            self.display_text_win()
            c = self.stdscr.getch()  # return integer
            ch = chr(c)
            if ch == "q":
                logger.debug("quit without write to a file: imediff.out")
                break
            # elif ch == "h" or c == curses.KEY_HELP:
            # Show help screen
            # self.display_popup_win(self.get_helptext())
            # Moves in document
            elif c == curses.KEY_HOME or ch == "0":
                self.text_win_corner_virt_row = 0
            elif c == curses.KEY_SF or c == curses.KEY_DOWN or ch == "j":
                self.text_win_corner_virt_row += 1
            elif c == curses.KEY_SR or c == curses.KEY_UP or ch == "k":
                self.text_win_corner_virt_row -= 1
            elif c == curses.KEY_NPAGE or ch == ";":
                self.text_win_corner_virt_row += 20
            elif c == curses.KEY_PPAGE or ch == "'":
                self.text_win_corner_virt_row -= 20
            # Terminal resize signal
            else:
                pass
            logger.debug("gui-command-loop")
        return

    ####################################################################
    def init_curses(self):
        # curses.start_color() # wrapper takes care
        logger.debug(
            "COLORS={}, COLOR_PAIRS={}".format(curses.COLORS, curses.COLOR_PAIRS)
        )
        stdscr_row_max, stdscr_col_max = self.stdscr.getmaxyx()
        logger.debug(
            "stdscr_row_max={}, stdscr_col_max={}".format(
                stdscr_row_max, stdscr_col_max
            )
        )
        if stdscr_row_max < 20 or stdscr_col_max < 60:
            logger.error(
                "E: terminal size too small: row={}:col={}".format(
                    stdscr_row_max, stdscr_col_max
                )
            )
            sys.exit(2)
        self.stdscr.clear()
        self.stdscr.refresh()
        self.text_win = curses.newwin(stdscr_row_max - 1, stdscr_col_max)
        self.status_win = curses.newwin(1, stdscr_col_max, stdscr_row_max - 1, 0)
        # set up color
        # curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(11, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(12, curses.COLOR_YELLOW, curses.COLOR_WHITE)
        curses.init_pair(13, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(14, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
        curses.init_pair(15, curses.COLOR_CYAN, curses.COLOR_WHITE)
        curses.init_pair(16, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.content = [
            (
                curses.color_pair(0),
                "curses.init_pair(0_ -- default NORMAL >>>>>>>>>>>>>>>",
            ),
            (
                curses.color_pair(1),
                "curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(2),
                "curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(3),
                "curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(4),
                "curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(5),
                "curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(6),
                "curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(7),
                "curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(8),
                "curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK) PREV=B_on_B, NEXT=W-on_W",
            ),
            (
                curses.color_pair(9),
                "curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(10),
                "curses.init_pair(10, curses.COLOR_RED, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(11),
                "curses.init_pair(11, curses.COLOR_GREEN, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(12),
                "curses.init_pair(12, curses.COLOR_YELLOW, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(13),
                "curses.init_pair(13, curses.COLOR_BLUE, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(14),
                "curses.init_pair(14, curses.COLOR_MAGENTA, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(15),
                "curses.init_pair(15, curses.COLOR_CYAN, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(16),
                "curses.init_pair(16, curses.COLOR_BLACK, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(0) | curses.A_REVERSE,
                "curses.init_pair(0_ -- default REVERSE >>>>>>>>>>>>>>>",
            ),
            (
                curses.color_pair(1) | curses.A_REVERSE,
                "curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(2) | curses.A_REVERSE,
                "curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(3) | curses.A_REVERSE,
                "curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(4) | curses.A_REVERSE,
                "curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(5) | curses.A_REVERSE,
                "curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(6) | curses.A_REVERSE,
                "curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(7) | curses.A_REVERSE,
                "curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(8) | curses.A_REVERSE,
                "curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK) PREV=B_on_B, NEXT=W-on_W",
            ),
            (
                curses.color_pair(9) | curses.A_REVERSE,
                "curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(10) | curses.A_REVERSE,
                "curses.init_pair(10, curses.COLOR_RED, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(11) | curses.A_REVERSE,
                "curses.init_pair(11, curses.COLOR_GREEN, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(12) | curses.A_REVERSE,
                "curses.init_pair(12, curses.COLOR_YELLOW, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(13) | curses.A_REVERSE,
                "curses.init_pair(13, curses.COLOR_BLUE, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(14) | curses.A_REVERSE,
                "curses.init_pair(14, curses.COLOR_MAGENTA, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(15) | curses.A_REVERSE,
                "curses.init_pair(15, curses.COLOR_CYAN, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(16) | curses.A_REVERSE,
                "curses.init_pair(16, curses.COLOR_BLACK, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(0) | curses.A_STANDOUT,
                "curses.init_pair(0_ -- default STANDOUT >>>>>>>>>>>>>>>",
            ),
            (
                curses.color_pair(1) | curses.A_STANDOUT,
                "curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(2) | curses.A_STANDOUT,
                "curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(3) | curses.A_STANDOUT,
                "curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(4) | curses.A_STANDOUT,
                "curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(5) | curses.A_STANDOUT,
                "curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(6) | curses.A_STANDOUT,
                "curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(7) | curses.A_STANDOUT,
                "curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLACK)",
            ),
            (
                curses.color_pair(8) | curses.A_STANDOUT,
                "curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK) PREV=B_on_B, NEXT=W-on_W",
            ),
            (
                curses.color_pair(9) | curses.A_STANDOUT,
                "curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(10) | curses.A_STANDOUT,
                "curses.init_pair(10, curses.COLOR_RED, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(11) | curses.A_STANDOUT,
                "curses.init_pair(11, curses.COLOR_GREEN, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(12) | curses.A_STANDOUT,
                "curses.init_pair(12, curses.COLOR_YELLOW, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(13) | curses.A_STANDOUT,
                "curses.init_pair(13, curses.COLOR_BLUE, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(14) | curses.A_STANDOUT,
                "curses.init_pair(14, curses.COLOR_MAGENTA, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(15) | curses.A_STANDOUT,
                "curses.init_pair(15, curses.COLOR_CYAN, curses.COLOR_WHITE)",
            ),
            (
                curses.color_pair(16) | curses.A_STANDOUT,
                "curses.init_pair(16, curses.COLOR_BLACK, curses.COLOR_WHITE)",
            ),
            (curses.color_pair(0), "curses.init_pair(0_ -- default =================="),
        ]

    ####################################################################
    def display_text_win(self):
        text_win_row_max, text_win_col_max = self.text_win.getmaxyx()
        for row_index in range(text_win_row_max):
            virt_row_index = row_index + self.text_win_corner_virt_row
            if virt_row_index < len(self.content):
                # valid row
                self.text_win.addstr(
                    row_index,
                    0,
                    self.content[virt_row_index][1][: text_win_col_max - 2],
                    self.content[virt_row_index][0],
                )
                self.text_win.clrtoeol()
            else:
                # invalid row
                self.text_win.addstr(
                    row_index,
                    0,
                    "...[EOF]...",
                    curses.color_pair(4) | curses.A_DIM,
                )
                self.text_win.clrtoeol()
        self.text_win.refresh()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s: %(filename)s: %(funcName)s: %(message)s",
        filename="example.log",
        level=logging.DEBUG,
    )
    logger.debug("__main__ start")
    tui = TUI(text_example * 3)
    tui.main()
    # finish
    sys.exit(0)
