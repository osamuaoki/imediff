## Snippets for checking corner cases

Here is memo for this directory.

## Tailing NL

See `test_readlines.py`

* `FOOLINE.split("\n")` -- drop NL
* `FOOLINE.splitlines(keepends=True)` -- keep NL
* `fp.readlines()` -- keep NL, list of lines


## Subclass and overriding method

See `test_report.py`

## Curses operations

There are many subtle points to use curses library.

The initial motivation was the internal integer overflow of curses library.  So dumping all the data into a textpad needed to be avoided and copy only a limited portion of data into curses.

As I checked
[Window Objects](https://docs.python.org/3/library/curses.html#window-objects)
in "The Python Standard Library » Generic Operating System Services » curses — Terminal handling for character-cell displays of displays",
above issue is well known issue.

* [Calling insch in corner instead of addch worked for me](https://stackoverflow.com/questions/21594778/how-to-fill-to-lower-right-corner-in-python-curses)
* [exception usage example](https://stackoverflow.com/questions/36387625/curses-fails-when-calling-addch-on-the-bottom-right-corner)
* [mvprintw or insch usage with example](https://stackoverflow.com/questions/6574836/printing-to-right-side-or-bottom-side-of-terminal-using-ncurses)
* [addstr + insstr solution example](https://stackoverflow.com/questions/6574836/printing-to-right-side-or-bottom-side-of-terminal-using-ncurses)

The use of `win.clrtoeol` may be useful to avoid garbage stays in the screen.

### many `test_curses0*.py` programs:

Tried many coding styles to decide coding style

Issues and thoughts

* `newpad` is complicated for refresh and requires longer string copy.
* `addstr` faces overflow problems
  * `addstr`+`insch` looked good but not good enough for non-alphanumeric
  * `try: ...` is the only reasonable way
* `getch` must be used directly with curses
* color setting needs to be reconsidered.
* single row window is the best way to prevent overflow to next line.
* bad cursor move actually leave cursor position as is.
* application of wdiff should be single line case

### `curses_baseline.py`:

Final baseline for TUI.

* passing line is done by tuple: `(line,i_start,i_end)`
* single row derwin to contain overflow
* BS erases character
* NULL cause error
* HT(TAB) is 8 char only
* VT is no effect on screen


For imediff TUI, let me stick to `newwin` to work with 3 area ... something like:

* stdscr (terminal size)  60 min x 12 min
* text_area               60 min x  9 min
* status_area             60 min x  1
* popup (active area)     3     x  5 min
* help text data          76 columns or less desirable

### Resources

https://www.google.com/search?q=python+curses+window+newwin+refresh

* https://stackoverflow.com/questions/3170406/python-curses-newwin-not-working
* https://stackoverflow.com/questions/67021267/python-curses-newwin-not-being-displayed-if-stdscr-hasnt-been-refreshed-first
* https://stackoverflow.com/questions/9653688/how-to-refresh-curses-window-correctly
* https://stackoverflow.com/questions/57241649/continuously-update-string-in-python-curses
* https://stackoverflow.com/questions/16763701/python-ncurses-doesnt-show-screen-until-first-key-press-even-though-refresh-i
* https://www.reddit.com/r/learnpython/comments/12xqdlm/curses_for_a_split_screen_terminal_application/

Basic tutorials:

* https://www.ibm.com/docs/sl/aix/7.2?topic=library-manipulating-window-data-curses
* https://sceweb.sce.uhcl.edu/helm/WEBPAGE-Python/documentation/howto/curses/node5.html

Also:

* `getch` --- return integer
* `getkey` -- return string

### functions to remember

* `curses.raw()` / `curses.noraw()`
* `curses.def_prog_mode()`/`curses.reset_prog_mode()`
* `curses.def_shell_mode()`/`curses.reset_shell_mode()`
* `curses.curs_set(visibility)`
  * visibility=0 invisible
  * visibility=1 normal
  * visibility=2 very visible
* `window.leaveok(flag)` -- True no cursor change
* `window.refresh([pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol])`
  * parameters needed for "pad" (virtual screen)
  * pminrow and pmincol: the upper left-hand corner of the rectangle to be displayed in the pad
  * sminrow, smincol, smaxrow, smaxcol: the edges of the rectangle to be displayed on the screen

