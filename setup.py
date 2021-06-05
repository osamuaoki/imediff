#!/usr/bin/python3
# vi:se ts=4 sts=4 et ai:
"""
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
import setuptools
from DistUtilsExtra.command import *
from imediff import VERSION, PACKAGE

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=PACKAGE,
    version=VERSION,
    author="Jarno Elonen, Osamu Aoki",
    author_email="elonen@iki.fi, osamu@debian.org",
    description="Interactive Merge Editor for DIFF2/3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/osamuaoki/imediff",
    packages=setuptools.find_packages(),
    scripts=["bin/git-ime"],
    entry_points={"console_scripts": ["imediff=imediff:main"]},
    data_files=[
        ("share/man/man1", ["doc/imediff.1", "doc/git-ime.1"]),
        ("lib/git-core/mergetools", ["mergetools/imediff"]),
    ],
    test_suite="test.test_diff23lib",
    license="GPLv2+",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Environment :: Console :: Curses",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Text Processing :: General",
    ],
    cmdclass={"build": build_extra.build_extra, "build_i18n": build_i18n.build_i18n},
)
