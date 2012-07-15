## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" To be used from ``qicd`` shell function

"""

import sys
import re
import qisrc.worktree

def main():
    """ Main entry point """
    try:
        worktree = qisrc.worktree.open_worktree()
    except Exception:
        sys.stderr.write("Not in a worktree\n")
        sys.exit(2)
    if len(sys.argv) < 2:
        print worktree.root
        sys.exit(0)

    token = sys.argv[1]
    project = find_best_match(worktree, token)
    if project:
        print project.path
        sys.exit(0)
    else:
        sys.stderr.write("no match for %s\n" % token)
        sys.exit(1)


def find_best_match(worktree, token):
    """ Find the best match for a project in a worktree

    """
    for project in worktree.projects:
        match = re.search("^(.*?/)?%s" % token, project.src)
        if match:
            return project
    return None
