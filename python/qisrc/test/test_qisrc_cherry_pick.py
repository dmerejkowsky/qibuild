## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qisrc.test.conftest import TestGit
from qisrc.test.conftest import TestGitWorkTree

def initial_setup(qisrc_action, git_server):
    """ Create a foo.git repo with three branches:
      * master for continuous releases
      * devel for development
      * bugfix for bug fixes

    While on the delev branch, we want to be able to cherry-pick
    all the patches made on the bugfix branch

    """
    git_server.create_repo("foo.git")
    contents = """
// foo.cpp

int main()
{
    std::cout << "hello, world" << std::endl;
    return 0;
}
"""
    git_server.push_file("foo.git", "foo.cpp", contents=contents)
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    contents = """
// foo.cpp

int main()
{
    std::cout << "hello, world" << std::endl;
    std::cout << "Exciting new feature!" << std::endl;
    return 0;
}
"""
    git_server.push_file("foo.git", "foo.cpp", contents, branch="devel",
                         message="Exciting new feature")
    git_server.switch_manifest_branch("bugfix")
    git_server.change_branch("foo.git", "bugfix")
    contents = """
// foo.cpp
#include <iostream>
int main()
{
    std::cout << "hello, world" << std::endl;
    return 0;
}
"""
    git_server.push_file("foo.git", "foo.cpp", contents,
                         branch="bugfix", fast_forward=False,
                         message="Add missing include")


def test_happy(qisrc_action, git_server):
    initial_setup(qisrc_action, git_server)
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    qisrc_action("cherry-pick", "bugfix")
    git_worktree = TestGitWorkTree()
    foo = git_worktree.get_git_project("foo")
    test_git = TestGit(foo.path)
    actual = test_git.read_file("foo.cpp")
    assert actual == """
// foo.cpp
#include <iostream>
int main()
{
    std::cout << "hello, world" << std::endl;
    std::cout << "Exciting new feature!" << std::endl;
    return 0;
}
"""
