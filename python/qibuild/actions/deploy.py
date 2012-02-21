## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Deploy some software to a remote host

Mainly useful for sending cross-compilation
results on a robot:

qibuild deploy project login@url:path

"""
import tempfile

import qibuild

def configure_parser(parser):
    """ Configure parser for this action

    """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("deploy arguments")
    group.add_argument("dest",
        help="A destination to deploy, for instance: "
             "login@url:path")


def do(args):
    """ Main entry point

    """
    toc = qibuild.toc_open(args.work_tree, args)

    (project_names, package_names, _) = toc.resolve_deps()
    dest = args.dest

    tmp = tempfile.mkdtemp()
    qibuild.command.call(["sshfs", dest, tmp])
    # Force qibuild install args:
    args.runtime = True
    args.include_deps = True
    qibuild.run_action("qibuild.actions.install", [tmp],
        forward_args=args)
    qibuild.command.call(["fusermount", "-u", tmp])
    qibuild.sh.rm(tmp)


