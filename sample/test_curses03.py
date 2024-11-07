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

Why do we use it? It IS a long establIShed fact that a reader will be
dIStracted by the readable content of a page when looking at its layout. The
point of using lOREM Ipsum IS that it has a more-or-less normal dIStribution of
letters, as opposed to using 'Content here, content here', making it look like
readable EnglISh. Many desktop publIShing packages and web page editors now use
lOREM Ipsum as their default model text, and a search for 'lorem ipsum' will
uncover many web sites still in their infancy. Various versions have evolved
over the years, sometimes by accident, sometimes on purpose (injected humour
and the like).

Where does it come from? Contrary to popular belief, lOREM Ipsum IS not simply
random text. It has roots in a piece of classical Latin literature from 45 BC,
making it over 2000 years old. Richard McClintock, a Latin professor at
Hampden-Sydney College in Virginia, looked up one of the more obscure Latin
words, consectetur, from a lOREM Ipsum passage, and going through the cites of
the word in classical literature, dIScovered the undoubtable source. lOREM
Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et
Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. ThIS book
IS a treatISe on the theory of ethics, very popular during the RenaISsance. The
first line of lOREM Ipsum, "lOREM ipsum dolor sit amet..", comes from a line in
section 1.10.32.


The standard chunk of lOREM Ipsum used since the 1500s IS reproduced below for
those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et
Malorum" by Cicero are also reproduced in their exact original form,
accompanied by EnglISh versions from the 1914 translation by H. Rackham.

Where can I get some? There are many variations of passages of lOREM Ipsum
available, but the majority have suffered alteration in some form, by injected
humour, or randomISed words which don't look even slightly believable. If you
are going to use a passage of lOREM Ipsum, you need to be sure there ISn't
anything embarrassing hidden in the middle of text. All the lOREM Ipsum
generators on the Internet tend to repeat predefined chunks as necessary,
making thIS the first true generator on the Internet. It uses a dictionary of
over 200 Latin words, combined with a handful of model sentence structures, to
generate lOREM Ipsum which looks reasonable. The generated lOREM Ipsum IS
therefore always free from repetition, injected humour, or non-characterIStic
words etc.
        8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES
        8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES
\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB
\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB
\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB
\t\t2TABS\t\t2TABS\t\t2TABS
\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS
\t\t2TABS\t\t2TABS\t\t2TABS
\t\t2TABS\t\t2TABS\t\t2TAB
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\r
\aBELL
BELLS\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a
X\bBS
\fFF
\nNL
\rCR
\tHT
\vVT
\004EOT (EOF)
\033ESC
EOF_LINE
"""

help_msg_no_way = """\
        8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES 8SPACES
