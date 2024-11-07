#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
Copyright (C) 2024 Osamu Aoki <osamu@debian.org>
"""

import sys
import curses
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename="example.log", level=logging.DEBUG)
exception = None
# See https://docs.python.org/3/library/curses.html
#     https://docs.python.org/3/howto/curses.html
# logger.debug('This message should go to the log file')
# logger.info('So should this')
# logger.warning('And this, too')
# logger.error('And non-ASCII stuff, too, like Øresund and Malmö')


def test_text(char, height, width):
    test_text = ""
    for col in range(0, width):
        test_text += "{:1}".format(col % 10)
    test_text += "\n\n\n"
    for col in range(0, width):
        test_text += "{:1}".format((col // 10) % 10)
    test_text += "\n\n\n"
    for row in range(6, (height // 3) - 6):
        test_text += (char[:1] * 32 + "  {:4}  ".format(row) + char[:1] * 40) * (
            width // 80
        ) + "\n\n\n"
    for row in range(height - (height // 3) * 3, height):
        test_text += "{:1}\n".format(char[:1] * width)
    return test_text


####################################################################
# Externally used main method and effective main method gui_loop
####################################################################
def main():  # for curses wrapper
    global exception
    logger.debug("start CURSES TEST")
    curses.wrapper(gui_main)
    if exception is not None:
        print("E: {} {}".format(type(exception).__name__, exception))
    logger.debug("end CURSES TEST")
    return


def gui_main(stdscr):  # for curses TUI (core)
    global exception
    y0, x0 = stdscr.getyx()
    # curses.curs_set(1)  # cursor on
    curses.curs_set(0)  # cursor off
    stdscr.clear()
    # curses.start_color()
    # curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # mode=e
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)  # tag=E:DIM/e:NORMAL
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # marker (diff/nill)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # mode=f
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)  # mode=a
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)  # mode=b
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # mode=c
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)  # NO
    margin = 2
    term_row_max, term_col_max = stdscr.getmaxyx()
    win_row_max = term_row_max - margin * 2 - 1
    win_col_max = term_col_max - margin * 2
    test_lines = test_text("#", term_row_max, term_col_max)
    for i, test_line in enumerate(test_lines.split("\n")):
        if i + margin < term_row_max - (margin + 1):
            stdscr.addstr(i + margin, margin, test_line[: term_col_max - margin * 2])
    stdscr.addstr(
        term_row_max - 1,
        0,
        "STEP 0: stdscr={}:{}, win_row={}:{} initial cursor ={}:{}".format(
            term_row_max, term_col_max, win_row_max, win_col_max, y0, x0
        ),
        curses.color_pair(1),
    )
    stdscr.refresh()
    stdscr.getkey()
    #####################################################################################
    stdscr.clear()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
        curses.color_pair(1),
    )
    stdscr.addstr(term_row_max - 1, 0, "STEP 1: ", curses.color_pair(1))
    try:
        stdscr.addstr(term_row_max - 1, term_col_max - 1, "X", curses.color_pair(1))
    except curses.error as err:
        stdscr.addstr(
            term_row_max - 2,
            0,
            "err={}".format(err),
            curses.color_pair(1) | curses.A_BOLD,
        )
        stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    #####################################################################################
    popup = curses.newpad(300, 200)
    test_lines = test_text("@", 50, 200)
    for i, test_line in enumerate(test_lines.split("\n")):
        if i % 3 == 0:
            popup.addstr(i, 0, test_line[:win_col_max], curses.color_pair(2))
    popup.refresh(0, 0, margin, margin, win_row_max, win_col_max)
    stdscr.addstr(
        term_row_max - 2, 0, "NNNNNNNNNNNNNNNNNNNNNNNNNNN", curses.color_pair(2)
    )
    stdscr.addstr(term_row_max - 1, 0, "STEP 2: ", curses.color_pair(2))
    stdscr.refresh()
    stdscr.getkey()
    #####################################################################################
    margin_row = get_center_margin(term_row_max - 1, 12, 5)
    margin_col = get_center_margin(term_col_max, 60, 5)
    outbox = curses.newwin(8, 40, margin_row, margin_col)
    outbox_row_max, outbox_col_max = outbox.getmaxyx()
    outbox.border()
    outbox.refresh()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV",
        curses.color_pair(3),
    )
    stdscr.addstr(term_row_max - 1, 0, "STEP 3: ", curses.color_pair(3))
    stdscr.clrtoeol()
    stdscr.getkey()
    #####################################################################################
    inbox = curses.newwin(6, 36, margin_row + 1, margin_col + 2)
    # inbox = outbox.derwin(6, 36, 1, 2)
    inbox_row_max, inbox_col_max = inbox.getmaxyx()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "========================================================",
        curses.color_pair(4),
    )
    inbox.addstr(
        0,
        0,
        "Hello, world! ################################",
        curses.color_pair(4) | curses.A_REVERSE,
    )
    stdscr.clrtoeol()
    stdscr.addstr(term_row_max - 1, 0, "STEP 4: ", curses.color_pair(4))
    stdscr.clrtoeol()
    inbox.refresh()
    stdscr.getkey()
    #####################################################################################
    stdscr.addstr(
        term_row_max - 2,
        0,
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        curses.color_pair(5),
    )
    stdscr.clrtoeol()
    stdscr.addstr(
        term_row_max - 1,
        0,
        "STEP 5: stdscr={}:{}, outbox={}:{}, inbox={}:{}".format(
            term_row_max,
            term_col_max,
            outbox_row_max,
            outbox_col_max,
            inbox_row_max,
            inbox_col_max,
        ),
        curses.color_pair(5),
    )
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "--------------------------------------------------------",
        curses.color_pair(6),
    )
    stdscr.addstr(term_row_max - 1, 0, "STEP 6: ", curses.color_pair(6))
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "++++++++++++++++++++++++++++++++++++++++++++++++++++++++",
        curses.color_pair(7),
    )
    stdscr.addstr(term_row_max - 1, 0, "STEP 7: ", curses.color_pair(7))
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "LLLLLLLLLLLLLLLLLLL curses.color_pair(8) LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",
        curses.color_pair(8),
    )
    stdscr.clrtoeol()
    stdscr.addstr(term_row_max - 1, 0, "STEP 8: ", curses.color_pair(8))
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "LLLLLLLLLLLLLLLLLLL curses.color_pair(1)|curses.A_REVERSE LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",
        curses.color_pair(1) | curses.A_REVERSE,
    )
    stdscr.clrtoeol()
    stdscr.addstr(
        term_row_max - 1, 0, "STEP 9: ", curses.color_pair(1) | curses.A_REVERSE
    )
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "LLLLLLLLLLLLLLLLLLL curses.color_pair(1)|curses.A_BOLD LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",
        curses.color_pair(1) | curses.A_BOLD,
    )
    stdscr.clrtoeol()
    stdscr.addstr(
        term_row_max - 1, 0, "STEP 10: ", curses.color_pair(1) | curses.A_BOLD
    )
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "LLLLLLLLLLLLLLLLLLL curses.color_pair(1)|curses.A_DIM LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",
        curses.color_pair(1) | curses.A_DIM,
    )
    stdscr.clrtoeol()
    stdscr.addstr(term_row_max - 1, 0, "STEP 11: ", curses.color_pair(1) | curses.A_DIM)
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    stdscr.addstr(
        term_row_max - 2,
        0,
        "LLLLLLLLLLLLLLLLLLL curses.color_pair(1)|curses.A_NORMAL LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",
        curses.color_pair(1) | curses.A_NORMAL,
    )
    stdscr.addstr(
        term_row_max - 1, 0, "STEP 12: ", curses.color_pair(1) | curses.A_NORMAL
    )
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    stdscr.addstr(
        term_row_max - 3,
        0,
        "LLLLLLLLLLLLLLLLLLL curses.color_pair(3)|curses.A_REVERSE LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",
        curses.color_pair(3) | curses.A_REVERSE,
    )
    stdscr.addstr(
        term_row_max - 2,
        0,
        "LLLLLLLLLLLLLLLLLLL curses.color_pair(3)|curses.A_DIM|curses.A_REVERSE LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",
        curses.color_pair(3) | curses.A_DIM | curses.A_REVERSE,
    )
    stdscr.clrtoeol()
    stdscr.addstr(
        term_row_max - 1,
        0,
        "STEP 13: ",
        curses.color_pair(3) | curses.A_DIM | curses.A_REVERSE,
    )
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    long_line = "LLLLLLLLLLLLLLLLLLL curses.color_pair(4) | curses.A_REVERSE | curses.A_BOLD LLLLLLLLLLLLLLL LONG LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL"
    stdscr.move(term_row_max - 1, 0)
    y0, x0 = stdscr.getyx()  # don't forget () here
    try:
        stdscr.addstr(
            term_row_max - 1,
            0,
            long_line,
            curses.color_pair(4) | curses.A_REVERSE | curses.A_BOLD,
        )
    except curses.error as _:
        pass
    y1, x1 = stdscr.getyx()

    stdscr.addstr(
        term_row_max - 6,
        0,
        "STEP 14: before {}:{} len={}".format(y0, x0, len(long_line)),
        curses.color_pair(4) | curses.A_BOLD,
    )
    stdscr.addstr(
        term_row_max - 5,
        0,
        "STEP 14: after {}:{} max_col-1={}".format(y1, x1, term_col_max - 1),
        curses.color_pair(4) | curses.A_BOLD,
    )
    stdscr.refresh()
    stdscr.getkey()

    # stdscr.move(term_row_max - 1, term_col_max-1)
    stdscr.move(0, 0)
    y2, x2 = stdscr.getyx()
    try:
        stdscr.move(term_row_max - 1, term_col_max)
    except curses.error as _:
        pass
    y3, x3 = stdscr.getyx()
    try:
        stdscr.addstr(
            "@",
            curses.color_pair(6) | curses.A_REVERSE | curses.A_BOLD,
        )
    except curses.error as _:
        pass
    y4, x4 = stdscr.getyx()
    stdscr.clrtoeol()
    y5, x5 = stdscr.getyx()
    stdscr.addstr(
        term_row_max - 6,
        0,
        "STEP 15 at right-bottom after {}:{} >> outside {}:{} >>@ {}:{}  >>clrtoeol {}:{}  max={}:{}".format(
            y2, x2, y3, x3, y4, x4, y5, x5, term_row_max, term_col_max
        ),
        curses.color_pair(4) | curses.A_BOLD,
    )
    stdscr.clrtoeol()
    stdscr.refresh()
    stdscr.getkey()
    #####################################################################################


def get_center_margin(span_out, span_in, margin_min):
    span_in_real = min(span_out - 2 * margin_min, span_in)
    margin = (span_out - span_in_real) // 2
    return margin


####################################################################
# Internally used utility methods (popup display via curses)
####################################################################
def tui_popup_text(stdscr, text):
    curses.curs_set(0)
    term_row_max, term_col_max = stdscr.getmaxyx()
    stdscr.border()
    for line_index, line_text in enumerate(text.split("\n")):  # no \n
        if line_index < term_row_max - 5:
            stdscr.addstr(
                line_index + 1,
                2,
                line_text[: term_col_max - 5],
                curses.A_BOLD | curses.color_pair(7),
            )
    stdscr.refresh()
    stdscr.getch()
    return


if __name__ == "__main__":
    # run program
    main()
    # finish
    sys.exit(0)
