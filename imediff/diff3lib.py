#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
Module diff3lib -- wrapper for diff3

Class SequenceMatcher3:
    A flexible class for comparing 3 of sequences of any type.

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

import sys

from imediff.diff2lib import SequenceMatcher2
from imediff.utils import *


class SequenceMatcher3:

    """
    SequenceMatcher3 is a matching class for comparing three of sequences of
    any type, so long as the sequence elements are hashable.

    Let's call these three sequences as A (yours), B (base), and C (theirs).
    Let's assume A and C are derivatives from B and try to merge C into A.
    The basic rule for the merging of three of sequences is as follows:
        * Check B-A matching and B-C matching situation.
        * Walk through B to see which sides made change. (12 cases)
        * Check if the high end of range is available (Either "E" or deletion)
        * Pick one making change as the merged content.
            * Merged as equal: 3 cases
                BA      EEEENN..    EEEEEE..    EEEENN..
                BC      EEEENN..    EEEENN..    EEEEEE..
                        ^^^^        ^^^^        ^^^^
                Range   AC          AC          AC
                Tag     E           E           E
            * Merged to pick A: 2 cases, undecided to pick conflict 1 case
                BA      NNNNNN..    NNNNEE..                NNNNEE..
                BC      EEEENN..    EEEENN..                EEEEEE..
                        ^^^^        ^^^^                    ^^^^
                Range   A           AC                      AC
                Tag     N*          A                       A
            * Merged to pick C: 2 cases, undecided to pick conflict 1 case
                BA      EEEENN..                EEEENN..    EEEEEE..
                BC      NNNNNN..                NNNNEE..    NNNNEE..
                        ^^^^                    ^^^^        ^^^^
                Range   C                       AC          AC
                Tag     N*                      C           C
            * Merged as conflict: 1 case, undecided to pick conflict 2 cases
                BA                  NNNNEE..    NNNNNN..    NNNNEE..
                BC                  NNNNNN..    NNNNEE..    NNNNEE..
                                    ^^^^        ^^^^        ^^^^
                Range               C           A           AC
                Tag                 N*          N*          N
            Please note the high end of range is unavailable if the continuing
            side is "N" and not complete deletion. (marked "N*")
            All "N" and "N*" containing ranges are conflict but are checked for
            A==C check (case "e")

            Here tag for diff3:
                'E'    a[j1:j2] == b[i1:i2] == c[k1:k2] == a[j1:j2]
                'A'    a[j1:j2] != b[i1:i2] == c[k1:k2] != a[j1:j2]
                'C'    a[j1:j2] == b[i1:i2] != c[k1:k2] != a[j1:j2]
                'e'    a[j1:j2] != b[i1:i2] != c[k1:k2] == a[j1:j2]
                'N'    a[j1:j2] != b[i1:i2] != c[k1:k2] != a[j1:j2]

    This requires diff2lib which is a wrapper of difflib and provides
    'get_chunks' method. Here tag for diff2:

                'E'    a[j1:j2] == b[i1:i2]
                'N'    a[j1:j2] != b[i1:i2]

    Example1: comparing two strings, and considering None to be "junk"

    >>> a = "private Thread currentThread foo bar;"
    >>> b = "private volatile Thread currentThread;"
    >>> c = "private volatile currentThread foo;tail"
    >>> s = SequenceMatcher3(None, a, b, c)
    >>>

    If you want to know how to change the first sequence into the second,
    use .get_chunks():

    >>> for tag, i1, i2, j1, j2, k1, k2 in s.get_chunks():
    ...     print("%s a[%d:%d],b[%d:%d],c[%d:%d] => '%s', '%s', '%s'" % (
    ...     tag, i1, i2, j1, j2, k1, k2, a[i1:i2], b[j1:j2], c[k1:k2]))
    ...
    E a[0:6],b[0:6],c[0:6] => 'privat', 'privat', 'privat'
    A a[6:6],b[6:15],c[6:15] => '', 'e volatil', 'e volatil'
    E a[6:8],b[15:17],c[15:17] => 'e ', 'e ', 'e '
    C a[8:15],b[17:24],c[17:17] => 'Thread ', 'Thread ', ''
    E a[15:28],b[24:37],c[17:30] => 'currentThread', 'currentThread', 'currentThread'
    N a[28:36],b[37:37],c[30:34] => ' foo bar', '', ' foo'
    E a[36:37],b[37:38],c[34:35] => ';', ';', ';'
    C a[37:37],b[38:38],c[35:39] => '', '', 'tail'

    Example 2: comparing two strings, and considering blanks to be "junk"

    >>> a = "private Thread currentThread foo bar;"
    >>> b = "private volatile Thread currentThread;"
    >>> c = "private volatile currentThread foo;tail"
    >>> s = SequenceMatcher3(lambda x: x == " ", a, b, c)
    >>>

    If you want to know how to change the first sequence into the second,
    use .get_chunks():

    >>> for tag, i1, i2, j1, j2, k1, k2 in s.get_chunks():
    ...     print("%s a[%d:%d],b[%d:%d],c[%d:%d] => '%s', '%s', '%s'" % (
    ...     tag, i1, i2, j1, j2, k1, k2, a[i1:i2], b[j1:j2], c[k1:k2]))
    ...
    E a[0:8],b[0:8],c[0:8] => 'private ', 'private ', 'private '
    A a[8:8],b[8:16],c[8:16] => '', 'volatile', 'volatile'
    e a[8:8],b[16:17],c[16:16] => '', ' ', ''
    C a[8:14],b[17:23],c[16:16] => 'Thread', 'Thread', ''
    E a[14:28],b[23:37],c[16:30] => ' currentThread', ' currentThread', ' currentThread'
    N a[28:36],b[37:37],c[30:34] => ' foo bar', '', ' foo'
    E a[36:37],b[37:38],c[34:35] => ';', ';', ';'
    C a[37:37],b[38:38],c[35:39] => '', '', 'tail'

    This example 2 produces more intuitive result due to setting for "junk".

    Methods:

    __init__(isjunk=None, a='', b='', c='')
        Construct a SequenceMatcher3.

    set_seqs(a, b)
        Set the two sequences to be compared.

    set_seq1(a)
        Set the first sequence to be compared.

    set_seq2(b)
        Set the second sequence to be compared.

    set_seq3(c)
        Set the third sequence to be compared.

    get_chunks()
        Return list of 7-tuples describing how to merge c into a while b being
        common older version.
    """

    def __init__(self, isjunk=None, a="", b="", c="", autojunk=True):
        """Construct a SequenceMatcher3.

        Optional arg isjunk is None (the default), or a one-argument
        function that takes a sequence element and returns true iff the
        element is junk.  None is equivalent to passing "lambda x: 0", i.e.
        no elements are considered to be junk.  For example, pass
            lambda x: x in " \\t"
        if you're comparing lines as sequences of characters, and don't
        want to synch up on blanks or hard tabs.

        Optional arg a is the first of three sequences to be compared.  By
        default, an empty string.  The elements of a must be hashable.  See
        also .set_seqs() and .set_seq1().

        Optional arg b is the second of three sequences to be compared.  By
        default, an empty string.  The elements of b must be hashable. See
        also .set_seqs() and .set_seq2().

        Optional arg c is the third of three sequences to be compared.  By
        default, an empty string.  The elements of b must be hashable. See
        also .set_seqs() and .set_seq3().

        Optional arg autojunk should be set to False to disable the
        "automatic junk heuristic" that treats popular elements as junk
        (see module documentation for more information).
        """

        # Members:
        # a
        #      first sequence (yours, merge prioritize on this)
        # b
        #      second sequence (old common, used to check who changed what)
        # c
        #      third sequence (theirs, data to be merged)
        # chunks
        #      a list of (tag, i1, i2, j1, j2, k1, k2) tuples, where tag is
        #      one of
        #          'E'    a[i1:i2] == b[j1:j2] == c[k1:k2] == a[i1:i2]
        #          'A'    a[i1:i2] != b[j1:j2] == c[k1:k2] != a[i1:i2]
        #          'C'    a[i1:i2] == b[j1:j2] != c[k1:k2] != a[i1:i2]
        #          'e'    a[i1:i2] != b[j1:j2] != c[k1:k2] == a[i1:i2]
        #          'N'    a[i1:i2] != b[j1:j2] != c[k1:k2] != a[i1:i2]
        # isjunk
        #      a user-supplied function taking a sequence element and
        #      returning true iff the element is "junk" -- this has
        #      subtle but helpful effects on the algorithm, which I'll
        #      get around to writing up someday <0.9 wink>.
        #      DON'T USE!  Only __chain_b uses this.  Use "in self.bjunk".

        self.isjunk = isjunk
        self.a = a
        self.b = b
        self.c = c
        self.autojunk = autojunk
        self.chunks = None

    def set_seq1(self, a):
        """Set the first sequence to be compared.
        """

        if a is self.a:
            return
        self.a = a
        self.chunks = None

    def set_seq2(self, b):
        """Set the second sequence to be compared.
        """

        if b is self.b:
            return
        self.b = b
        self.chunks = None

    def set_seq3(self, c):
        """Set the third sequence to be compared.
        """

        if c is self.c:
            return
        self.c = c
        self.chunks = None

    def set_seqs(self, a, b, c):
        """Set the two sequences to be compared.
        """

        self.set_seq1(a)
        self.set_seq2(b)
        self.set_seq3(c)

    def get_chunks(self):
        """Return list of 7-tuples describing how a, b, c matches.

        Each tuple is of the form (tag, i1, i2, j1, j2, k1, k2).  The first
        tuple has i1 == j1 == k1 == 0, and remaining tuples have i1 == the i2
        from the tuple preceding it, and likewise for j1 == the previous j2,
        and likewise for k1 == the previous k2.

        The tags are strings, with these meanings:

        'E':   a == b == c
        'e':   a != b != c == A
        'A':   c == b --> a, change in a
        'C':   a == b --> c, change in c
        'N':   b-->a, b-->c, conflicting changes

        >>> a = "qabxcdsdgp"
        >>> b = "abycdfsdkg"
        >>> c = "abycdfzcpgp"
        >>> s = SequenceMatcher3(None, a, b, c)
        >>> for tag, i1, i2, j1, j2, k1, k2 in s.get_chunks():
        ...    print(("%s a[%d:%d] (%s) / b[%d:%d] (%s) / c[%d:%d] (%s)" %
        ...           (tag, i1, i2, a[i1:i2], j1, j2, b[j1:j2], k1, k2, c[k1:k2])))
        ...
        A a[0:1] (q) / b[0:0] () / c[0:0] ()
        E a[1:3] (ab) / b[0:2] (ab) / c[0:2] (ab)
        A a[3:4] (x) / b[2:3] (y) / c[2:3] (y)
        E a[4:6] (cd) / b[3:5] (cd) / c[3:5] (cd)
        A a[6:6] () / b[5:6] (f) / c[5:6] (f)
        N a[6:8] (sd) / b[6:9] (sdk) / c[6:9] (zcp)
        E a[8:9] (g) / b[9:10] (g) / c[9:10] (g)
        e a[9:10] (p) / b[10:10] () / c[10:11] (p)
        """

        a = self.a
        b = self.b
        c = self.c
        chunks_ba = SequenceMatcher2(self.isjunk, b, a).get_chunks()
        chunks_bc = SequenceMatcher2(self.isjunk, b, c).get_chunks()
        n_ba = 0  # walking index for chunks_ba
        n_bc = 0  # walking index for chunks_bc
        len_ba = len(chunks_ba)
        len_bc = len(chunks_bc)
        il = jl = kl = 0  # range lower end for b, a, c (next in next round)
        ih = jh = kh = 0  # range high end for b, a, c (next in next round)
        answer = list()
        tag = ""
        while n_ba < len_ba or n_bc < len_bc:
            # logger.debug("diff3lib: n_ba={} n_bc={} len_ba={} len_bc={}".format(n_ba, n_bc, len_ba, len_bc))
            # get a chunk data
            if n_ba < len_ba:
                (tag_ba, il_ba, ih_ba, jl_ba, jh_ba) = chunks_ba[n_ba]
            else:
                (tag_ba, il_ba, ih_ba, jl_ba, jh_ba) = chunks_ba[len_ba - 1]
                (tag_ba, il_ba, ih_ba, jl_ba, jh_ba) = ("E", ih_ba, ih_ba, jh_ba, jh_ba)
                # print("diff3lib: OVERRUN n_ba={} len_ba={}".format(n_ba, len_ba), file=sys.stderr)
            if n_bc < len_bc:
                (tag_bc, il_bc, ih_bc, kl_bc, kh_bc) = chunks_bc[n_bc]
            else:
                (tag_bc, il_bc, ih_bc, kl_bc, kh_bc) = chunks_bc[len_bc - 1]
                (tag_bc, il_bc, ih_bc, kl_bc, kh_bc) = ("E", ih_bc, ih_bc, kh_bc, kh_bc)
                # print("diff3lib: OVERRUN n_bc={} len_bc={}".format( n_bc, len_bc), file=sys.stderr)
            # get tag for this set of chunks if high range value is available
            if tag == "N":
                pass  # All undecided comes in as tag == "N", otherwise tag == ""
            elif tag_ba == "E" and tag_bc == "E":
                tag = "E"
            elif tag_ba == "N" and tag_bc == "E":
                tag = "A"
            elif tag_ba == "E" and tag_bc == "N":
                tag = "C"
            elif tag_ba == "N" and tag_bc == "N":
                tag = "N"
            if ih_ba == ih_bc:
                n_ba += 1
                n_bc += 1
                ih = ih_ba  # == ih_bc
                jh = jh_ba
                kh = kh_bc
            elif ih_ba > ih_bc:
                n_bc += 1
                ih = ih_bc
                kh = kh_bc
                if tag_ba == "E":
                    jh = jh_ba - (ih_ba - ih_bc)
                elif jh_ba == jl_ba:
                    jh = jh_ba
                else:
                    jh = None  # undecided
                    tag = "N"
            if ih_ba == ih_bc:
                kh = kh_bc
            elif ih_ba < ih_bc:
                n_ba += 1
                ih = ih_ba
                jh = jh_ba
                if tag_bc == "E":
                    kh = kh_bc - (ih_bc - ih_ba)
                elif kh_bc == kl_bc:
                    kh = kh_bc
                else:
                    kh = None  # undecided
                    tag = "N"
            if jh is not None and kh is not None:
                if tag == "N":
                    if a[jl:jh] == c[kl:kh]:
                        tag = "e"
                answer.append((tag, jl, jh, il, ih, kl, kh))
                il = ih
                jl = jh
                kl = kh
                tag = ""
        self.chunks = answer
        return answer


if __name__ == "__main__":
    import doctest

    doctest.testmod()
