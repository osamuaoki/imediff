# IMEDIFF - 2-way/3-way merge tool (CLI, Ncurses)

* Copyright (C) 2003,2004 Jarno Elonen <elonen@iki.fi>
* Copyright (C) 2018-2024 Osamu Aoki <osamu@debian.org>

Released under the GNU General Public License, 2.0+.
See LICENSE for details

The latest upstream source: https://github.com/osamuaoki/imediff

This provides the imediff command and git-ime command.

## What is imediff

The imediff command helps you to merge 2 slightly different files with an
optional base file interactively or non-interactively.

For non-interactive 2-way diff operation, this can express diffs with ordinary
diff-format 

```console
 $ imediff -n older.txt newer.txt -o diff.txt
```

For non-interactive 2-way diff operation, this can also express diffs with
wdiff format 

```console
 $ imediff -n -f older.txt newer.txt -o wdiff.txt
```

For non-interactive 3-way merge operation, this can not only express conflicts
with ordinary diff3-format but also 3-way wdiff format 

```console
 $ imediff -n yours.txt base.txt theirs.txt -o merged.txt
 $ imediff -n -f yours.txt base.txt theirs.txt -o wdiff-merged.txt
```
Here, this 3-way-merge logic is smarter than "diff3 -m".

For interactive operation, this uses the in-place alternating display of the
changed content on a single-pane full screen terminal user interface.  The
source of line is clearly identified by the color of the line or the identifier
character at the first column.  The advantage of this user interface is the
minimal movement of the line of sight for the user.

For interactive 2-way pick operation, this can select sections from input
files.

```console
 $ imediff older.txt newer.txt -o picked.txt
```

For interactive 3-way merge operation, this can select sections from input
files.

```console
 $ imediff yours.txt base.txt theirs.txt -o merged.txt
```

The line matching logic of imediff has been improved to ignore whitespaces and
use partial line matches to provide the best presentation with small chunk of
lines.

The automatic 3 way merge logic of the imediff command operates not only on the
difference by line but on the difference by character.  This is another great
feature of the imediff command. So for the non-overlapping changes, it always
yields the clean merge.

You can also use the imediff command non-interactively from CLI with --macro
option.

NOTE: There seems to be some limitation (16K?) of acceptable input lines for
imediff program running under full screen.  This causes imediff to crash.  The
root cause seems to be the underlining ncurses binding which imediff uses.

## What is git-ime

The "git ime" command helps you to unsquash 2 consecutive commits (`HEAD^`,
`HEAD`) of a git repository.  The "`git rebase -i <treeish>`" and "`gitk`" can
be used to organize unsquashed changes.

If any staged changes or local uncommitted changes are found in the git
repository, "git ime" immediately exits without changes to be on the safe side.

If the latest commit involves multiple files, "git ime" splits this big commit
by the file into multiple smaller commits involving a single file for each
commit.

If the latest commit involves only a single file, the commit may be split into
multiple smaller commits involving a set of minimal partial changes.  If the
target file is small, splitting process may be managed interactively by
imediff.  (You can force non-interactive splitting by "-a" option.)

This "git ime" is not only useful at the checked out branch head but also at
"edit" prompt during the interactive execution of "`git rebase -i <treeish>`".
Execute "git ime" after committing the pending commit.

## Quick start for Debian/Ubuntu derivative users

Please install the `imediff` package from the APT repository.

At the console command line prompt, type:

* "imediff" to read the tutorial,
* "imediff -h" to get all the command line options,
* "imediff -o output older newer" to merge 2 files, and
* "imediff -o output yours base theirs" to merge 3 files.

For usage instructions, type "h" and "H" in the interactive display.

(The use of GNU gettext is disabled for the sake of portability.)

## History and features

This was originally written by Jarno Elonen in Python2. The latest original
upstream version was 1.1.2 released on 2007-8-18.

The original author's website was https://elonen.iki.fi/code/imediff/ .  Now it
redirects to this site https://github.com/osamuaoki/imediff .

Osamu Aoki made a minor patched release for Debian buster in Oct 2018.

