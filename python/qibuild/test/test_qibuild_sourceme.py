## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import sys
import subprocess

def test_qibuild_sourceme(tmpdir, qibuild_action):
    foo_proj = qibuild_action.create_project("foo")
    if not sys.platform.startswith("linux"):
        return
    print_env = tmpdir.join("print_env.py")
    print_env.write("""\
import os
for line in os.environ["LD_LIBRARY_PATH"].split():
    print(line)
""")
    sourceme = qibuild_action("sourceme")
    process = subprocess.Popen(". %s && python %s" % (sourceme, print_env.strpath),
                               shell=True, stdout=subprocess.PIPE)
    out, err = process.communicate()
    out = out.decode("utf-8")
    assert not err
    lines = out.splitlines()
    assert os.path.join(foo_proj.sdk_directory, "lib") in  lines
