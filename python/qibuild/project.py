## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


""" This module contains the Project class, and method to
handle them

A project is simply a directory in a worktree containing a qibuild.manifest
file.

The :py:class:`toc` object is able to:
 * update a project to set cmake flags, build directory and so on
   (see :py:func:`update_project`
 * bootstrap the project to generate the dependencies.cmake used
   by the qibuild CMake framework
   (see :py:func:`bootstrap_project`)


"""

import os
import logging

import qibuild.sh

LOGGER = logging.getLogger("qibuild.toc.project")


class Project:
    """ Store information about a :term:`project`

    """
    def __init__(self, name, directory):
        self.name       = name
        self.directory  = directory
        self.depends    = list()
        self.rdepends   = list()
        self.config     = qibuild.config.ProjectConfig()

        #build related settings
        self.cmake_flags     = list()
        self.build_directory = None
        self.sdk_directory   = None
        self._custom_sdk_dir = False

        self.load_config()

    def get_sdk_dir(self):
        """ Return the SDK dir of the project.
        To use the project build results, from an other project,
        you just have to add this directory to CMAKE_FIND_ROOT_PATH

        """
        return os.path.join(self.build_directory, "sdk")

    def load_config(self):
        """ Update project dependency list """
        handle_old_manifest(self.directory)
        project_xml = os.path.join(self.directory, "qiproject.xml")
        if not os.path.exists(project_xml):
            return
        self.config.read(project_xml)
        self.depends  = self.config.depends
        self.rdepends = self.config.rdepends

    def set_custom_build_directory(self, build_dir):
        """ could be used to override the default build_directory
        """
        self.build_directory = build_dir

        #detect single sdk directory for multiple projects
        if not self._custom_sdk_dir:
            self.sdk_directory = os.path.join(self.build_directory, "sdk")


    def __str__(self):
        res = ""
        res += "Project: %s\n" % (self.name)
        res += "  directory       = %s\n" % self.directory
        res += "  depends         = %s\n" % self.depends
        res += "  rdepends        = %s\n" % self.rdepends
        res += "  build_directory = %s\n" % self.build_directory
        res += "  cmake_flags     = %s"   % ", ".join(self.cmake_flags)
        return res

    def __repr__(self):
        res = "<Project %s in %s>" % (self.name, self.directory)
        return res

def name_from_directory(project_dir):
    """Get the project name from the project directory

    The directory should contain a "qiproject.xml" file,
    looking like

        <project name="...">

        </project>

    If such a section can not be found, simply return
    the base name of the directory
    """
    # FIXME: qiproject.xml is read twice!
    # once for finding project names, and an other time for
    # loading complete configuration (with {r,}depends)
    handle_old_manifest(project_dir)
    xml = os.path.join(project_dir, "qiproject.xml")
    if not os.path.exists(xml):
        return os.path.basename(project_dir)
    p_cfg = qibuild.config.ProjectConfig()
    p_cfg.read(xml)
    return p_cfg.name


def version_from_directory(project_dir):
    """Try to guess version from the sources of the project.

    Return None if not found.
    """
    version_cmake = os.path.join(project_dir, "version.cmake")
    if not os.path.exists(version_cmake):
        return None
    contents = None
    with open(version_cmake, "r") as fp:
        contents = fp.read()
    name = name_from_directory(project_dir)
    import re
    up_name = name.upper()
    match = re.match('^set\(%s_VERSION\s+"?(.*?)"?\s*\)' % up_name,
                     contents)
    if not match:
        LOGGER.warning("Invalid version.cmake. Should have a line looking like\n"
           "set(%s_VERSION <VERSION>)",  up_name)
        return None
    return match.groups()[0]



