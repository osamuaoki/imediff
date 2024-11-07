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
    # Clear screen
    try:
        curses.curs_set(0)  # cursor off
    except Exception as e:
        exception = e
    # https://stackoverflow.com/questions/3170406/python-curses-newwin-not-working
    stdscr.clear()
    curses.curs_set(1)  # cursor on
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_WHITE)
    # This raises ZeroDivisionError when i == 10.
    term_row_max, term_col_max = stdscr.getmaxyx()
    textarea = stdscr.derwin(term_row_max - 1, term_col_max, 0, 0)
    textarea_row_max, textarea_col_max = textarea.getmaxyx()
    statusarea = stdscr.derwin(1, term_col_max, term_row_max - 1, 0)
    statusarea_row_max, statusarea_col_max = statusarea.getmaxyx()
    test_lines = test_text("#", term_row_max - 1, term_col_max)
    for i, test_line in enumerate(test_lines.split("\n")):
        if i < term_row_max - 1:
            try:
                textarea.addstr(i, 0, test_line[:term_col_max])
            except Exception as e:
                print("E: {}".format(e))
                pass
    statusarea.addstr(
        0,
        0,
        "STEP 0: stdscr={}:{}, textarea={}:{} statusarea={}:{}".format(
            term_row_max,
            term_col_max,
            textarea_row_max,
            textarea_col_max,
            statusarea_row_max,
            statusarea_col_max,
        ),
        curses.color_pair(6),
    )
    stdscr.refresh()
    textarea.refresh()
    statusarea.refresh()
    stdscr.getkey()
    #####################################################################################
    stdscr.clear()
    stdscr.addstr(term_row_max - 1, 0, "STEP 1: ")
    stdscr.refresh()
    stdscr.getkey()
    #####################################################################################
    box_row = 12
    box_col = 60
    margin_row = get_center_margin(textarea_row_max, box_row, 5)
    margin_col = get_center_margin(textarea_col_max, box_col, 5)
    outbox = textarea.derwin(box_row, box_col, margin_row, margin_col)
    outbox_row_max, outbox_col_max = outbox.getmaxyx()
    outbox.border()
    stdscr.addstr(term_row_max - 1, 0, "STEP 2: ", curses.color_pair(2))
    outbox.refresh()
    stdscr.getkey()
    #####################################################################################
    inbox = outbox.derwin(6, 36, 1, 2)
    inbox_row_max, inbox_col_max = inbox.getmaxyx()
    inbox.addstr(
        0, 0, "Hello, world! ################################\n" * 2, curses.A_REVERSE
    )
    stdscr.addstr(term_row_max - 1, 0, "STEP 3: ", curses.color_pair(3))
    inbox.refresh()
    stdscr.getkey()
    #####################################################################################
    # intext = textarea.newpad(1000,300)  # BAD
    intext = curses.newpad(1000, 300)
    intext.addstr(0, 0, test_lines)
    intext.refresh(0, 0, 5, 5, 30, 60)
    stdscr.addstr(
        term_row_max - 1,
        0,
        "STEP 4: stdscr={}:{}, outbox={}:{}, inbox={}:{}   END of example".format(
            term_row_max,
            term_col_max,
            outbox_row_max,
            outbox_col_max,
            inbox_row_max,
            inbox_col_max,
        ),
        curses.color_pair(4),
    )
    stdscr.refresh()
    stdscr.getkey()
    #####################################################################################


def get_center_margin(span_out, span_in, margin_min):
    span_in_real = min(span_out - 2 * margin_min, span_in)
    margin = (span_out - span_in_real) // 2
    return margin


if __name__ == "__main__":
    # run program
    main()
    # finish
    sys.exit(0)
