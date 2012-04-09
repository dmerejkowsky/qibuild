## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Synchronize a worktree with a manifest:
update every repository, clone any new repository

"""

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--rebase", action="store_true", dest="rebase",
        help="Use git pull --rebase")
    parser.set_defaults(rebase=False)


def do(args):
    """Main entry point"""
    fail = list()
    worktree = qibuild.open_worktree(args.worktree)

