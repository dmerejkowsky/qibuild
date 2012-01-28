## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Initialize a new toc worktree """


# FIXME qibuild --interactive:
#   - Propose a list of configs to choose from, automagically set
#     toolchain name and cmake generator.
#   (preparing the release of qitoolchain/ repo)
#   - Only configure the local file.

import os
import logging

import qibuild

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("--interactive", action="store_true",
        help="start a wizard to help you configuring qibuild")
    parser.add_argument("--force", action="store_true", help="force the init")
    parser.add_argument("--cmake-generator",
        help="Choose a default cmake generator")
    parser.set_defaults(
        cmake_generator="Unix Makefiles")

def do(args):
    """Main entry point"""
    # If user did not specify a worktree, make sure he is not
    # trying to create nested worktrees (there's nothing wrong in
    # having nested worktree, but it may be confusing a little bit)
    if not args.work_tree:
        old_work_tree = qibuild.worktree.guess_work_tree()
        if old_work_tree and os.path.exists(old_work_tree) and not args.force:
            raise Exception("You already have a qi worktree in : %s.\n" % (old_work_tree) +
                        "Use --force if you know what you are doing "
                        "and really want to create a new worktree here.")

    # Use getcwd() if no worktree was given
    work_tree = args.work_tree
    if not work_tree:
        work_tree = os.getcwd()

    # Safe to be called: only creates the .qi/ repertory
    qibuild.toc.create(work_tree)

    # Safe to be called now that we've created it :)
    toc = qibuild.toc.toc_open(work_tree)

    if not args.interactive:
        return

    run_wizard(toc)


def ask_generator():
    """ Ask the user to choose a cmake generator

    """

    cmake = qibuild.command.find_program("cmake")
    if not cmake:
        mess  = "Could not find CMake in your PATH.\n"
        mess  += "Please check your configuration"
        raise Exception(mess)

    cmake_generator = qibuild.interact.ask_choice(qibuild.KNOWN_CMAKE_GENERATORS,
        "Please choose a generator")

    if cmake_generator == 'NMake Makefiles':
        cl = qibuild.command.find_program("cl.exe")
        if not cl:
            mess  = "Could not find cl.exe in your path"
            mess += "Please run from Visual Studio command line prompt"
            raise Exception(mess)

    return cmake_generator

def run_wizard(toc):
    """Write a new configuration if the file passed as
    argument, asking the user a few questions

    """
    cmake_generator = ask_generator()
    toc.config.defaults.cmake.generator = cmake_generator
    toc.save_config()