\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB\t1TAB
\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TABS\t\t2TAB
\aBELL\aBELL\aBELL\aBELL\aBELL\aBELL\aBELL\aBELL\aBELL\aBELL\aBELL\aBELL
BELLS_FOLLOW
\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a
\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a\a
\000NULL
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
        self.text_win_corner_virt_col = 0
        while True:
            # enforce sanity
            self.text_win_corner_virt_col = max(0, self.text_win_corner_virt_col)
            self.text_win_corner_virt_row = max(0, self.text_win_corner_virt_row)
            self.display_text_win()
            self.display_status_win()
            c = self.stdscr.getch()  # return integer
            ch = chr(c)
            if ch == "w" or ch == "x" or c == curses.KEY_EXIT or c == curses.KEY_SAVE:
                logger.debug("write to a file: imediff.out")
                try:
                    with open(
                        "imediff.out", mode="w", buffering=io.DEFAULT_BUFFER_SIZE
                    ) as fp:
                        fp.write(self.virt_lines)
                except OSError as err:
                    logger.error(
                        "Error {} in creating an output file: {}".format(
                            err, "imediff.out"
                        )
                    )
                    sys.exit(2)
                break
            elif ch == "q":
                logger.debug("quit without write to a file: imediff.out")
                break
            # elif ch == "h" or c == curses.KEY_HELP:
            # Show help screen
            # self.display_popup_win(self.get_helptext())
            elif ch == "H":
                # Show tutorial screen
                self.display_popup_win(help_msg)
            # Moves in document
            elif c == curses.KEY_HOME or ch == "0":
                self.text_win_corner_virt_row = 0
                self.text_win_corner_virt_col = 0
            elif c == curses.KEY_SF or c == curses.KEY_DOWN or ch == "j":
                self.text_win_corner_virt_row += 1
            elif c == curses.KEY_SR or c == curses.KEY_UP or ch == "k":
                self.text_win_corner_virt_row -= 1
            elif c == curses.KEY_NPAGE or ch == ";":
                self.text_win_corner_virt_row += 20
            elif c == curses.KEY_PPAGE or ch == "'":
                self.text_win_corner_virt_row -= 20
            elif c == curses.KEY_RIGHT or ch == "l":
                self.text_win_corner_virt_col += 8
            elif c == curses.KEY_LEFT or ch == "h":
                self.text_win_corner_virt_col -= 8
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
        color_a = "GREEN"  # a (OLDER/YOURS)
        color_b = "YELLOW"  # b (NEWER/COMMON)
        color_c = "CYAN"  # c (-----/THEIRS)
        color_m = "RED"  # marker d,f,null
        color_e = "MAGENTA"  # e (EDITOR)
        color_0 = "WHITE"  # tag=Ee attrib=DIM/NORMAL
        cc = dict()
        cc["GREEN"] = curses.COLOR_GREEN
        cc["YELLOW"] = curses.COLOR_YELLOW
        cc["CYAN"] = curses.COLOR_CYAN
        cc["RED"] = curses.COLOR_RED
        cc["MAGENTA"] = curses.COLOR_MAGENTA
        cc["BLUE"] = curses.COLOR_BLUE
        cc["WHITE"] = curses.COLOR_WHITE
        cc["BLACK"] = curses.COLOR_BLACK
        # set color pair_number as (pair_number, fg, bg)
        curses.init_pair(1, cc[color_a], cc["BLACK"])
        curses.init_pair(2, cc[color_b], cc["BLACK"])
        curses.init_pair(3, cc[color_c], cc["BLACK"])
        curses.init_pair(4, cc[color_m], cc["BLACK"])
        curses.init_pair(5, cc[color_e], cc["BLACK"])
        curses.init_pair(6, cc[color_0], cc["BLACK"])

        self.attrib = [
            curses.color_pair(i % 6 + 1) for i in range(len(self.virt_lines))
        ]

    ####################################################################
    def display_text_win(self):
        text_win_row_max, text_win_col_max = self.text_win.getmaxyx()
        for row_index in range(text_win_row_max):
            virt_row_index = row_index + self.text_win_corner_virt_row
            if virt_row_index < len(self.virt_lines):
                # valid row
                line = self.virt_lines[virt_row_index].rstrip()
                if len(line) >= self.text_win_corner_virt_col + text_win_col_max:
                    # long overflowing columns
                    self.text_win.addstr(
                        row_index,
                        0,
                        line[
                            self.text_win_corner_virt_col : self.text_win_corner_virt_col
                            + text_win_col_max
                            - 1
                        ],
                        self.attrib[virt_row_index],
                    )
                    self.text_win.insch(
                        line[
                            self.text_win_corner_virt_col
                            + text_win_col_max
                            - 1 : self.text_win_corner_virt_col
                            + text_win_col_max
                        ],
                        self.attrib[virt_row_index],
                    )
                else:
                    # empty trailing columns
                    if self.text_win_corner_virt_col >= len(line):
                        # no data to display
                        self.text_win.move(row_index, 0)
                        self.text_win.clrtoeol()
                    else:
                        # some remaining data
                        self.text_win.addstr(
                            row_index,
                            0,
                            line[self.text_win_corner_virt_col :],
                            self.attrib[virt_row_index],
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

    def display_status_win(self):
        _, status_win_col_max = self.status_win.getmaxyx()
        status_line = (
            "text_win_corner_virt_col={}, self.text_win_corner_virt_row={}".format(
                self.text_win_corner_virt_col, self.text_win_corner_virt_row
            )
        )
        if len(status_line) >= status_win_col_max:
            self.status_win.addstr(0, 0, status_line[: status_win_col_max - 1])
            self.status_win.insch(status_line[-1:])
        else:
            self.status_win.addstr(0, 0, status_line)
            self.status_win.clrtoeol()
        self.status_win.refresh()

    def display_popup_win(
        self, msg, msg_row_max=0, msg_col_max=0, margin_row=1, margin_col=2
    ):
        # A pop-up centered window with specified window size and border box
        # drawing.  The text are drawn in the box and has 1 space before and after
        # for readability.
        #
        # get msg display size for virt_msg
        virt_lines = msg.split("\n")  # no trailing \n
        virt_row_max = len(virt_lines)
        virt_col_max = 12  # enough for EOF amrker
        for line in virt_lines:
            virt_col_max = max(virt_col_max, len(line))
        corner_virt_row = 0
        corner_virt_col = 0
        # set up centered box_win
        stdscr_row_max, stdscr_col_max = self.stdscr.getmaxyx()
        span_col = stdscr_col_max - 2 * margin_col
        span_row = stdscr_row_max - 2 * margin_row
        logger.debug(
            "stdscr_row={}:{} span={}:{} msg='{}'".format(
                stdscr_row_max, stdscr_col_max, span_row, span_col, msg
            )
        )
        if msg_row_max == 0 and (virt_row_max + 2 * margin_row) <= stdscr_row_max:
            msg_row_max = virt_row_max
        elif msg_row_max == 0 or msg_row_max >= span_row:
            # force reasonable msg_row_max
            msg_row_max = stdscr_row_max - 2 * margin_row
        if msg_col_max == 0 and (virt_row_max + 2 * margin_row) <= stdscr_row_max:
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
        self.box_win.leaveok(True)
        self.box_win.refresh()
        while True:
            corner_virt_row = max(0, corner_virt_row)
            corner_virt_col = max(0, corner_virt_col)
            # set up centered msg_win
            self.msg_win = self.box_win.derwin(
                msg_row_max, msg_col_max + 1, margin_row, margin_col
            )
            self.msg_win.move(0, 0)
            msg_win_row_max, msg_win_col_max = self.msg_win.getmaxyx()
            for row_index in range(msg_win_row_max):
                virt_row_index = row_index + corner_virt_row
                if virt_row_index < len(virt_lines):
                    # valid row
                    line = virt_lines[virt_row_index].rstrip()
                    if len(line) >= corner_virt_col + msg_win_col_max:
                        # long overflowing columns
                        self.msg_win.move(row_index, 0)
                        self.msg_win.addstr(
                            line[corner_virt_col : corner_virt_col + msg_win_col_max],
                            self.attrib[virt_row_index],
                        )
                    else:
                        # empty trailing columns
                        if corner_virt_col >= len(line):
                            # no data to display
                            self.msg_win.move(row_index, 0)
                            self.msg_win.clrtoeol()
                        else:
                            # some remaining data
                            self.msg_win.move(row_index, 0)
                            self.msg_win.addstr(
                                line[corner_virt_col:],
                                curses.color_pair(0),
                            )
                            self.msg_win.clrtoeol()
                else:
                    # invalid row
                    self.msg_win.move(row_index, 0)
                    self.msg_win.addstr(
                        "...[EOF]...",
                        curses.color_pair(4) | curses.A_DIM,
                    )
                    self.msg_win.clrtoeol()
                self.msg_win.refresh()
            c = self.stdscr.getch()  # c : integer (stdscr! here)
            ch = chr(c)
            if c == curses.KEY_HOME or ch == "0":
                corner_virt_row = 0
                corner_virt_col = 0
            elif c == curses.KEY_SF or c == curses.KEY_DOWN or ch == "j":
                corner_virt_row += 1
            elif c == curses.KEY_SR or c == curses.KEY_UP or ch == "k":
                corner_virt_row -= 1
            elif c == curses.KEY_NPAGE or ch == ";":
                corner_virt_row += 20
            elif c == curses.KEY_PPAGE or ch == "'":
                corner_virt_row -= 20
            elif c == curses.KEY_RIGHT or ch == "l":
                corner_virt_col += 8
            elif c == curses.KEY_LEFT or ch == "h":
                corner_virt_col -= 8
            # Terminal resize signal
            # elif c == curses.KEY_RESIZE:
            elif c == ord("y") or c == ord("Y") - 32 or c == ord(" "):
                c = ord("y")
                break
            elif c == ord("n") or c == ord("N") - 32:
                c = ord("n")
                break
        return c


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
