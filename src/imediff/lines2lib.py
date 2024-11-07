#!/usr/bin/python3
# vim:se tw=78 sw=4 sts=4 ts=4 et ai si ft=python fileencoding=utf-8 :

"""
Module lines2lib -- matching 2 lines library

Copyright (C) 2018--2024 Osamu Aoki <osamu@debian.org>

"""
from difflib import SequenceMatcher

import re
import sys
import logging

logger = logging.getLogger(__name__)


class LineMatcher:
    """
    Linematcher

    A public class to help manage 2 lists of similar lines by finding fuzzy
    matching of filtered lines. This fuzzy matching of filtered lines is
    controlled by the line_rule value.

    line_rule   pattern    -- filtering behavior
         0      r""        -- drop none between text, but strip
         1      r"\s+"     -- drop all whitespaces
         2      r"[\s\"']" -- drop all whitespaces and quotes (default)
         3      r"\W+"     -- drop all non-alphanumerics

         10     r""        -- drop none between text, but strip and lowercase
         11     r"\s+"     -- drop all whitespaces and lowercase
         12     r"[\s\"']" -- drop all whitespaces and quotes and lowercase
         13     r"\W+"     -- drop all non-alphanumerics and lowercase

    The fuzzy matching is performed on partial match of head and tail portion
    of lines provided by _LineMatcher class.  This partial match is controlled
    by 3 parametrs:

    parameters
    * line_max     -- initial length to compare (upper limit, defalt=128)
    * line_min     -- final   length to compare (lower limit, default=1)
    * line_factor  -- length shortening factor (default=8 for x0.8)

    The resulting tag from Linematcher class object are:

    * 'E' ----------------------- for a[j1:j2] == b[i1:i2] -- exact match
    * 'N' ----------------------- for a[j1:j2] != b[i1:i2] -- no match
    * 'F' ----------------------- for a[j1:j2] != b[i1:i2] -- fuzzy match

    Example:
    >>> a = [   "line 1 abcde\\n",
    ...         "line 2 qazws\\n",
    ...         "line 3 edcrf\\n",
    ...         "line 4 tgbyh\\n",
    ...         "line 5 yhnuj\\n",
    ...         "line 6 ujmik\\n",
    ...         "line 7 olpvb\\n",
    ...         "line 8 abcde\\n",
    ...         "line 9 olpvb\\n",
    ...         "line 0 abcde\\n",
    ...         "line 0 abcde\\n",
    ...         "line A olpvb\\n",
    ...         "line B abcde\\n",
    ...         "line Z abcde\\n",
    ...     ]
    >>> b = [   "line 1 abcde\\n",
    ...         " line 2 qazws XXX\\n",
    ...         "  line 3 e dcrf\\n",
    ...         "  line 4 tgbyh\\n",
    ...         "   line 5  yhnuj\\n",
    ...         "   line 6  uj mik\\n",
    ...         "line 7 olpvb\\n",
    ...         "   line 8 abc\\n",
    ...         "   line X XXX\\n",
    ...         "   line X XXX\\n",
    ...         "ine  9 olp vb\\n",
    ...         " l ine  0 abc\\n",
    ...         " line A  olpv b\\n",
    ...         "B  abc\\n",
    ...         "l i n e Z 'a b c d' \\\"e\\n",
    ...     ]
    >>> lines = LineMatcher(a, b)
    >>> lines._dump_opcodes()
    match: 0 -> 0, tag = E
        a: line 1 abcde
        b: line 1 abcde
    match: 1 -> 1, tag = F
        a: line 2 qazws
        b:  line 2 qazws XXX
    match: 2 -> 2, tag = F
        a: line 3 edcrf
        b:   line 3 e dcrf
    match: 3 -> 3, tag = F
        a: line 4 tgbyh
        b:   line 4 tgbyh
    match: 4 -> 4, tag = F
        a: line 5 yhnuj
        b:    line 5  yhnuj
    match: 5 -> 5, tag = F
        a: line 6 ujmik
        b:    line 6  uj mik
    match: 6 -> 6, tag = E
        a: line 7 olpvb
        b: line 7 olpvb
    match: 7 -> 7, tag = F
        a: line 8 abcde
        b:    line 8 abc
    UNmatch: 8:8 -> 8:10, tag = N
    match: 8 -> 10, tag = F
        a: line 9 olpvb
        b: ine  9 olp vb
    match: 9 -> 11, tag = F
        a: line 0 abcde
        b:  l ine  0 abc
    UNmatch: 10:11 -> 12:12, tag = N
    match: 11 -> 12, tag = F
        a: line A olpvb
        b:  line A  olpv b
    match: 12 -> 13, tag = F
        a: line B abcde
        b: B  abc
    match: 13 -> 14, tag = F
        a: line Z abcde
        b: l i n e Z 'a b c d' "e
    """

    def __init__(
        self,
        a=[],
        b=[],
        line_rule=2,
        line_max=128,  # initial length to compare (upper limit)
        line_min=1,  # final   length to compare (lower limit)
        line_factor=8,  # length shortening factor
        # 8 for 80% of length_before every 2 steps
    ):
        """
        Construct a LineMatcher object using whitespace filtered object and _LineMatcher internal object
        class which find matches including partial matches

        """

        # initialize
        self.a = a
        self.b = b
        if not (line_rule >= 0 and line_rule < 20):
            logger.error(
                "E: line_rule should be between 0 and 19 but {}".format(line_rule)
            )
            sys.exit(2)
        # line_rule:
        # 0      r""        -- drop none between text, but strip
        # 1      r"\s+"     -- drop all whitespaces
        # 2      r"[\s\"']" -- drop all whitespaces and quotes (default)
        # 3      r"\W+"     -- drop all non-alphanumerics
        # 10     r""        -- drop none between text, but strip and lowercase
        # 11     r"\s+"     -- drop all whitespaces and lowercase
        # 12     r"[\s\"']" -- drop all whitespaces and quotes and lowercase
        # 13     r"\W+"     -- drop all non-alphanumerics and lowercase
        if (line_rule % 10) == 0:
            re_preform = re.compile(r"")
        elif (line_rule % 10) == 1:
            re_preform = re.compile(r"\s+")
        elif (line_rule % 10) == 2:
            re_preform = re.compile(r"[\s\"']+")
        elif (line_rule % 10) == 3:
            re_preform = re.compile(r"\W+")
        else:
            re_preform = re.compile(r"")
        self.a_int = []
        for ax in a:
            if line_rule < 10:
                filtered_ax = re_preform.sub("", ax).strip()
            else:
                filtered_ax = re_preform.sub("", ax).strip().lower()
            self.a_int.append(filtered_ax)
        self.b_int = []
        for bx in b:
            if line_rule < 10:
                filtered_bx = re_preform.sub("", bx).strip()
            else:
                filtered_bx = re_preform.sub("", bx).strip().lower()
            self.b_int.append(filtered_bx)
        self.int = _LineMatcher(
            self.a_int,
            self.b_int,
            0,
            len(self.a_int),
            0,
            len(self.b_int),
            line_max=line_max,
            line_min=line_min,
            line_factor=line_factor,
        )

    def get_opcodes(self):
        match = []
        for tag, i1, i2, j1, j2 in self.int.get_opcodes():
            # this is match for self.int only
            if tag == "E":
                if self.a[i1] == self.b[j1]:
                    # real exact match
                    tag = "E"
                else:
                    # match after filter is fuzzy match
                    tag = "F"
            match.append((tag, i1, i2, j1, j2))
        return match

    def _dump_opcodes(self):
        """
        private function to dump internal data state of class object for
        LineMatcher class
        """
        for tag, i1, i2, j1, j2 in self.get_opcodes():
            if (i1 + 1) == i2 and (j1 + 1) == j2:
                print("match: {} -> {}, tag = {}".format(i1, j1, tag))
                print("    a: {}".format(self.a[i1]).rstrip())
                print("    b: {}".format(self.b[j1]).rstrip())
            else:
                print("UNmatch: {}:{} -> {}:{}, tag = {}".format(i1, i2, j1, j2, tag))


