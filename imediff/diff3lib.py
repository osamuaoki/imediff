#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
Module diff3lib -- wrapper for diff3

Class SequenceMatcher3:
    A flexible class for comparing 3 of sequences of any type.

Copyright (C) 2018       Osamu Aoki <osamu@debian.org>

This is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2,
or (at your option) any later version.

This is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public
License along with the program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import sys

from imediff.diff2lib import SequenceMatcher2
from imediff.utils import *

class SequenceMatcher3:

    """
    SequenceMatcher3 is a matching class for comparing three of sequences of
    any type, so long as the sequence elements are hashable.

    Let's call these three sequences as A (yours), B (old), and C (theirs).
    Then let's call concatenated A+B+C with separator string as D (diff).
    The rule for the merging of three of sequences is as follows:

    * Check B-A matching and B-C matching situation.
    * Walk through the ranges of B-A matching and B-C matching on b
      There are 12 basic cases.

    CASE NEEE            EENE
     BA  NNNEEE          EEENNN        
     BC  EEEEEE          EEEEEE        
         AF ^            EF ^        

    CASE NNEE    NNNE    ENNE    ENEE
     BA  NNNEEE  NNNNNN  EEENNN  EEEEEE
     BC  NNNEEE  NNNEEE  NNNEEE  NNNEEE
         XF*^    X- ^    CF ^    CF ^

    CASE NEEN    NENN    EENN    EEEN
     BA  NNNEEE  NNNNNN  EEENNN  EEEEEE
     BC  EEENNN  EEENNN  EEENNN  EEENNN
         AF ^    X- ^    EF*^    EF ^

    CASE NNEN            ENNN 
     BA  NNNEEE          EEENNN        
     BC  NNNNNN          NNNNNN        
         X- ^            X- ^

    * If CASE EENN is followed by NNEE, then check A-C between these
      checkpoints being identical or not.  If Match, change XF* to eF,
      otherwise treat it as XF for previous match is EENN. (Not for NENN nor
      ENNN)
    * If AF or CF follows unfinalized X-, Make them as finalized XF.

    This requires diff2lib which is a wrapper of difflib and provides
    'get_chunks' method.

    Example, comparing two strings, and considering blanks to be "junk":

    >>> a = "private Thread currentThread foo bar;"
    >>> b = "private volatile Thread currentThread;"
    >>> c = "private volatile currentThread foo;"
    >>> s = SequenceMatcher3(lambda x: x == " ", a, b, c)
    >>>

    If you want to know how to change the first sequence into the second,
    use .get_chunks():

    >>> for tag, i1, i2, j1, j2, k1, k2 in s.get_chunks():
    ...     print("%1s a[%d:%d],b[%d:%d],c[%d:%d] => '%s', '%s', '%s'" % (
    ...     tag, i1, i2, j1, j2, k1, k2, a[i1:i2], b[j1:j2], c[k1:k2]))
    ...
    E a[0:6],b[0:6],c[0:6] => 'privat', 'privat', 'privat'
    A a[6:6],b[6:15],c[6:15] => '', 'e volatil', 'e volatil'
    E a[6:8],b[15:17],c[15:17] => 'e ', 'e ', 'e '
    C a[8:15],b[17:24],c[17:17] => 'Thread ', 'Thread ', ''
    E a[15:28],b[24:37],c[17:30] => 'currentThread', 'currentThread', 'currentThread'
    N a[28:36],b[37:37],c[30:34] => ' foo bar', '', ' foo'
    E a[36:37],b[37:38],c[34:35] => ';', ';', ';'

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

    def __init__(self, isjunk=None, a='', b='', c='', autojunk=True):
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
        ...    print(("%1s a[%d:%d] (%s) / b[%d:%d] (%s) / c[%d:%d] (%s)" %
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
        sm_ba = SequenceMatcher2(self.isjunk, b, a)
        sm_bc = SequenceMatcher2(self.isjunk, b, c)
        chunks_ba = sm_ba.get_chunks()
        chunks_bc = sm_bc.get_chunks()
        diff3 = list()
        i_ba = 0 # walking index
        i_bc = 0 # walking index
        i_bax = i_ba # walking index
        i_bcx = i_bc # walking index
        il = jl = kl = 0 # range lower end for b, a, c (next in next round)
        ilx = jlx = klx = 0 # range lower end for b, a, c (previous)
        ih = jh = kh = 0 # range higher end for b, a, c (used in next round)
        ihx = jhx = khx = 0 # range higher end for b, a, c (previous)
        il_ba = ih_ba = jl_ba = jh_ba = il_bc = ih_bc = kl_bc = kh_bc = 0
        len_ba = len(chunks_ba)
        len_bc = len(chunks_bc)
        answer = list()
        tag = "*"
        tag_ba = tag_bc = '*'
        tagset = "****"
        side = "BA+BC"
        while True:
            # preserve previous values
            tag_bax = tag_ba
            il_bax = il_ba
            ih_bax = ih_ba
            jl_bax = jl_ba
            jh_bax = jh_ba
            tag_bcx = tag_bc
            il_bcx = il_bc
            ih_bcx = ih_bc
            kl_bcx = kl_bc
            kh_bcx = kh_bc
            # get a chunk data
            #logger.debug("diff3lib: i_ba={} i_bc={} len_ba={} len_bc={}".format(i_ba, i_bc, len_ba, len_bc))
            if len(chunks_ba):
                (tag_ba, il_ba, ih_ba, jl_ba, jh_ba) = chunks_ba[i_ba]
            else:
                (tag_ba, il_ba, ih_ba, jl_ba, jh_ba) = ("E", 0, 0, 0, 0)
            if len(chunks_bc):
                (tag_bc, il_bc, ih_bc, kl_bc, kh_bc) = chunks_bc[i_bc]
            else:
                (tag_bc, il_bc, ih_bc, kl_bc, kh_bc) = ("E", 0, 0, 0, 0)
            tagsetx = tagset
            tagset = tag_bax + tag_bcx + tag_ba + tag_bc
            # preserve previous values
            i_bax = i_ba
            i_bcx = i_bc
            ihx = ih
            jhx = jh
            khx = kh
            # Get new values
            #
            #  BA  ...EEENNN...
            #  BC  ...EEENNN...
            #      EF    ^
            if tagset == 'EENN':
                # Finalize step
                ih = il_ba # = il_bc
                jh = jl_ba
                kh = kl_bc
                tag = "E"
                finalized = True
            #  BA  ...EEEEEE...
            #  BC  ...EEENNN...
            #      EF    ^
            elif tagset == 'EEEN':
                # Finalize step
                ih = il_bc
                jh = jl + ih - ihx
                kh = kl_bc
                tag = "E"
                finalized = True
            #  BA  ...EEENNN...
            #  BC  ...EEEEEE...
            #      EF    ^
            elif tagset == 'EENE':
                # Finalize step
                ih = il_ba
                jh = jl_ba
                kh = kl + ih - ihx
                if tag == "N":
                    tag = "N"
                elif tag == "A":
                    tag = "A"
                elif tag == "C":
                    tag = "C"
                else:
                    tag = "E"
                finalized = True
            #  BA  ...NNNEEE...
            #  BC  ...EEEEEE...
            #      AF    ^
            elif tagset == 'NEEE':
                # Finalize step
                ih = il_ba
                jh = jl_ba
                kh = kl + ih - ihx
                if tag == "N":
                    tag = "N"
                else:
                    tag = "A"
                finalized = True
            #  BA  ...NNNEEE...
            #  BC  ...EEENNN...
            #      AF    ^
            elif tagset == 'NEEN':
                # Finalize step
                ih = il_ba # = il_bc
                jh = jl_ba
                kh = kl_bc
                if tag == "N":
                    tag = "N"
                else:
                    tag = "A"
                finalized = True
            #  BA  ...EEENNN...
            #  BC  ...NNNEEE...
            #      CF    ^
            elif tagset == 'ENNE':
                # Finalize step
                ih = il_ba # = il_bc
                jh = jl_ba
                kh = kl_bc
                if tag == "N":
                    tag = "N"
                else:
                    tag = "C"
                finalized = True
            #  BA  ...EEEEEE...
            #  BC  ...NNNEEE...
            #      CF    ^
            elif tagset == 'ENEE':
                # Finalize step
                ih = il_bc
                jh = jl + ih - ihx
                kh = kl_bc
                if tag == "N":
                    tag = "N"
                else:
                    tag = "C"
                finalized = True
            #  BA  ...NNNEEE...
            #  BC  ...NNNEEE...
            #      NF*   ^
            elif tagset == 'NNEE':
                # Finalize step
                ih = il_ba # = il_bc
                jh = jl_ba
                kh = kl_bc
                if tagsetx == "EENN" and a[jl_bax:jh_bax] == c[kl_bcx:kh_bcx]:
                    tag = "e" # Exact same change happened on A and C 
                else:
                    tag = "N"
                finalized = True
            #  BA  ...NNNNNN...  ...NNNNNN...  ...NNNEEE...  ...EEENNN...
            #  BC  ...NNNEEE...  ...EEENNN...  ...NNNNNN...  ...NNNNNN...
            #      N-    ^             ^
            elif tagset == 'NNNE' or tagset == 'NENN' or tagset == 'NNEN' or tagset == 'ENNN':
                finalized = False
                tag = "N"
            #  BA  EEE... NNN... EEE...
            #  BC  EEE... EEE... NNN...
            #      ^      ^      ^
            elif jl_ba == 0 and kl_bc == 0 and il_ba == il_bc:
                if jh_ba == 0 and kh_bc == 0:
                    finalized = True
                    tag = "e"
                elif jh_ba == 0:
                    finalized = True
                    tag = "C"
                elif kh_bc == 0:
                    finalized = True
                    tag = "A"
                elif tagset == '**EE' or tagset == '**NE' or tagset == '**EN':
                    finalized = False
                    tag = "*"
                elif tagset == '**NN':
                    finalized = True
                    tag = "N"
                else:
                    finalized = False
                    print(">>> START ERROR >>>")
                    sys.exit(3)
            else:
                finalized = False
                print(">>> ERROR IN ELSE >>>")
                sys.exit(3)
            #print("=== final={} tag={} side={} ===".format(finalized, tag, side))
            #print("    BA i_bax=%i i_ba=%i tagset=%s picked b[%i:%i]='%s' a[%i:%i]='%s'" % (i_bax, i_ba, tagset, il, ih, b[il:ih], jl, jh, a[jl:jh]))
            #print("    BC i_bcx=%i i_bc=%i tagset=%s picked b[%i:%i]='%s' c[%i:%i]='%s'" % (i_bcx, i_bc, tagset, il, ih, b[il:ih], kl, kh, c[kl:kh]))
            if finalized:
                if not (jl == 0 and jh == 0 and 
                        il == 0 and ih == 0 and 
                        kl == 0 and kh == 0):
                    answer.append((tag, jl, jh, il, ih, kl, kh))
                # Set lower bound for next step
                il = ih
                jl = jh
                kl = kh
                tag = "*"
            # End loop at the end
            if i_ba >= len_ba - 1 and i_bc >= len_bc - 1:
                finalized = True # Force finalize at the end
                ih = ih_ba # = ih_bc
                jh = jh_ba
                kh = kh_bc
                if tagset[-2:] == 'EN':
                    if tag == "N":
                        tag = "N"
                    else:
                        tag = "C" # C has trailing string
                elif tagset[-2:] == 'NE':
                    if tag == "N":
                        tag = "N"
                    else:
                        tag = "A" # A has trailing string
                elif tagset[-2:] == 'NN':
                    if a[jl_ba:jh_ba] == c[kl_bc:kh_bc]:
                        tag = "e" # Exact same change happened on A and C 
                    else:
                        tag = "N"
                elif tagset[-2:] == 'EE':
                    tag = "E"
                else:
                    print(">>> BREAK ERROR >>> tagset={}".format(tagset))
                    sys.exit(3)
                break
            # Walk to next chunk
            if ih_ba > ih_bc:
                #print('walk BC side chunk[%i] from b[%i:%i]=%s to next' % (i_bc, il_bc, ih_bc, b[il_bc:ih_bc]))
                i_bc += 1
                side = "BC"
            elif ih_ba < ih_bc:
                #print('walk BA side chunk[%i] from b[%i:%i]=%s to next' % (i_ba, il_ba, ih_ba, b[il_ba:ih_ba]))
                i_ba += 1
                side = "BA"
            else: # ih_ba == ih_bc
                #print('walk BA+BC side chunk[BA=%i, BC=%i] from b[%i:%i]=%s to next' % (i_ba, i_bc, il_ba, ih_ba, b[il_ba:ih_ba]))
                i_ba += 1
                i_bc += 1
                side = "BA+BC"
                if i_ba > len_ba -1:
                    i_ba = len_ba -1
                    side = "BC-last"
                if i_bc > len_bc -1:
                    i_bc = len_bc -1
                    side = "BA-last"
            if i_ba > len_ba -1 or i_bc > len_bc -1:
                print(">>>> ERROR >>>>")
                sys.exit(3)
        # Finalize step
        #print("=== out of loop final={} tag={} side={} ===".format(finalized, tag, side))
        #print("    BA i_bax=%i i_ba=%i tagset=%s ending b[%i:%i]='%s' a[%i:%i]='%s'" % (i_bax, i_ba, tagset, il, ih, b[il:ih], jl, jh_ba, a[jl:jh]))
        #print("    BC i_bcx=%i i_bc=%i tagset=%s ending b[%i:%i]='%s' c[%i:%i]='%s'" % (i_bcx, i_bc, tagset, il, ih, b[il:ih], kl, kh, c[kl:kh]))
        answer.append((tag, jl, jh, il, ih, kl, kh))
        self.chunks = answer
        return answer

if __name__ == '__main__':
    import doctest
    doctest.testmod()
