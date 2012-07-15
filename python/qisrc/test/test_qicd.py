## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qisrc.qicd import find_best_match

class FakeProject:
    def __init__(self, src):
        self.src = src
        self.path = src

class FakeWorktree:
    def __init__(self, *srcs):
        self.projects = list()
        for src in srcs:
            project = FakeProject(src)
            self.projects.append(project)

def test_no_match():
    wortkree = FakeWorktree("foo", "bar")
    assert find_best_match(wortkree, "baz") is None

def test_basename():
    wortkree = FakeWorktree("lib/libfoo",  "lib/libbar")
    assert find_best_match(wortkree, "libf") == "lib/libfoo"

def test_shortest_wins():
    worktree = FakeWorktree("data/foo", "foo")
    assert find_best_match(worktree, "fo") == "foo"
    assert find_best_match(worktree, "data/f") == "data/foo"
