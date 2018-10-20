# IMEDIFF2 - an interactive fullscreen 2-way merge tool

Copyright (C) 2003,2004 Jarno Elonen <elonen@iki.fi>
Released under the GNU General Public License,
see COPYING for details

The program is written in Python using the curses module.
For usage instructions, type "imediff -h" and/or hit
'h' or '?' in the interactive mode.

The original author's website at
  https://elonen.iki.fi/code/imediff/

Latest original upstream version is 1.1.2, released on 2007-8-18.

## FORK NOTICE

Copyright (C) 2018 Osamu Aoki <osamu@debian.org>

This is my fork/update of 5 year old source found in Debian archive.

  https://github.com/osamuaoki/imediff2

Please report bug to this github unless this is merge to Debian.

 * No more surprise hitting "q".  You will be asked. (Fix Debian bug #799865)
 * Fix manpage generation issue (Fix Debian bug #860351)
 * New git-ime wrapper script (great for git rebase/un-squash commit)
 * You can customize key bindings.

Under Debian:

```
 $ sudo apt-get update; sudo apt-get dist-upgrade
 $ sudo apt-get install devscripts debhelper xsltproc docbook-xsl python-all dh-python
 $ git clone git@github.com:osamuaoki/imediff2.git
 $ cd imediff2
 $ make dist
 $ cd ../imediff2-1.1.2.1
 $ debuild
 $ cd ..
 $ sudo dpkg -i imediff2-1.1.2.1-1.1.deb

```

## Note on Debian package links

* https://packages.debian.org/source/sid/imediff2 (source package)
* https://packages.debian.org/sid/imediff2 (binary package)
* https://bugs.debian.org/cgi-bin/pkgreport.cgi?repeatmerged=0;src=imediff2 (BTS)

Osamu
