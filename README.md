# IMEDIFF - an interactive fullscreen merge tool for DIFF2/3

 * Copyright (C) 2003,2004 Jarno Elonen <elonen@iki.fi>
 * Copyright (C) 2018 Osamu Aoki <osamu@debian.org>

Released under the GNU General Public License, 2.0+.
See LICENSE for details

The latest upstream source: https://github.com/osamuaoki/imediff

## What is imediff

The imediff command helps you to merge 2 or 3 input files using the
full screen terminal user interface with the single-pane view.

From the console command line prompt, type:
 * "imediff" to read the tutorial,
 * "imediff -h" to get all the command line options,
 * "imediff -o output older newer" to merge 2 files, and
 * "imediff -o output yours base theirs" to merge 3 files.

For usage instructions, type "h" and "H" in the interactive screen.

## History and features

This was originally written by Jarno Elonen in Python2.  The original author's
website at:  https://elonen.iki.fi/code/imediff/

Latest original upstream version is 1.1.2, released on 2007-8-18.

Osamu Aoki made a minor patched release for Debian in Oct 2018.

 * No more surprise hitting "q".  You will be asked. (Fix Debian bug #799865)
 * Fix manpage generation issue (Fix Debian bug #860351)
 * New git-ime wrapper script (great for git rebase/un-squash commit)
 * You can customize key bindings.

Osamu also wanted to add some features:

 * Use of Python3 with setup.py and setuptools to organize the source into
   multiple source files.
 * Use standard libraries for the flexible customization
   (argparse, configparser, logging)
 * Addition of diff3 merge capability
 * Addition of wdiff capability
 * Addition of cursor location display capability
 * Make it edit highlighted section only
 * Make its TUI more friendly under monochrome terminal
 * Use curses.wrapper()
 * CLI and logging interface for easy self-testing/debugging
 * Include simple tutorial within "imediff".
 * Add "git-mergetool" integration.

This was accomplished by practically a whole rewrite of the source code in
November-December 2018.  Osamu decided to release this as imediff after
consulting with Jarno Elonen. Now program name is without "2", since it
supports diff for not only 2 files but also 3 files.  The version number is
bumped to 2.0.

## Note to developer

Build some files with "make" first.

## Note to translator

Please make sure to fit each line to 80 chars.  Tutorial contents should be
within 76 chars/line.

## Note on Debian package links

* imediff2
  * https://packages.debian.org/source/sid/imediff2 (source package in Debian)
  * https://packages.debian.org/sid/imediff2 (binary package in Debian)
  * https://bugs.debian.org/cgi-bin/pkgreport.cgi?repeatmerged=0;src=imediff2 (BTS)

* imediff: TBD

Osamu
