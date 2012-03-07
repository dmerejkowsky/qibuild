## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Toolchain

A set of packages and a toolchain file
"""

import os
import ConfigParser
# FIXME: should we use XML for persistence of Toolchain objects?
import pickle

import qibuild
import qibuild.configstore
import qitoolchain

CONFIG_PATH = "~/.config/qi/"
CACHE_PATH  = "~/.cache/qi"
SHARE_PATH  = "~/.local/share/qi/"


def get_default_packages_path(tc_name):
    """ Get a default path to store extracted packages

    """
    default_root = qibuild.sh.to_native_path(SHARE_PATH)
    default_root = os.path.join(default_root, "toolchains")
    config = ConfigParser.ConfigParser()
    cfg_path = get_tc_config_path()
    config.read(cfg_path)
    root = default_root
    if config.has_section("default"):
        try:
            root = config.get("default", "root")
        except ConfigParser.NoOptionError:
            pass
    res = os.path.join(root, tc_name)
    qibuild.sh.mkdir(res, recursive=True)
    return res

def get_tc_names():
    """ Return the list of all known toolchains, simply by
    parsing the file names in the cache

    """
    cache_path = qibuild.sh.to_native_path(CACHE_PATH)
    cache_path = os.path.join(cache_path, "toolchains")
    if not os.path.exists(cache_path):
        return list()
    filenames = os.listdir(cache_path)
    tc_names = [x for x in filenames if x.endswith(".pickle")]
    tc_names = [x[:-7] for x in tc_names]
    return tc_names


def get_tc_feed(tc_name):
    """ Get the feed associated to a toolchain

    """
    tc = open_toolchain(tc_name)
    return tc.feed


def get_tc_config_path():
    """ Return the general toolchain config file.
    It simply lists all the known toolchains

        [toolchains]
        linux32=
        linux64=
        ...


    """
    config_path = qibuild.sh.to_native_path(CONFIG_PATH)
    qibuild.sh.mkdir(config_path, recursive=True)
    config_path = os.path.join(config_path, "toolchains.cfg")
    return config_path

def get_tc_storage_path(tc_name):
    """ Path to the storage file of the toolchain

    """
    cache_path = qibuild.sh.to_native_path(CACHE_PATH)
    cache_path = os.path.join(cache_path, "toolchains")
    qibuild.sh.mkdir(cache_path, recursive=True)
    return os.path.join(cache_path, "%s.pickle" % tc_name)

class Package():
    """ A package always has a name and a path.

    It may also be associated to a toolchain file, relative to its path
    It may also have a version number, of be coming from a feed

    """
    def __init__(self, name, path, toolchain_file=None):
        self.name = name
        self.path = path
        self.toolchain_file = toolchain_file
        self.version = None
        self.feed = None
        # Quick hack for now
        self.depends = list()

    def __repr__(self):
        res = "<Package %s in %s"  % (self.name, self.path)
        if self.toolchain_file:
            res += " (using toolchain from %s)" % self.toolchain_file
        res += ">"
        return res

    def __str__(self):
        res = self.name
        res += "\n  in %s" % self.path
        if self.toolchain_file:
            res += "\n  using %s toolchain file" % self.toolchain_file
        return res

    def __eq__(self, other):
        if self.name  != other.name:
            return False
        if self.path != other.path:
            return False
        if self.toolchain_file != self.toolchain_file:
            return False
        return True

    def __lt__(self, other):
        return self.name < other.name

def open_toolchain(name):
    """ Open a new toolchain from a name

    :return: a :py:class:`Toolchain` object

    """
    storage_path = get_tc_storage_path(name)
    if not os.path.exists(storage_path):
        raise Exception("No such toolchain: %s" % name)
    with open(storage_path, "r") as fp:
        return pickle.load(fp)


def create_toolchain(name):
    """ Create a new toolchain
    :return: a :py:class:`Toolchain` object

    """
    tc = Toolchain(name)
    tc.dump()
    return tc


class Toolchain:
    """ A toolchain is a set of packages

    If has a name that will later be used as 'build config'
    by the toc object.

    It has a persistent storage, but to benifit from
    it you should not use the constructor but use
    the :py:meth:`create_toolchain` and :py:meth:`open_toolchain`
    methods instead.

    """
    def __init__(self, name):
        self.name = name
        self.packages = list()
        self.cache = self._get_cache_path()
        self.toolchain_file  = os.path.join(self.cache, "toolchain-%s.cmake" % self.name)
        self.feed = None

        # Add self to the list of known toolchains:
        if not self.name in get_tc_names():
            config = ConfigParser.ConfigParser()
            config_path = get_tc_config_path()
            config.read(config_path)
            if not config.has_section("toolchains"):
                config.add_section("toolchains")
            config.set("toolchains", self.name, "")
            with open(config_path, "w") as fp:
                config.write(fp)

        self.cmake_flags = list()

    def __str__(self):
        res  = "Toolchain %s\n" % self.name
        if self.feed:
            res += "Using feed from %s\n" % self.feed
        else:
            res += "No feed\n"
        if self.packages:
            res += "  Packages:\n"
        else:
            res += "No packages\n"
        for package in self.packages:
            res += " " * 4 + str(package).replace("\n", "\n" + " " * 4)
            res += "\n"
        return res

    def remove(self):
        """ Remove a toolchain

        Clean cache, remove all packages
        """
        qibuild.sh.rm(self.cache)
        storage_path = get_tc_storage_path(self.name)
        qibuild.sh.rm(storage_path)

    def _get_cache_path(self):
        """ Returns path to self cache directory

        """
        config_path = get_tc_config_path()
        config = ConfigParser.ConfigParser()
        config.read(config_path)
        cache_path = qibuild.sh.to_native_path(CACHE_PATH)
        cache_path = os.path.join(cache_path, "toolchains")
        if config.has_section("default"):
            try:
                root_cfg = config.get("default", "root")
                cache_path = os.path.join(root_cfg, "cache")
            except ConfigParser.NoOptionError:
                pass
        cache_path = os.path.join(cache_path, self.name)
        qibuild.sh.mkdir(cache_path, recursive=True)
        return cache_path

    def dump(self):
        """ Dump self to the storage path

        """
        storage_path = get_tc_storage_path(self.name)
        to_create = os.path.dirname(storage_path)
        qibuild.sh.mkdir(to_create, recursive=True)
        with open(storage_path, "w") as fp:
            pickle.dump(self, fp)

    def add_package(self, package):
        """ Add a package to the list
        If a package with the same name already exists,
        it will be replaced

        """
        self.packages = [p for p in self.packages if
                p.name != package.name]
        self.packages.insert(0, package)
        self.update_toolchain_file()
        self.dump()

    def remove_package(self, name):
        """ Remove a package from the list.
        An exception is raised if the package name is not found
        in this toolchain

        """
        if name not in [p.name for p in self.packages]:
            raise Exception("No such package: %s" % name)
        self.packages = [p for p in self.packages if
                p.name != name]
        self.update_toolchain_file()
        self.dump()


    def update_toolchain_file(self):
        """ Generates a toolchain file for use by qibuild

        """
        lines = ["# Autogenerated file. Do not edit\n"]

        for package in self.packages:
            if package.toolchain_file:
                tc_file = qibuild.sh.to_posix_path(package.toolchain_file)
                lines.append('include("%s")\n' % tc_file)
        for package in self.packages:
            package_path = qibuild.sh.to_posix_path(package.path)
            lines.append('list(INSERT CMAKE_FIND_ROOT_PATH 0 "%s")\n' % package_path)
            # For some reason CMAKE_FRAMEWORK_PATH does not follow CMAKE_FIND_ROOT_PATH
            # (well, you seldom use frameworks when cross-compiling ...), so we
            # need to change this variable too
            lines.append('list(INSERT CMAKE_FRAMEWORK_PATH 0 "%s")\n' % package_path)

        oldlines = list()
        if os.path.exists(self.toolchain_file):
            with open(self.toolchain_file, "r") as fp:
                oldlines = fp.readlines()

        # Do not write the file if it's the same
        if lines == oldlines:
            return

        with open(self.toolchain_file, "w") as fp:
            lines = fp.writelines(lines)

    def parse_feed(self, feed, dry_run=False):
        """ Parse an xml feed,
        adding packages to self while doing so

        """
        # Delegate this to qitoolchain.feed module
        qitoolchain.feed.parse_feed(self, feed, dry_run=dry_run)

        self.feed = feed
        self.update_toolchain_file()
        self.dump()

    def get(self, package_name):
        """ Get the path to a package

        """
        package_names = [p.name for p in self.packages]
        if package_name not in package_names:
            mess  = "Could not get %s from toolchain %s\n" % (package_name, self.name)
            mess += "No such package"
            raise Exception(mess)
        package = [p for p in self.packages if p.name == package_name][0]
        package_path = package.path
        return package_path

    def install_package(self, package_name, destdir, runtime=False):
        """ Install a package to a destdir.

        If a runtime is False, only the runtime files
        (dynamic libraries, executables, config files) will be
        installed

        """
        package_path = self.get(package_name)
        if runtime:
            qibuild.sh.install(package_path, destdir,
                filter_fun=qibuild.sh.is_runtime)
        else:
            qibuild.sh.install(package_path, destdir)

