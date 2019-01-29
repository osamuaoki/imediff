# IMEDIFF - an interactive fullscreen merge tool for DIFF2/3

 * Copyright (C) 2003,2004 Jarno Elonen <elonen@iki.fi>
 * Copyright (C) 2018 Osamu Aoki <osamu@debian.org>

Released under the GNU General Public License, 2.0+.
See LICENSE for details

The latest upstream source: https://github.com/osamuaoki/imediff

## What is imediff

The imediff command helps you to merge 2 slightly different files with an
optional base file interactively using the in-place alternating display of
the changed content on a single-pane full screen terminal user interface.

The advantage of this user interface is the minimal movement of the line of
sight for the user.  Other great tools such as vimdiff, xxdiff, meld and
kdiff3 require you to look at different points of display to find the exact
position of changes.  This makes imediff the most stress-free tool.  (I
realized this when I first used the original imediff2 program by Jarno
Elonen <elonen@iki.fi>.)

Other great tools for merge such as "diff3 -m ..." and "git merge ..."
operate only on the difference by line.  So even for the non-overlapping
changes, they yield the merge conflict if changes happen on the same line.

The automatic merge logic of the imediff command operates not only on the
difference by line but on the difference by character.  This is another
great feature of the imediff command. So for the non-overlapping changes, it
always yields the clean merge.

## Quick start

From the console command line prompt, type:
 * "imediff" to read the tutorial,
 * "imediff -h" to get all the command line options,
 * "imediff -o output older newer" to merge 2 files, and
 * "imediff -o output yours base theirs" to merge 3 files.

For usage instructions, type "h" and "H" in the interactive display.

If you wish to translate "h" menu, send me a translation PO file :-)

You can get Japanese help screen by setting and exporting "LANGUAGE=ja".

(This uses GNU gettext as its backend.  LANGUAGE setting has priority
over setting of LC_ALL etc.)

## History and features

This was originally written by Jarno Elonen in Python2. The latest original
upstream version was 1.1.2 released on 2007-8-18.

The original author's website was https://elonen.iki.fi/code/imediff/ .
Now it redirects to this site https://github.com/osamuaoki/imediff .

Osamu Aoki made a minor patched release for Debian buster in Oct 2018.

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
 * Add decent test cases
 * Include simple tutorial within "imediff".
 * Add "git-mergetool" integration.
 * Good CJK wide character support with East_Asian_Width on console.

This was accomplished by practically a whole rewrite of the source code in
November-December 2018.  Osamu decided to release this as imediff after
consulting with Jarno Elonen. Now program name is without "2", since it
supports diff for not only 2 files but also 3 files.  The version number is
bumped to 2.0.

## Note to developer and translator

### making Debian package

You can make your own Debian package as:

    $ git checkout master
    $ git archive --prefix=imediff-2.0/  upstream | xz > ../imediff_2.0.orig.tar.xz
    $ pdebuild
    $ sudo dpkg -i imediff_2.0-1_all.deb

Here, we assume the upstream version to be 2.0, and the Debian revision to be
1.

Please make sure to use tailing backslash for --prefix argument and bump
upstream version as needed.

### sharing changed source tree

You can fork this source to your account, e.g., `yourname`, and work on it as:

    $ git clone git@github.com:yuourname/imediff.git
    $ cd imediff
    $ git checkout --track origin/upstream
    $ git checkout upstream
     ... hack source
    $ git checkout master
     ... hack source
    $ git push --all

This way, you can share your changes back to me easily via "pull request".

### updating manpages

Please make sure to fit each code below 80-88 chars. (Run "black" on python
code)

Manpages need to be updated from XML files with "make" first in doc/ directory
when you edit it.

### updating PO

Tutorial contents should be within 76 chars/line to fit in console.

Update PO with:

    $ ./setup.py build_i18n -m

If anyone wants more contents to be translated such as manpage and tutorial,
adding po4a may be a good idea.  For now, let's keep it minimal.

### testing code

If you make changes, please test then.

To test the in-source-tree module, invoke the test script from setup.py in the
root of the source tree as:

    $ python3 setup.py test

To test the installed module, invoke the test script directly as:

    $ cd test
    $ python3 test_diff23lib.py -v

## Note on Debian package links

* imediff2 (based on older upstream source and released for Debian buster)
  * https://packages.debian.org/source/sid/imediff2 (source package in Debian)
  * https://packages.debian.org/sid/imediff2 (binary package in Debian)
  * https://bugs.debian.org/cgi-bin/pkgreport.cgi?repeatmerged=0;src=imediff2 (BTS)

* imediff: TBD (beta version on github)

This is written by Osamu Aoki on December 2018

