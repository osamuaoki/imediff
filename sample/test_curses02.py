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
    debug("start CURSES TEST")
    curses.wrapper(gui_main)
    if exception is not None:
        print("E: {} {}".format(type(exception).__name__, exception))
    debug("end CURSES TEST")
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
    # curses.curs_set(1)  # cursor on
    curses.curs_set(0)  # cursor off
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
    stdscr.insstr(term_row_max - 1, term_col_max - 1, "@")
    stdscr.refresh()
    stdscr.getkey()
    textarea = stdscr.derwin(term_row_max - 1, term_col_max, 0, 0)
    textarea_row_max, textarea_col_max = textarea.getmaxyx()
    textarea.insstr(textarea_row_max - 1, textarea_col_max - 1, "*")
    textarea.refresh()
    textarea.getkey()
    statusarea = stdscr.derwin(1, term_col_max, term_row_max - 1, 0)
    statusarea_row_max, statusarea_col_max = statusarea.getmaxyx()
    statusarea.insstr(statusarea_row_max - 1, statusarea_col_max - 1, "%")
    statusarea.refresh()
    statusarea.getkey()
    statusarea = stdscr.derwin(1, term_col_max, term_row_max - 1, 0)
    statusarea_row_max, statusarea_col_max = statusarea.getmaxyx()
    try:
        statusarea.addstr(statusarea_row_max - 1, statusarea_col_max - 1, "$")
    except curses.error as _:
        pass
    statusarea.refresh()
    # getkey is noy window specific
    # statusarea.getkey()
    # textarea.getkey()
    stdscr.getkey()
    stdscr.clear()
    stdscr.border()
    stdscr.refresh()
    stdscr.getkey()
    for row in range(0, textarea_row_max):
        color = row % 6
        textarea.insstr(row, 0, "&" * (textarea_col_max), color)
    textarea.addstr(textarea_row_max - 1, 10, "!" * 10)
    textarea.clrtoeol()
    textarea.refresh()
    stdscr.getkey()
    offset_col = 10
    stdscr.addstr(term_row_max - 1, offset_col, "Z" * (term_col_max - 1 - offset_col))
    stdscr.insch("E")
    stdscr.refresh()
    stdscr.getkey()

    #####################################################################################


def get_center_margin(span_out, span_in, margin_min):
    span_in_real = min(span_out - 2 * margin_min, span_in)
    margin = (span_out - span_in_real) // 2
    return margin


def get_sanitized(x, x_min, x_max):
    if x_min > x_max:
        print("ERROR min={}, max={}".format(x_min, x_max))
        sys.exit(1)
    elif x < x_min:
        x = x_min
    elif x >= x_max:
        x = x_max
    else:
        pass  # sanity OK
    return x


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
                line_index + 1, 2, line_text[: term_col_max - 5], curses.A_BOLD
            )
    stdscr.refresh()
    stdscr.getch()
    return


# debug message
def debug(msg):
    logger.debug(msg)
    return


if __name__ == "__main__":
    # run program
    main()
    # finish
    sys.exit(0)
