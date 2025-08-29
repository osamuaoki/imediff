#!/usr/bin/python3
# vim:se tw=79 sts=4 ts=4 et ai fileencoding=utf-8 :

"""
IMEDIFF - Interactive Merge Editor for DIFF2 and DIFF3
          Curses based single-pane fullscreen interactive tool
          and CLI based non-interactive tool with --macro

Copyright (C) 2003, 2004 Jarno Elonen <elonen@iki.fi>
Copyright (C) 2018--2025 Osamu Aoki <osamu@debian.org>

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
from imediff.config import config_template

import configparser
import os
import sys
import logging

logger = logging.getLogger(__name__)


def initialize_confs(conf):
    """Process configuration file"""
    config_file = os.path.expanduser(conf)
    # Allow inline comment with #
    confs_i = configparser.ConfigParser(inline_comment_prefixes=("#"))
    confs_i.read_string(config_template)
    confs_f = configparser.ConfigParser(inline_comment_prefixes=("#"))
    if config_file == "none":
        confs = confs_i
    elif os.path.exists(config_file):
        confs_f.read(config_file)
        if (
            "version" in confs_f["config"].keys()
            and confs_f["config"]["version"] == confs_i["config"]["version"]
        ):
            confs = confs_f
        else:
            logger.error(
                '''\
Error in {0}: version mismatch
        the current version:  {1}
        the required version: {2}

Rename {0} to {0}.bkup and make the new {0} by
editing the template obtained by "imediff -t"'''.format(
                    conf, confs_f["config"]["version"], confs_i["config"]["version"]
                )
            )
            # enhanced visibility
            print(
                '''\
Error in {0}: version mismatch
        the current version:  {1}
        the required version: {2}

Rename {0} to {0}.bkup and make the new {0} by
editing the template obtained by "imediff -t"'''.format(
                    conf, confs_f["config"]["version"], confs_i["config"]["version"]
                )
            )
            sys.exit(2)
    else:
        confs = confs_i
    logger.debug("confs: end with len(confs)={}".format(len(confs)))
    return confs
