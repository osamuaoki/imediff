#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
Module diff3blocklib -- wrapper for diff3 (large)

Class LargeSequenceMatcher:
    A flexible class for comparing 3 of sequences of lines.

Copyright (C) 2024 Osamu Aoki <osamu@debian.org>

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

import sys
from imediff.diff3lib import SequenceMatcher3
from imediff.utils import logger


class LargeSequenceMatcher(SequenceMatcher3):

    """
    LargeSequenceMatcher is a matching class for comparing three of sequences
    of lines while splitting large data into multiple blocks.

    Each block should not exceed pre-defined scope upper limit to prevent
    integer overflow when using this data with the ncurses library to display
    data.

    If a single matching chunk exceed scope limit, it is recorded as a block
    with overflow flag set to True.

    Methods:

    __init__(a=[], b=[], c=[], matcher=0, isjunk=None, autojunk=True, linerule=2, scope=10000)
        Construct a LargeSequenceMatcher.

    set_block()
        set block list

    get_opcodes()
        Return list of 7-tuples describing how to merge c into a while b being
        common older version.
    """

    def __init__(
        self,
        a=[],
        b=[],
        c=[],
        matcher=0,
        isjunk=None,
        autojunk=True,
        linerule=2,
        scope=10000,
    ):
        """Construct a LargeSequenceMatcher.

        Optional arg a is the first of three lines to be compared. By default,
        an empty list. See also .set_seqs() and .set_seq1() of SequenceMatcher3.

        Optional arg b is the second of three lines to be compared. By default,
        an empty list. See also .set_seqs() and .set_seq1() of SequenceMatcher3.

        Optional arg c is the third of three lines to be compared. By default,
        an empty list. See also .set_seqs() and .set_seq1() of SequenceMatcher3.

        Optional arg matcher, isjunk, autojunk are passed to SequenceMatcher3
        called by instances of this Class of SequenceMatcher3.

        Optional arg scope is used as the upper limit of each block
        """

        super().__init__(a, b, c, matcher, isjunk, autojunk, linerule)
        self.scope = scope
        self.block = []

    def set_block(self):
        """Set block as list containing subset of lines to be compared."""

        self.block = []
        # TODO: XXX FIXME XXX need code here


if __name__ == "__main__":
    import doctest

    flags = doctest.REPORT_NDIFF | doctest.FAIL_FAST
    fail, total = doctest.testmod(optionflags=flags)
    print("{} failures out of {} tests -- ".format(fail, total), end="")
    if fail == 0:
        sys.exit(0)
    else:
        sys.exit(1)