class _LineMatcher:
    """
    _LineMatcher

    A private class to help manage 2 lists of similar lines by finding
    matching lines including partial line matches.

    Example:
    >>> a = [   "line1abcde",
    ...         "line2qazws",
    ...         "line3edcrf",
    ...         "line4tgbyh",
    ...         "line5yhnuj",
    ...         "line6ujmik",
    ...         "line7olpvb",
    ...         "line8abcde",
    ...         "line9olpvb",
    ...         "line0abcde",
    ...         "line0abcde",
    ...         "lineAolpvb",
    ...         "lineBabcde",
    ...         "lineZabcde",
    ...     ]
    >>> b = [   "line1abcde",
    ...         "line2qazwsx",
    ...         "line3edcrf",
    ...         "line4tgbyhx",
    ...         "line5yhnuj",
    ...         "line6ujmikz",
    ...         "line7olpvb",
    ...         "line8abcdez",
    ...         "line9olpvb",
    ...         "line0abcde",
    ...         "line0abcdexx",
    ...         "lineAolpvb",
    ...         "lineBabcde",
    ...         "lineZabcdex",
    ...     ]
    >>> lines = _LineMatcher(a, b, 0, len(a), 0, len(b))
    >>> lines._dump_opcodes()
    match: 0 -> 0, tag = E
        a: line1abcde
        b: line1abcde
    match: 1 -> 1, tag = F
        a: line2qazws
        b: line2qazwsx
    match: 2 -> 2, tag = E
        a: line3edcrf
        b: line3edcrf
    match: 3 -> 3, tag = F
        a: line4tgbyh
        b: line4tgbyhx
    match: 4 -> 4, tag = E
        a: line5yhnuj
        b: line5yhnuj
    match: 5 -> 5, tag = F
        a: line6ujmik
        b: line6ujmikz
    match: 6 -> 6, tag = E
        a: line7olpvb
        b: line7olpvb
    match: 7 -> 7, tag = F
        a: line8abcde
        b: line8abcdez
    match: 8 -> 8, tag = E
        a: line9olpvb
        b: line9olpvb
    match: 9 -> 9, tag = E
        a: line0abcde
        b: line0abcde
    match: 10 -> 10, tag = F
        a: line0abcde
        b: line0abcdexx
    match: 11 -> 11, tag = E
        a: lineAolpvb
        b: lineAolpvb
    match: 12 -> 12, tag = E
        a: lineBabcde
        b: lineBabcde
    match: 13 -> 13, tag = F
        a: lineZabcde
        b: lineZabcdex
    """

    def __init__(
        self,
        a=[],
        b=[],
        is1=0,
        is2=0,
        js1=0,
        js2=0,
        depth=0,  # used to track recursive call to _LineMatcher-class
        line_max=128,  # initial length to compare (upper limit)
        line_min=1,  # final   length to compare (lower limit)
        line_factor=8,  # length shortening factor
        # 8 for 80% of length_before every 2 steps
    ):
        """
        Construct a _LineMatcher

        """

        # initialize
        self.a = a
        self.b = b
        self.is1 = is1
        self.is2 = is2
        self.js1 = js1
        self.js2 = js2
        self.depth = depth
        self.line_min = line_min
        self.line_factor = line_factor
        maxlen = 0
        for i in range(is1, is2):
            len_a = len(a[i])
            if len_a > maxlen:
                maxlen = len_a
        for j in range(js1, js2):
            len_b = len(b[j])
            if len_b > maxlen:
                maxlen = len_b
        self.line_max = min(line_max, maxlen // 2)

    def get_opcodes(self):
        if self.depth == 0:  # depth = 0
            side = 0
            logger.debug(
                "{}_LineMatcher ===  a[{}:{}]/b[{}:{}]  ===  line_full[:]  ===".format(
                    "    " * self.depth, self.is1, self.is2, self.js1, self.js2
                ),
            )
        elif self.depth > 0:  # depth > 0
            if self.depth % 2 == 1:  # depth = 1, 3, 5, ...
                side = +1
                logger.debug(
                    "{}_LineMatcher ===  a[{}:{}]/b[{}:{}]  ===  line_head[:{:02d}] ===".format(
                        "    " * self.depth,
                        self.is1,
                        self.is2,
                        self.js1,
                        self.js2,
                        self.line_max,
                    ),
                )
            else:  # self.depth % 2 == 0:  # depth = 2, 4, 6, ...
                side = -1
                logger.debug(
                    "{}_LineMatcher ===  a[{}:{}]/b[{}:{}]  ===  line_tail[-{:02d}:] ===".format(
                        "    " * self.depth,
                        self.is1,
                        self.is2,
                        self.js1,
                        self.js2,
                        self.line_max,
                    ),
                )
        else:
            logger.error(
                "{}_LineMatcher ===  a[{}:{}]/b[{}:{}]  ===  depth should not be negative".format(
                    "!!!!" * self.depth, self.is1, self.is2, self.js1, self.js2
                )
            )
            sys.exit(2)
        if side == 0:
            # self.is1, self.is2, self.js1, self.js2 are known to cover all
            side_id = "full"
            am = self.a
            bm = self.b
        elif side == 1:  # left side match (odd-depth)
            side_id = "head"
            am = []
            bm = []
            for i in range(self.is1, self.is2):
                am.append(self.a[i][: self.line_max])
            for j in range(self.js1, self.js2):
                bm.append(self.b[j][: self.line_max])
        else:  # side == -1, right side match (even-depth)
            side_id = "tail"
            am = []
            bm = []
            for i in range(self.is1, self.is2):
                am.append(self.a[i][-self.line_max :])
            for j in range(self.js1, self.js2):
                bm.append(self.b[j][-self.line_max :])
        for i in range(self.is1, self.is2):
            logger.debug(
                "{}_LineMatcher_filter a[{}] -> {}:am[{}]='{}'".format(
                    "    " * self.depth, i, side_id, i - self.is1, am[i - self.is1]
                ),
            )
        for j in range(self.js1, self.js2):
            logger.debug(
                "{}_LineMatcher_filter b[{}] -> {}:bm[{}]='{}'".format(
                    "    " * self.depth, j, side_id, j - self.js1, bm[j - self.js1]
                ),
            )
        seq = SequenceMatcher(None, am, bm)
        match = []
        for tag, i1, i2, j1, j2 in seq.get_opcodes():
            logger.debug(
                "{}<< SequenceMatcher_tag={}  ===  a[{}:{}]/b[{}:{}]".format(
                    "    " * self.depth,
                    tag,
                    i1 + self.is1,
                    i2 + self.is1,
                    j1 + self.js1,
                    j2 + self.js1,
                ),
            )
            ip1 = self.is1 + i1
            ip2 = self.is1 + i2
            jp1 = self.js1 + j1
            jp2 = self.js1 + j2
            if tag == "equal":
                # multi line section and equal for filtered lines
                for i in range(i1, i2):
                    ip = self.is1 + i
                    jp = self.js1 + (i - i1) + j1
                    if side == 0:
                        # full match on filtered line
                        match.append(("E", ip, ip + 1, jp, jp + 1))
                        logger.debug(
                            "{}>> _LineMatcher_tag=E  ===  a[{}:{}]/b[{}:{}]  === full match".format(
                                "    " * self.depth, ip, ip + 1, jp, jp + 1
                            ),
                        )
                    else:
                        # partial match only (F for fuzzy)
                        match.append(("F", ip, ip + 1, jp, jp + 1))
                        logger.debug(
                            "{}>> _LineMatcher_tag=F  ===  a[{}:{}]/b[{}:{}]  === fuzzy match".format(
                                "    " * self.depth, ip, ip + 1, jp, jp + 1
                            ),
                        )
            elif i1 == i2 or j1 == j2:
                # delete "a" or delete "b" for filtered lines
                match.append(("N", ip1, ip2, jp1, jp2))
                logger.debug(
                    "{}>> _LineMatcher_tag=N  ===  a[{}:{}]/b[{}:{}]  === delete one side".format(
                        "    " * self.depth, ip1, ip2, jp1, jp2
                    ),
                )
            elif (i1 + 1) == i2 and (j1 + 1) == j2:
                # single line match -> assume fuzzy match without checking
                # even though this is not equal
                match.append(("F", ip1, ip2, jp1, jp2))
                logger.debug(
                    "{}>> _LineMatcher_tag=N  ===  a[{}:{}]/b[{}:{}]  === fuzzy non-match (single line)".format(
                        "    " * self.depth, ip1, ip2, jp1, jp2
                    ),
                )
            else:  # fuzzy match was not resolved
                # dig deeper for multi-line changes to find fuzzy matches
                if side == 0:  # full
                    # full -> left side
                    logger.debug(
                        "{}>> _LineMatcher_tag=?  ===  a[{}:{}]/b[{}:{}]  === dig deeper depth={} from full".format(
                            "    " * self.depth, ip1, ip2, jp1, jp2, self.depth + 1
                        ),
                    )
                    match.extend(
                        _LineMatcher(
                            a=self.a,
                            b=self.b,
                            is1=ip1,
                            is2=ip2,
                            js1=jp1,
                            js2=jp2,
                            line_max=self.line_max,
                            depth=self.depth + 1,
                        ).get_opcodes()
                    )
                elif side == +1:  # head side
                    # left side -> right side
                    logger.debug(
                        "{}>> _LineMatcher_tag=?  ===  a[{}:{}]/b[{}:{}]  === dig deeper depth={} from full/tail".format(
                            "    " * self.depth, ip1, ip2, jp1, jp2, self.depth + 1
                        ),
                    )
                    match.extend(
                        _LineMatcher(
                            a=self.a,
                            b=self.b,
                            is1=ip1,
                            is2=ip2,
                            js1=jp1,
                            js2=jp2,
                            line_max=self.line_max,
                            depth=self.depth + 1,
                        ).get_opcodes()
                    )
                elif self.line_max > self.line_min:  # tail side: side == -1
                    # right side -> left side (shorter)
                    logger.debug(
                        "{}>> _LineMatcher_tag=?  ===  a[{}:{}]/b[{}:{}]  === dig deeper depth={} from tail with shorter line_max ={}".format(
                            "    " * self.depth,
                            ip1,
                            ip2,
                            jp1,
                            jp2,
                            self.depth + 1,
                            self.line_max * self.line_factor // 10,
                        ),
                    )
                    match.extend(
                        _LineMatcher(
                            a=self.a,
                            b=self.b,
                            is1=ip1,
                            is2=ip2,
                            js1=jp1,
                            js2=jp2,
                            line_max=self.line_max * self.line_factor // 10,
                            depth=self.depth + 1,
                        ).get_opcodes()
                    )
                else:
                    # no more shorter, give up as multi-line block change
                    logger.debug(
                        "{}>> _LineMatcher_tag=N  ===  a[{}:{}]/b[{}:{}]  === no more depth with line_max {} <= line_min {}".format(
                            "    " * self.depth,
                            ip1,
                            ip2,
                            jp1,
                            jp2,
                            self.line_max,
                            self.line_min,
                        ),
                    )
                    match.append(
                        (
                            "N",
                            ip1,
                            ip2,
                            jp1,
                            jp2,
                        )
                    )
        return match

    def _dump_opcodes(self):
        """
        private function to dump internal data state of class object for
        _LineMatcher class
        """
        for tag, i1, i2, j1, j2 in self.get_opcodes():
            if (i1 + 1) == i2 and (j1 + 1) == j2:
                print("match: {} -> {}, tag = {}".format(i1, j1, tag))
                print("    a: {}".format(self.a[i1]))
                print("    b: {}".format(self.b[j1]))
            else:
                print("UNmatch: {}:{} -> {}:{}, tag = {}".format(i1, i2, j1, j2, tag))


if __name__ == "__main__":
    import doctest

    flags = doctest.REPORT_NDIFF | doctest.FAIL_FAST
    fail, total = doctest.testmod(optionflags=flags)
    print("{} failures out of {} tests -- ".format(fail, total), end="")
    if fail == 0:
        sys.exit(0)
    else:
        sys.exit(1)
