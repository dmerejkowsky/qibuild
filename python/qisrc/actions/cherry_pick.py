## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Cherry-pick commits from an other branch.

Note: it is assumed that the base branch for all development
branch and bug fixes is called 'master'
"""

import qisys.parsers
import qisrc.parsers

def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("branch")

def do(args):
    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=True,
                                                  use_build_deps=False)