def update_project(project, toc):
    """ Update a project using a Toc instance:

    This is to be called right after the toc object has
    been created, to be sure that the settings are consistent
    among all the projects.

    """
    # Handle custom global build directory containing all projects
    u_toc_bname = toc.build_folder_name
    b_toc_bname = u_toc_bname.encode("UTF-8")
    u_singlebdir = toc.config.local.build.build_dir
    u_p_name = project.name
    b_p_name = u_p_name.encode("UTF-8")
    if u_singlebdir:
        b_singlebdir = u_singlebdir.encode("UTF-8")
        b_singlebdir = os.path.expanduser(b_singlebdir)
        if not os.path.isabs(b_singlebdir):
            b_singlebdir = os.path.join(toc.work_tree, b_singlebdir)
        bname = os.path.join("build-%s" % b_toc_bname, b_p_name)
        project.build_directory = os.path.normpath(os.path.join(b_singlebdir, bname))
    else:
        bname = "build-%s" % b_toc_bname
        project.build_directory = os.path.join(project.directory, bname)


    # Handle single sdk dir
    u_sdk_dir = toc.config.local.build.sdk_dir
    if u_sdk_dir:
        b_sdk_dir = u_sdk_dir.encode("UTF-8")
        if os.path.isabs(b_sdk_dir):
            project.sdk_directory = b_sdk_dir
        else:
            project.sdk_directory = os.path.join(toc.work_tree, b_sdk_dir)
        u_bname = "sdk-%s" % (toc.build_folder_name)
        b_bname = u_bname.encode("UTF-8")
        project.sdk_directory = os.path.normpath(os.path.join(project.sdk_directory, b_bname))
        project._custom_sdk_dir = True
        b_cmake_sdk_dir = qibuild.sh.to_posix_path(project.sdk_directory)
        u_cmake_sdk_dir = b_cmake_sdk_dir.decode("UTF-8")
        project.cmake_flags.append("QI_SDK_DIR=%s" % (u_cmake_sdk_dir))
    else:
        #normal sdk dir in buildtree
        project.sdk_directory   = os.path.join(project.build_directory, "sdk")


    # add CMAKE_BUILD_TYPE cmake flags
    if toc.build_type:
        project.cmake_flags.append("CMAKE_BUILD_TYPE=%s" % (toc.build_type.upper()))

    # add cmake flags
    if toc.user_cmake_flags:
        project.cmake_flags.extend(toc.user_cmake_flags)

    # add the toolchain file:
    if toc.toolchain is not None:
        tc_file = toc.toolchain.toolchain_file
        toolchain_path = qibuild.sh.to_posix_path(tc_file)
        u_toolchain_path = toolchain_path.decode("UTF-8")
        project.cmake_flags.append('CMAKE_TOOLCHAIN_FILE=%s' % u_toolchain_path)

    # lastly, add a correct -DCMAKE_MODULE_PATH
    cmake_qibuild_dir = qibuild.cmake.get_cmake_qibuild_dir()
    b_qibuild_dir = os.path.join(cmake_qibuild_dir, "qibuild")
    u_qibuild_dir = b_qibuild_dir.decode("UTF-8")
    project.cmake_flags.append("qibuild_DIR=%s" % u_qibuild_dir)



def bootstrap_project(project, toc):
    """ Create the magic build/dependencies.cmake file


    """
    # To be written in dependencies.cmake
    to_write = """
#############################################
#QIBUILD AUTOGENERATED FILE. DO NOT EDIT.
#############################################

# Add path to CMake framework path if necessary:
set(_qibuild_path "{cmake_qibuild_dir}")
list(FIND CMAKE_MODULE_PATH "${{_qibuild_path}}" _found)
if(_found STREQUAL "-1")
  # Prefer cmake files matching  current qibuild installation
  # over cmake files in the cross-toolchain
  list(INSERT CMAKE_MODULE_PATH 0 "${{_qibuild_path}}")


  # Uncomment this if you really need to use qibuild
  # cmake files from the cross-toolchain
  # list(APPEND CMAKE_MODULE_PATH "${{_qibuild_path}}")
endif()

# Dependencies:
{dep_to_add}

# Store CMAKE_MODULE_PATH and CMAKE_FIND_ROOT_PATH in cache:
set(CMAKE_MODULE_PATH ${{CMAKE_MODULE_PATH}} CACHE INTERNAL ""  FORCE)
set(CMAKE_FIND_ROOT_PATH ${{CMAKE_FIND_ROOT_PATH}} CACHE INTERNAL ""  FORCE)

{custom_cmake_code}
"""
    custom_cmake_code = ""
    u_config = toc.active_config
    if u_config:
        b_config = u_config.encode("UTF-8")
        local_dir = os.path.join(toc.work_tree, ".qi")
        local_cmake = os.path.join(local_dir, "%s.cmake" % b_config)
        if os.path.exists(local_cmake):
            custom_cmake_code += 'include("%s")\n' % \
                qibuild.sh.to_posix_path(local_cmake)

    cmake_qibuild_dir = qibuild.cmake.get_cmake_qibuild_dir()
    cmake_qibuild_dir = qibuild.sh.to_posix_path(cmake_qibuild_dir)
    dep_sdk_dirs = toc.get_sdk_dirs(project.name)

    dep_to_add = ""
    for sdk_dir in dep_sdk_dirs:

        dep_to_add += """
list(FIND CMAKE_FIND_ROOT_PATH "{sdk_dir}" _found)
if(_found STREQUAL "-1")
    list(INSERT CMAKE_FIND_ROOT_PATH 0 "{sdk_dir}")
endif()
""".format(sdk_dir=qibuild.sh.to_posix_path(sdk_dir))

    to_write = to_write.format(
        cmake_qibuild_dir  = cmake_qibuild_dir,
        dep_to_add        = dep_to_add,
        custom_cmake_code = custom_cmake_code
    )

    qibuild.sh.mkdir(project.build_directory, recursive=True)

    dep_cmake = os.path.join(project.build_directory, "dependencies.cmake")

    with open(dep_cmake, "w") as fp:
        fp.write(to_write)


def handle_old_manifest(directory):
    """ Handle processing a qibuild.manifest file,
    transforming it to a project.xml file on the fly

    """
    project_xml = os.path.join(directory, "qiproject.xml")
    if not os.path.exists(project_xml):
        qibuild_manifest = os.path.join(directory, "qibuild.manifest")
        if os.path.exists(qibuild_manifest):
            xml = qibuild.config.convert_project_manifest(qibuild_manifest)
            with open(project_xml, "w") as fp:
                fp.write(xml)
