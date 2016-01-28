## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Check that qibuild help messages do
not contains typos

Note that this also serves as an integrated test for
qisys.main(), and of installing qibuild with pip

"""

from __future__ import print_function

import copy
import os
import subprocess
import virtualenv

import enchant.checker

import qisys.sh
import qipy.venv
from qibuild import QIBUILD_ROOT_DIR

import pytest

# List of words to ignore, case sensitive
# one word per line, rest for comments
IGNORE_LIST = """
CFLAGS
CMAKE
CMake
CONFIG
CPUS
DESTDIR
Goverlap # coming from qibuild depend --help, where we document dot usage
Gsplines # ditto
NUM # NUM_JOBS, NUM_CPUS
QI
QITEST
Rebase
RelWithDebInfo
SRC
TOOLCHAIN
Toolchain
Tpng # ditto qibuild depends
WORKTREE
backtrace
breakpad
buildable
cflags
cmake
config
configs
cov # cov-build, cov-analysis
coverity
deps
dest
destdir
devel
dir
execve
foreach
gcc
gtest
hostname
html
init
intl
json
lf # --lf
libs
linux
mytag
mytarget
ncpu
njobs
os
pdb
perf
perfs
pml
png
qiBuild
qibuild
qidoc
qilinguist
qipkg
qipy
qisrc
qitest
qitoolchain
rebase
rebased
refspec
rsync
runtime
sdk
sourceme
src
svn
timestamps
toolchain
toolchains
tmp
trycompile
untracked
valgrind
virtualenv
werror
workspace
worktree
xml
"""

IGNORE_LIST = IGNORE_LIST.split("\n")
IGNORE_LIST = [x and x.split()[0] for x in IGNORE_LIST]

def test_spellcheck_qibuild_help(tmpdir):
    # First, create a virtualenv an install qibuild on in
    venv = tmpdir.join("venv")
    virtualenv.create_environment(venv.strpath,
                                  site_packages=True) # need pyenchant
    # Then install qibuild:
    pip = qipy.venv.find_script(venv.strpath, "pip")

    top_src_dir = os.path.join(QIBUILD_ROOT_DIR, "..", "..")
    top_src_dir = qisys.sh.to_native_path(top_src_dir)
    cmd = [pip, "install", "--editable", top_src_dir]
    qisys.command.call(cmd)

    # Find all the qi* scripts in the venv:
    bin_path = venv.join("bin")
    qi_scripts = [script for script in bin_path.listdir() \
            if script.basename.startswith("qi")]

    error_lines = list()
    for qi_script in qi_scripts:
        check_script(qi_script, error_lines)

    if error_lines:
        #pylint: disable-msg=E1101
        pytest.fail("\n".join(error_lines))

def check_script(script_path, error_lines=list()):
    """ First run ``<script_path> help`` then
    ``<script_path> <action> --help`` for each action

    Append details of spell check run to the ``error_lines``
    passed as parameter.

    This will allow us to call pytest.fail() exactly once
    no matter how many mistakes there are

    """
    cmd = [script_path.strpath, "help"]
    check_cmdline(cmd, error_lines)
    script_name = script_path.basename
    package_name = "%s.actions" % script_name
    action_modules = qisys.script.action_modules_from_package(package_name)
    for action_module in action_modules:
        action_name = action_module.__name__.split(".")[-1]
        cmd = [script_path.strpath, "help", action_name]
        check_cmdline(cmd, error_lines)

def check_cmdline(cmd, error_lines=list):
    def underline(text):
        return "-" * len(text)

    cmdline = copy.copy(cmd)
    cmdline[0] = os.path.basename(cmd[0])
    print("Checking", *cmdline)
    output = subprocess.check_output(cmd)
    errors = check_for_errors(output, IGNORE_LIST)
    if errors:
        cmd_string = " ".join(cmdline)
        error_lines.append(cmd_string)
        error_lines.append(underline(cmd_string))
        error_lines.extend(sorted(set(errors)))

def check_for_errors(text, ignore_list):
    """ Check the given text for errors.
    :return: the list of all the bad words

    """
    res = list()
    checker = enchant.checker.SpellChecker("en_US")
    checker.set_text(text)
    for error in checker:
        if error.word not in ignore_list:
            res.append(error.word)
    return res
