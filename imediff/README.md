# Note on delta, diff2, diff3, merge, ...

I am no expert on this subject of computing delta.

I collected readily available information on the web for my reference and
summarized as my reminders.

I also documented history and feature of `imediff`.

Here, I use shorthand as follows:

 * diff2: delta of 2 data
 * diff3: delta of 3 data

## Computing deltas

Algorithm of computing delta seems to be non-trivial one since it is a NP-hard
problem.

There seem to be several algorithms for computing deltas:

  * https://en.wikipedia.org/wiki/Diff

## Python difflib for diff2

The python offers `diflib` as a standard library for computing deltas

  * https://docs.python.org/3/library/difflib.html

This is based on an extended Ratcliff and Obershelp algorithm.  The idea is to
find the longest contiguous matching subsequence that contains no “junk”
element.  As for longest contiguous matching subsequence, see:

  * https://en.wikipedia.org/wiki/Longest_common_subsequence_problem
  * John W. Ratcliff and David Metzener, Pattern Matching: The Gestalt
    Approach, Dr. Dobb's Journal, page 46, July 1988.
  * https://xlinux.nist.gov/dads/HTML/ratcliffObershelp.html
  * PATTERN MATCHING: THE GESTALT APPROACH: https://collaboration.cmc.ec.gc.ca/science/rpn/biblio/ddj/Website/articles/DDJ/1988/8807/8807c/8807c.htm

## Alternative algorithms for diff2

I found several interesting blogs and source codes examples.

* susisu
  * 差分検出アルゴリズム三種盛り (javascript)
    https://susisu.hatenablog.com/entry/2017/10/09/134032
* Wikibooks: Algorithm Implementation
  * Levenshtein distance
    https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance
  * Longest common subsequence
    https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_subsequence
* Tociyuki (perl `diff3` author)
  * Heckel 法による diff プログラム
    https://tociyuki.hatenablog.jp/entry/20141209/1418117214
  * Hirschberg 法 - Myers による O(ND) テキスト差分
    https://tociyuki.hatenablog.jp/entry/20150330/1427683909
  * またもや Heckel 法による diff プログラム
    https://tociyuki.hatenablog.jp/entry/20151201/1448942936
  * Hirschberg-Wu 法による diff プログラム
    https://tociyuki.hatenablog.jp/entry/20151203/1449158483
  * Hirschberg-Wu 法による diff プログラム改良版
    https://tociyuki.hatenablog.jp/entry/20151207/1449474412
  * テキスト差分 Wu によるO(NP) 法の Hirschberg 法化まとめ
    https://tociyuki.hatenablog.jp/entry/20170526/1495801840
  * Simple variant of diff(1) program
    https://gist.github.com/tociyuki/09eae66a6650b5f7defc
  * word based unified color differences between two texts (The BSD 3-Clause)
    https://github.com/tociyuki/udiff-cxx11
* Neil Bowers
  * Text-Diff-1.45 12 ++ / Text::Diff (License: perl_5)
    https://metacpan.org/pod/Text::Diff
    https://github.com/neilb/Text-Diff
* Tye McQueen
  * Algorithm-Diff-1.1903 19 ++ / Algorithm::Diff
    https://metacpan.org/pod/Algorithm::Diff
* Paul Heckel -- see next section
* http://wiki.c2.com/?DiffAlgorithm

These were too much to digest but there seems to be newer algorithm than one
used in Python library for diff2.

  * unified format diff between texts line by line with Wu's O(NP) and Hirschberg's linear space method in C++11
    https://gist.github.com/tociyuki/acedd33ca4913f1ab8e9

Addition of this may be TODO for post 2.0 sources.  But for now, too much work.
python standard library is fast enough.

## Paul Heckel's diff algorithm for diff2

  * Paul Heckel (April 1978). "A technique for isolating differences between files"
    * http://documents.scribd.com/docs/10ro9oowpo1h81pgh1as.pdf
  * https://gist.github.com/ndarville/3166060
  * https://stackoverflow.com/questions/42755035/difficulty-understanding-paul-heckels-diff-algorithm
  * https://www.npmjs.com/package/heckel-diff
  * https://github.com/mcudich/HeckelDiff/blob/master/Source/Diff.swift
  * https://johnresig.com/projects/javascript-diff-algorithm/
    * https://johnresig.com/files/jsdiff.js
    * https://github.com/ndarville/jsdiff/blob/master/jsdiff.js

