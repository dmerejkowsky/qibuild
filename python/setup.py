## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from distutils.core import setup
import sys
import os

packages = [
    "qibuild",
    "qibuild.external",
    "qisrc",
    "qisrc.actions",
    "qibuild",
    "qibuild.actions",
    "qitoolchain",
    "qitoolchain.actions",
]

scripts = [
    "bin/qisrc",
    "bin/qibuild",
    "bin/qitoolchain",
]

package_data = {
 "qibuild" : ["templates/project/CMakeLists.txt",
              "templates/project/main.cpp",
              "templates/project/test.cpp",
              "templates/project/qibuild.manifest"
              ]
}


setup(name = 'qibuild',
      version = "1.14",
      description = "Compilation of C++ projects made easy!",
      author = "Aldebaran Robotics",
      author_email = "qi-dev@aldebaran-robotics.com",
      packages = packages,
      package_data = package_data,
      license = "BSD",
      scripts = scripts
)
