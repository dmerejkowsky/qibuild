## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for qitoolchain

"""

import os
import tempfile
import unittest
from xml.etree import ElementTree

import qibuild
import qibuild.archive
import qitoolchain

def get_tc_file_contents(tc):
    """ get the contents of the toolchain file of a toolchain

    """
    tc_file_path = tc.toolchain_file
    with open(tc_file_path, "r") as fp:
        contents = fp.read()
    return contents


class QiToolchainTestCase(unittest.TestCase):
    def setUp(self):
        """ Small hack: set qitoolchain.CONFIG_PATH global variable
        for test

        """
        self.tmp = tempfile.mkdtemp(prefix="test-qitoolchain")
        qitoolchain.toolchain.CONFIG_PATH = os.path.join(self.tmp, "config")
        qitoolchain.toolchain.CACHE_PATH  = os.path.join(self.tmp, "cache")
        qitoolchain.toolchain.SHARE_PATH  = os.path.join(self.tmp, "share")


    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def test_setup(self):
        # Check that we are not modifying normal config
        config_path = qitoolchain.get_tc_config_path()
        expected = os.path.join(self.tmp, "config", "toolchains.cfg")
        self.assertEquals(config_path, expected)

        # Check that there are no toolchain yet
        tc_names = qitoolchain.get_tc_names()
        self.assertEquals(tc_names, list())


    def test_create_toolchain(self):
        qitoolchain.create_toolchain("foo")
        self.assertEquals(qitoolchain.get_tc_names(), ["foo"])

    def test_remove_toolchain(self):
        tc = qitoolchain.create_toolchain("foo")
        self.assertEquals(qitoolchain.get_tc_names(), ["foo"])
        tc.remove()
        self.assertEquals(qitoolchain.get_tc_names(), list())

    def test_add_package(self):
        tc = qitoolchain.create_toolchain("test")

        self.assertEquals(tc.packages, list())

        foo_package = qitoolchain.Package("foo", "/path/to/foo")
        tc.add_package(foo_package)
        self.assertEquals(tc.packages, [foo_package])

        # Check that generated toolchain file is correct
        tc_file = get_tc_file_contents(tc)
        self.assertTrue('list(INSERT CMAKE_FIND_ROOT_PATH 0 "%s")' % "/path/to/foo"
            in tc_file, tc_file)

        # Check that adding the package twice does nothing
        tc.add_package(foo_package)
        self.assertEquals(tc.packages, [foo_package])

        # Create a new toolchain object and check that toolchain
        # file contents did not change
        other_tc = qitoolchain.open_toolchain("test")
        other_tc_file = get_tc_file_contents(other_tc)
        self.assertEquals(other_tc_file, tc_file)

    def test_remove_package(self):
        tc = qitoolchain.create_toolchain("test")

        error = None

        try:
            tc.remove_package("foo")
        except Exception, e:
            error = e

        self.assertFalse(error is None)
        self.assertTrue("No such package" in str(error))

        foo_package = qitoolchain.Package("foo", "/path/to/foo")
        tc.add_package(foo_package)

        tc.remove_package("foo")

        tc_file = get_tc_file_contents(tc)

        self.assertFalse("/path/to/foo" in tc_file)

    def test_add_package_with_tc_file(self):
        tc = qitoolchain.create_toolchain("test")
        naoqi_ctc = qitoolchain.Package("naoqi-ctc", "/path/to/ctc", "toolchain-geode.cmake")
        tc.add_package(naoqi_ctc)

        tc_file = get_tc_file_contents(tc)
        self.assertTrue('include("toolchain-geode.cmake")' in tc_file, tc_file)

    def test_remove_package_with_tc_file(self):
        tc = qitoolchain.create_toolchain("test")
        naoqi_ctc = qitoolchain.Package("naoqi-ctc", "/path/to/ctc", "toolchain-geode.cmake")
        tc.add_package(naoqi_ctc)
        tc.remove_package("naoqi-ctc")

        tc_file = get_tc_file_contents(tc)
        self.assertFalse("toolchain-geode.cmake" in tc_file)

    def test_tc_order(self):
        tc = qitoolchain.create_toolchain("test")
        a_path  = "/path/to/a"
        b_path  = "/path/to/b"
        a_cmake = "a-config.cmake"
        b_cmake = "b-config.cmake"

        a_package   = qitoolchain.Package("a", a_path, a_cmake)
        b_package   = qitoolchain.Package("b", b_path, b_cmake)

        tc.add_package(a_package)
        tc.add_package(b_package)

        tc_file = get_tc_file_contents(tc)
        tc_file_lines = tc_file.splitlines()

        a_path_index  = 0
        b_path_index  = 0
        a_cmake_index = 0
        b_cmake_index = 0
        for (i, line) in enumerate(tc_file_lines):
            if a_cmake in line:
                a_cmake_index = i
            if b_cmake in line:
                b_cmake_index = i
            if a_path in line:
                a_path_index = i
            if b_path in line:
                b_path_index = i

        self.assertTrue(a_path_index != 0)
        self.assertTrue(b_path_index != 0)
        self.assertTrue(a_cmake_index != 0)
        self.assertTrue(b_cmake_index != 0)

        # Check that toolchain files are always written before
        # CMAKE_FIND_ROOT_PATH
        self.assertTrue(a_cmake_index < a_path_index)
        self.assertTrue(a_cmake_index < b_path_index)
        self.assertTrue(b_cmake_index < a_path_index)
        self.assertTrue(b_cmake_index < b_path_index)




class FeedTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="test-feed")
        self.srv = os.path.join(self.tmp, "srv")
        qitoolchain.toolchain.CONFIG_PATH = os.path.join(self.tmp, "config")
        qitoolchain.toolchain.CACHE_PATH  = os.path.join(self.tmp, "cache")
        qitoolchain.toolchain.SHARE_PATH  = os.path.join(self.tmp, "share")

    def setup_srv(self):
        this_dir = os.path.dirname(__file__)
        this_dir = qibuild.sh.to_native_path(this_dir)
        feeds_dir = os.path.join(this_dir, "feeds")
        contents = os.listdir(feeds_dir)
        for filename in contents:
            if filename.endswith(".xml"):
                self.configure_xml(filename, self.srv)

        packages_dir = os.path.join(this_dir, "packages")
        contents = os.listdir(packages_dir)
        for filename in contents:
            if filename.endswith(".tar.gz"):
                continue
            if filename.endswith(".zip"):
                continue
            package_dir = os.path.join(packages_dir, filename)
            archive = qibuild.archive.zip(package_dir)
            qibuild.sh.install(archive, self.srv, quiet=True)

    def tearDown(self):
        qibuild.sh.rm(self.tmp)

    def configure_xml(self, name, dest):
        """ Copy a xml file from the test dir to a
        dest in self.tmp

        Returns path to the created file
        Replace @srv_url@ by file://path/to/fest/feeds/ while
        doing so

        """
        this_dir = os.path.dirname(__file__)
        this_dir = qibuild.sh.to_native_path(this_dir)
        src = os.path.join(this_dir, "feeds", name)
        dest = os.path.join(self.tmp, dest)
        qibuild.sh.mkdir(dest, recursive=True)
        dest = os.path.join(dest, name)
        srv_path = qibuild.sh.to_posix_path(self.srv)
        srv_url = "file://" + srv_path
        with open(src, "r") as fp:
            lines = fp.readlines()
        lines = [l.replace("@srv_url@", srv_url) for l in lines]
        with open(dest, "w") as fp:
            fp.writelines(lines)
        return dest

    def test_sdk(self):
        # Generate a fake SDK in self.tmp
        sdk_path = os.path.join(self.tmp, "sdk")
        sdk_xml = self.configure_xml("sdk.xml", sdk_path)

        tc = qitoolchain.create_toolchain("sdk")
        tc.parse_feed(sdk_xml)
        tc_file = get_tc_file_contents(tc)

        package_names = [p.name for p in tc.packages]

        self.assertTrue("naoqi-sdk" in package_names)
        self.assertTrue(qibuild.sh.to_posix_path(sdk_path) in tc_file)

    def test_ctc(self):
        # Generate a fake ctc in self.tmp
        ctc_path = os.path.join(self.tmp, "ctc")
        ctc_xml  = self.configure_xml("ctc.xml", ctc_path)

        tc = qitoolchain.create_toolchain("ctc")
        tc.parse_feed(ctc_xml)
        tc_file = get_tc_file_contents(tc)

        package_names = [p.name for p in tc.packages]

        self.assertTrue("naoqi-geode-ctc" in package_names)
        cross_tc_path = os.path.join(ctc_path, "toolchain-geode.cmake")
        cross_tc_path = qibuild.sh.to_posix_path(cross_tc_path)
        expected  = 'include("%s")' % cross_tc_path

        self.assertTrue(expected in tc_file,
            "Did not find %s\n in\n %s" % (expected, tc_file))

    def test_ctc_nonfree(self):
        self.setup_srv()

        # Generate a fake ctc in self.tmp
        ctc_path = os.path.join(self.tmp, "ctc")
        ctc_xml  = self.configure_xml("ctc-nonfree.xml", ctc_path)

        tc = qitoolchain.create_toolchain("ctc")
        tc.parse_feed(ctc_xml)

        package_names = [p.name for p in tc.packages]

        self.assertTrue("nuance" in package_names)
        self.assertTrue("naoqi-geode-ctc" in package_names)

        nuance_path = tc.get("nuance")
        nuance_geode = os.path.join(nuance_path, "nuance-42-geode")

        self.assertTrue(os.path.exists(nuance_geode))

        ctc_path = tc.get("naoqi-geode-ctc")
        cross_tc_path = os.path.join(ctc_path, "toolchain-geode.cmake")
        cross_tc_path = qibuild.sh.to_posix_path(cross_tc_path)
        self.assertTrue(os.path.exists(cross_tc_path))
        expected  = 'include("%s")' % cross_tc_path

        tc_file = get_tc_file_contents(tc)
        self.assertTrue(expected in tc_file,
            "Did not find %s\n in\n %s" % (expected, tc_file))


    def test_buildfarm(self):
        self.setup_srv()
        buildfarm_xml = os.path.join(self.srv, "buildfarm.xml")

        tc = qitoolchain.create_toolchain("buildfarm")
        tc.parse_feed(buildfarm_xml)

        package_names = [p.name for p in tc.packages]

        self.assertTrue("boost" in package_names)
        self.assertTrue("naoqi" in package_names)

    def test_master_maint(self):
        self.setup_srv()
        master_xml = os.path.join(self.srv, "master.xml")
        maint_xml  = os.path.join(self.srv, "maint.xml")

        tc_master = qitoolchain.create_toolchain("master")
        tc_maint  = qitoolchain.create_toolchain("maint")

        tc_master.parse_feed(master_xml)
        tc_maint.parse_feed(maint_xml)

        boost_master = tc_master.get("boost")
        boost_maint  = tc_maint.get("boost")

        boost_44 = os.path.join(boost_master, "boost-1.44-linux32")
        boost_42 = os.path.join(boost_maint , "boost-1.42-linux32")

        self.assertTrue(os.path.exists(boost_44))
        self.assertTrue(os.path.exists(boost_42))


    def test_feed_is_stored(self):
        self.setup_srv()
        buildfarm_xml = os.path.join(self.srv, "buildfarm.xml")

        tc = qitoolchain.create_toolchain("buildfarm")
        tc.parse_feed(buildfarm_xml)
        self.assertEquals(tc.feed, buildfarm_xml)

        # Re-open the toolchain we created, check that the feed
        # is persistent
        tc2 = qitoolchain.open_toolchain("buildfarm")
        self.assertEquals(tc2.feed, buildfarm_xml)

    def test_parse_feed_twice(self):
        self.setup_srv()
        tc = qitoolchain.create_toolchain("test")
        full = os.path.join(self.srv, "full.xml")
        minimal = os.path.join(self.srv, "minimal.xml")
        tc.parse_feed(full)
        package_names = [p.name for p in tc.packages]
        package_names.sort()
        self.assertEquals(["boost", "python"], package_names)
        self.assertTrue("python" in get_tc_file_contents(tc))

        tc2 = qitoolchain.open_toolchain("test")
        tc2.parse_feed(minimal)
        package_names = [p.name for p in tc2.packages]
        package_names.sort()
        self.assertEquals(["boost"], package_names)
        self.assertFalse("python" in get_tc_file_contents(tc2))

    def test_relative_url(self):
        os.mkdir(self.srv)
        feeds = os.path.join(self.srv, "feeds")
        packages = os.path.join(self.srv, "packages")
        os.mkdir(feeds)
        os.mkdir(packages)

        # Create a fake package
        a_package = os.path.join(packages, "a_package")
        os.mkdir(a_package)
        a_file = os.path.join(a_package, "a_file")
        with open(a_file, "w") as fp:
            fp.write("This file is not empty\n")
        archive = qibuild.archive.zip(a_package)
        package_name = os.path.basename(archive)

        # Create a fake feed:
        a_feed = os.path.join(feeds, "a_feed.xml")
        to_write = """<toolchain>
  <package name="a_package"
           url="{rel_url}"
  />
