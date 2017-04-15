# IMEDIFF2 - an interactive fullscreen 2-way merge tool

Copyright (C) 2003,2004 Jarno Elonen <elonen@iki.fi>
Released under the GNU General Public License,
see COPYING for details

The program is written in Python using the curses module.
For usage instructions, type "imediff -h" and/or hit
'h' or '?' in the interactive mode.

Visit the project website at
http://alioth.debian.org/projects/imediff2/

## FORK NOTICE

This is my fork/update of 5 year old source found in Debian archive.

Please report bug to this github unless this is merge to Debian.

 * No more surprise hitting "q".  You will be asked.
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

Osamu
