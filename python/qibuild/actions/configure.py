## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Configure a project

"""

import logging
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("cmake arguments")
    group.add_argument("--build-directory", dest="build_directory",
        action="store",
        help="override the default build directory used by cmake")
    group.add_argument("-D", dest="cmake_flags",
        action="append",
        help="additional cmake flags")
    group.add_argument("--no-clean-first", dest="clean_first",
        action="store_false",
        help="do not clean CMake cache")
    group.add_argument("--debug-trycompile", dest="debug_trycompile",
        action="store_true",
        help="pass --debug-trycompile to CMake call")
    parser.set_defaults(clean_first=True)

def do(args):
    """Main entry point"""
    if args.build_directory and not args.single:
        raise Exception("You should use --single when specifying a build directory")

    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc_open(args.work_tree, args)

    (project_names, _, _) = toc.resolve_deps()

    projects = [toc.get_project(name) for name in project_names]
    if args.build_directory:
        projects[0].set_custom_build_directory(args.build_directory)

    if args.debug_trycompile:
        print "--debug-trycompile ON"

    if toc.active_config:
        logger.info("Active configuration: %s", toc.active_config)
    for project in projects:
        logger.info("Configuring %s", project.name)
        toc.configure_project(project,
            clean_first=args.clean_first,
            debug_trycompile=args.debug_trycompile)