## Algorithms for diff3

When I searched for `diff3` implemented in python, I found `diff3.py`.

  * https://github.com/cmake-basis/BASIS/blob/master/src/utilities/python/diff3.py
  * https://github.com/schuhschuh/cmake-basis/blob/master/src/utilities/python/diff3.py
  * http://www.nmr.mgh.harvard.edu/~you2/dramms/dramms-1.4.3-source/build/bundle/src/BASIS/src/utilities/python/diff3.py

All these are based on Perl code by MIZUTANI Tociyuki

  * https://metacpan.org/pod/Text::Diff3
    MIZUTANI, Tociyuki  /   ￼Text-Diff3-0.10  ++  / Text::Diff3

I initially tried to use above `diff3.py`.  I may have broke code when adopting
it, but I didn't get right answer when delta existed at the tail ends.  This
code was transcoded from perl to python and used one-dimensional array `d2` to
hold 2-dimensional data.  This odd python code was difficult to understand and
debug.  I gave up fixing this initial trial.

```
d2 = (diff(origtext, yourtext), diff(origtext, theirtext))
```

From `diff3.py`, I took the basic idea of combining 2 diff2 data to make diff3
data.  After my second trial to write my own diff3, I made decent success
verified with accompanied test codes.  I released `diff3lib.py` as a part of
`imediff` version 2.0.  My `diff3lib.py` code is not a derivative work of
`diff3.py`.  (I suspect these may be mostly logically equivalent.  But I didn't
check again.)

Now that I wrote working code, the following paper started to make some sense.
It may be good idea to reread this.  (I wrote my code before I found this
paper.)

  * http://www.cis.upenn.edu/~bcpierce/papers/diff3-short.pdf (paper)

## Improved merge algorithms for diff3

The merge logic of `imediff` works on both line and character in 2-stage
action.  I think this is one most important improvement of `imediff`.

The merge logic working only on character can merge non-overlapping change on
the same line cleanly.  But it wastes CPU resource and may pick up accidental
match in totally wrong position of code.

This 2-stage merge action provides a practical improvement of clean merge for
non-overlapping change on the same line without regression over the traditional
merge logic which works only on line as seen in `diff3 -m` and `git`'s internal
merge.

When implementing this 2-stage merge action, `imediff` uses the same code twice
by taking advantage of the python *iterable* concept.

## Problem of GNU diff3

MIZUTANI Tociyuki <tociyuki@gmail.com> published a blog for his diff3 perl
code.

  * https://tociyuki.hatenablog.jp/entry/20051019/1129742409 Algorithm::Diff3改めText::Diff3へ

At the bottom, he has a section with its Japanese titled meaning "Funny
behavior of `diff3 -m`" and wonder if this funny behavior is an intestinal
feature or a bug after mentioning "If the 2 lines in the original file are
removed in both party, `diff3 -m` yields merged output like a conflict case."

> ポート元のGNU utilsの挙動で、一つ不思議なものがあります。オリジナルのファイル
> のある連続行を、2つの側で同時に削除するとコンフリクト発生とみなすようです。
> 違いますよね？私のmerge.plでは、コンフリクトではなく双方刷り合わせ上での正常
> 削除とみなしています。当初、これは、diffのアルゴリズムの違いでdiffの出力が
> 違っているのだろうと考えたのですが、途中結果を出力できるようにして、つきあわ
> せてみると一緒。diff3の変更箇所ブロック出力まで一緒なので、この手のパターンを
> コンフリクトとみなしているのは、mergeを出力する部分のようです。なんかC言語の
> ソースを読んでも、例によってなぜそれをコンフリクト扱いにしているか、わからな
> いのです。仕様でそうしているのか、それともバグなのか。

NOTE: I verified that my `diff3lib.py` functions like MIZUTANI Tociyuki's
`merge.pl` to produce a clean merge result.

Osamu / 2019-01-31

<!-- vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 : -->
