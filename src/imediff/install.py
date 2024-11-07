#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
IMEDIFF - Interactive Merge Editor for DIFF2 and DIFF3
          Curses based single-pane fullscreen interactive tool
          and CLI based non-interactive tool with --macro

Copyright (C) 2003, 2004 Jarno Elonen <elonen@iki.fi>
Copyright (C) 2018--2024 Osamu Aoki <osamu@debian.org>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the Free
Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.
"""

from imediff import __version__
import os
import sys
import subprocess

def install():
    """
    Entry point for imediff_install command

    Exit value
        0       normal exit
        1       error exit after an internal error
    """

    if os.getuid == 0:
        print("E: This imediff_install needs to be run from non-root user")
        print(
            "I: For system-wide install, use the Debian package or the upstream source."
        )
        print("I:  * https://tracker.debian.org/pkg/imediff")
        print("I:  * https://github.com/osamuaoki/imediff")
        sys.exit(1)
    # check install path of imediff module for site-package
    src_dir = os.path.dirname(os.path.abspath(__file__))
    # possible values for this_file
    # ~/.local/lib/python3.11/site-packages/imediff -- normal user-mode
    #  ~/.venv/lib/python3.11/site-packages/imediff -- after "python3 -m venv"
    python_dir = os.path.dirname(os.path.dirname(src_dir))
    lib_dir = os.path.dirname(python_dir)
    dest_dir = os.path.dirname(lib_dir)
    fp = open(dest_dir + "/bin/git-ime", "w")
    subprocess.run(["mkdir", "-p", dest_dir + "/bin"])
    subprocess.run(
        [
            "sed",
            "-e",
            "s/@@version@@/" + __version__ + "/",
            src_dir + "/data/git-ime.in",
        ],
        stdout=fp,
    )
    subprocess.run(["rm", "-f", src_dir + "/data/git-ime.in"])
    subprocess.run(["chmod", "755", dest_dir + "/bin/git-ime"])
    print("I: successfully installed: " + dest_dir + "/bin/git-ime")
    print("I: manual page for imediff can be found at: " + src_dir + "/imediff.1")
    print("I: manual page for git-ime can be found at: " + src_dir + "/git-ime.1")
    print("I: script for git-mergetool(1) can be found at: " + src_dir + "/imediff")
    print("I: For more, see the upstream source site.")
    print("I:   * https://github.com/osamuaoki/imediff")
    # subprocess.run(['mkdir', '-p', usr_dir + "/lib/git-core/mergetools"])
    # subprocess.run(['cp', '-f', src_dir + "/imediff", usr_dir + "/lib/git-core/mergetools"])
    # subprocess.run(['mkdir -p', usr_dir + "/share/man/man1/"])
    # subprocess.run(['cp', '-f', src_dir + "/imediff.1", usr_dir + "/share/man/man1/"])
    # subprocess.run(['cp', '-f', src_dir + "/git-ime.1", usr_dir + "/share/man/man1/"])

    sys.exit(0)


if __name__ == "__main__":
    install()
