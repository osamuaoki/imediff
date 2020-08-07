#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
Module diff2lib -- wrapper for diff2

Class SequenceMatcher2:
    A flexible class for comparing pairs of sequences of any type.

Copyright (C) 2018       Osamu Aoki <osamu@debian.org>

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

import difflib


def _tag2t(tag):
    if tag == "equal":
        t = "E"
    else:
        t = "N"
    return t


class SequenceMatcher2(difflib.SequenceMatcher):

    """
    SequenceMatcher2 is a flexible wrapper class for comparing pairs of
    sequences of any type, so long as the sequence elements are hashable.
    The is to accommodate different algorithms available.

    Example, comparing two strings, and considering blanks to be "junk":

    >>> a = "private Thread currentThread;"
    >>> b = "private volatile Thread currentThread;"
    >>> s = SequenceMatcher2(lambda x: x == " ", a, b)
    >>>

    You can group matched and unmatched ranges by using .get_chunks():

    >>> for tag, i1, i2, j1, j2 in s.get_chunks():
    ...     print("%1s a[%d:%d], b[%d:%d]='%s', '%s'" % (tag, i1, i2, j1, j2, a[i1:i2], b[j1:j2]))
    E a[0:8], b[0:8]='private ', 'private '
    N a[8:8], b[8:17]='', 'volatile '
    E a[8:29], b[17:38]='Thread currentThread;', 'Thread currentThread;'

    Methods:

    __init__(isjunk=None, a='', b='')
        Construct a SequenceMatcher2.

    set_seqs(a, b)
        Set the two sequences to be compared.

    set_seq1(a)
        Set the first sequence to be compared.

    set_seq2(b)
        Set the second sequence to be compared.

    get_chunks()
        Return list of 5-tuples describing how to turn a into b.
    """

    def __init__(self, isjunk=None, a="", b="", autojunk=True):
        """Construct a SequenceMatcher2.

        Optional arg isjunk is None (the default), or a one-argument
        function that takes a sequence element and returns true iff the
        element is junk.  None is equivalent to passing "lambda x: 0", i.e.
        no elements are considered to be junk.  For example, pass
            lambda x: x in " \\t"
        if you're comparing lines as sequences of characters, and don't
        want to synch up on blanks or hard tabs.

        Optional arg a is the first of two sequences to be compared.  By
        default, an empty string.  The elements of a must be hashable.  See
        also .set_seqs() and .set_seq1().

        Optional arg b is the second of two sequences to be compared.  By
        default, an empty string.  The elements of b must be hashable. See
        also .set_seqs() and .set_seq2().

        Optional arg autojunk should be set to False to disable the
        "automatic junk heuristic" that treats popular elements as junk
        (see module documentation for more information).
        """

        # Members:
        # a
        #      first sequence
        # b
        #      second sequence; differences are computed as "what do
        #      we need to do to 'a' to change it into 'b'?"
        # chunks
        #      a list of (tag, i1, i2, j1, j2) tuples, where tag is
        #      one of
        #          'N'    a[i1:i2] should be replaced by b[j1:j2]
        #          'E'    a[i1:i2] == b[j1:j2]
        # isjunk
        #      a user-supplied function taking a sequence element and
        #      returning true iff the element is "junk" -- this has
        #      subtle but helpful effects on the algorithm, which I'll
        #      get around to writing up someday <0.9 wink>.
        #      DON'T USE!  Only __chain_b uses this.  Use "in self.bjunk".

        super().__init__(isjunk, a, b, autojunk)
        self.chunks = None

    def get_chunks(self):
        """Return list of 5-tuples describing how to turn a into b.

        Each tuple is of the form (tag, i1, i2, j1, j2).  The first tuple
        has i1 == j1 == 0, and remaining tuples have i1 == the i2 from the
        tuple preceding it, and likewise for j1 == the previous j2.

        The tags are strings, with these meanings:

        'N':   a[i1:i2] should be replaced by b[j1:j2]
                  delete if j1==j2
                  insert if j1==j2
        'E':   a[i1:i2] == b[j1:j2]

        >>> a = "qabxcd"
        >>> b = "abycdf"
        >>> s = SequenceMatcher2(None, a, b)
        >>> for tag, i1, i2, j1, j2 in s.get_chunks():
        ...    print(("%1s a[%d:%d] (%s) b[%d:%d] (%s)" %
        ...           (tag, i1, i2, a[i1:i2], j1, j2, b[j1:j2])))
        ...
        N a[0:1] (q) b[0:0] ()
        E a[1:3] (ab) b[0:2] (ab)
        N a[3:4] (x) b[2:3] (y)
        E a[4:6] (cd) b[3:5] (cd)
        N a[6:6] () b[5:6] (f)
        """

        # Long version
        #        answer = list()
        #        for tag, i1, i2, j1, j2 in self.get_opcodes():
        #            if tag == 'equal':
        #                answer.append(('E', i1, i2, j1, j2))
        #            else: # tag != 'equal'
        #                answer.append(('N', i1, i2, j1, j2))
        #        self.chunks = answer

        # Short version
        self.chunks = [
            (_tag2t(tag), i1, i2, j1, j2) for tag, i1, i2, j1, j2 in self.get_opcodes()
        ]
        return self.chunks


if __name__ == "__main__":
    import doctest

    doctest.testmod()