</toolchain>
"""
        rel_url = "../packages/" + package_name
        to_write = to_write.format(rel_url=rel_url)

        with open(a_feed, "w") as fp:
            fp.write(to_write)

        tc = qitoolchain.create_toolchain("test")
        feed_url = "file://" + qibuild.sh.to_posix_path(a_feed)
        tc.parse_feed(feed_url)

    def test_add_package_to_feed(self):
        self.setup_srv()
        tc = qitoolchain.create_toolchain("test")
        minimal_xml = os.path.join(self.srv, "minimal.xml")
        feed_url = "file://" + qibuild.sh.to_posix_path(minimal_xml)
        tc.parse_feed(feed_url)
        package_names = [p.name for p in tc.packages]
        self.assertEquals(package_names, ["boost"])

        qitoolchain.feed.add_package_to_feed(
            minimal_xml, "nuance", "nuance-42-atom.tar.gz")
        tc.parse_feed(feed_url)
        package_names = [p.name for p in tc.packages]
        self.assertEquals(package_names, ["nuance", "boost"])


    def test_add_package_then_update(self):
        self.setup_srv()
        minimal_xml = os.path.join(self.srv, "minimal.xml")
        feed_url = "file://" + qibuild.sh.to_posix_path(minimal_xml)
        tc = qitoolchain.create_toolchain("test")
        tc.parse_feed(feed_url)
        package_names = [p.name for p in tc.packages]
        self.assertEquals(package_names, ["boost"])

        foo_package = qitoolchain.Package("foo", "/path/to/foo")
        tc.add_package(foo_package)
        package_names = [p.name for p in tc.packages]
        self.assertEquals(package_names, ["foo", "boost"])

        # Make the feed change, re-parse the feed,
        # check that:
        #  - new packages have been added from the feed
        #  - manually added foo package is still here
        qitoolchain.feed.add_package_to_feed(
            minimal_xml, "nuance", "nuance-42-atom.tar.gz")
        tc.parse_feed(feed_url)
        package_names = [p.name for p in tc.packages]
        self.assertEquals(package_names, ["nuance", "boost", "foo"])


if __name__ == "__main__":
    unittest.main()