* No more surprise hitting "q".  You will be asked. (Fix Debian bug #799865)
* Fix manpage generation issue (Fix Debian bug #860351)
* New git-ime wrapper script (great for git rebase/un-squash commit)
* You can customize key bindings.

Osamu also wanted to add some features:

* Use of Python3 with pyproject.toml and setuptools to organize the source
   into a module with multiple source files.
* Use standard libraries for the flexible customization (argparse,
  configparser, logging)
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
* Add "git-ime" to help making partial patch series commits to git.
* Good CJK wide character support with East_Asian_Width on console.

This was accomplished by practically a whole rewrite of the source code in
November-December 2018.  Osamu decided to release this as imediff after
consulting with Jarno Elonen. Now program name is without "2", since it
supports diff for not only 2 files but also 3 files.  The version number is
bumped to 2.0.  In version 2.5, line matching rules are updated to produce
better diff presentation.

## Package installation

### Deb-package

You can install `imediff` package on Debian, Ubuntu, and derivatives.

This provides `imediff` and `git-ime` commands.

### Wheel-package

You can install wheel package from https://pypi.org/project/imediff/

After installation of wheel package as a user, you need to run:

```console
 $ imediff_install
```

This installs `git-ime` shell command to the pertinent virtual environment etc.

## Note to developer and translator

### Building package

* The building of deb-package is from "debian" branch.

* The building of wheel-package is supported from "main" branch.

You must have a relatively new system with python 3.9 equivalent of Debian 12.0
(bookworm) released on June 10th, 2023 with:

* https://github.com/pypa/setuptools (>=61.0.0)
* https://github.com/pypa/installer/
* https://github.com/pypa/build
* https://github.com/hukkin/tomli

```console
 $ cd /path/to/source-root
  ... hack
 $ python3 -m build
 $ cd build
 $ pip install 
```
The building of rpm is not supported as out-of-box now (patch welcome).

Code is not written for Windows compatibility in mind, yet. Gettext support was
intentionally dropped in favor of better compatibility across various systems.

The `git-ime` command requires you to have some POSIX shell and the `git`
command access.

### making Debian package

You can make your own Debian package as:

```console
 $ git clone https://github.com/osamuaoki/imediff.git
 $ cd imediff
 $ git checkout main
  ... hack source
 $ git commit -a
 $ rm -rf debian
 $ git add -A .
 $ git commit
 $ git tag 2.5
 $ git reset --hard HEAD^
 $ git deborig # to make ../*.orig.tar.xz
 $ sbuild
 $ cd ..
 $ sudo dpkg -i imediff_2.5-1_all.deb
```

Here, we assume the upstream version to be 2.5, and the Debian revision to be
1.

If you have bug fixes or feature enhancement propose changes to me via "pull
request"

### updating python source

Please make sure to fit each code below 80-88 chars. (Run "black" on python
code)  In case if reformat errors, check its syntax by:

```console
 $ python3 -m py_compile program.py
```

### updating manpages

Manpages need to be updated from XML files with "make" first in doc/ directory
when you edit it.

If you wish to update manpage from XML, `docbook-xsl` and `xsltproc` are needed
for building manpage from xml source then manually touch up details.

### testing python source

Whenever you make changes, please test them.

To test the installed module, invoke the test script as:

```console
 $ cd /path/to/source-root
 $ export PYTHONPATH=$(pwd)/src/
 $ python3 test/test_unittest_all.py -v
```

To test the installed module, invoke the test script as:

```console
 $ cd /path/to/source-root
 $ python3 test/test_unittest_all.py -v
```

## Note on Debian package links

* imediff2 (based on older python2 source for and before stretch)
  * https://tracker.debian.org/pkg/imediff2
  * https://packages.debian.org/source/sid/imediff2 (source package in Debian)
  * https://packages.debian.org/sid/imediff2 (binary package in Debian)
  * https://bugs.debian.org/cgi-bin/pkgreport.cgi?repeatmerged=0;src=imediff2 (BTS)

* imediff: (based on newer python3 source for buster)
  * https://tracker.debian.org/pkg/imediff
  * https://packages.debian.org/source/sid/imediff (source package in Debian)
  * https://packages.debian.org/sid/imediff (binary package in Debian)
  * https://bugs.debian.org/cgi-bin/pkgreport.cgi?repeatmerged=0;src=imediff (BTS)

This is written and updated by Osamu Aoki on February 2024.

