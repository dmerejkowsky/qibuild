## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Automatic testing for qibuild.config.QiBuildConfig

"""

import os
import unittest
import tempfile
from StringIO import StringIO

import qibuild


def cfg_from_string(str, user_config=None):
    cfg_loc = StringIO(str)
    qibuild_cfg = qibuild.config.QiBuildConfig(user_config=user_config)
    qibuild_cfg.read(cfg_loc)
    return qibuild_cfg


def cfg_to_string(cfg):
    cfg_loc = StringIO()
    cfg.write(cfg_loc)
    return cfg_loc.getvalue()


def local_cfg_to_string(cfg):
    cfg_loc = StringIO()
    cfg.write_local_config(cfg_loc)
    return cfg_loc.getvalue()

class QiBuildConfig(unittest.TestCase):

    def test_simple(self):
        xml = """
<qibuild version="1">
  <config name="linux32">
    <env path="/path/to/swig" />
  </config>
  <ide name="qtcreator"
      path="/path/to/qtcreator"
  />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertTrue(qibuild_cfg.active_config is None)
        ide = qibuild_cfg.ides["qtcreator"]
        self.assertEquals(ide.name, "qtcreator")
        self.assertEquals(ide.path, "/path/to/qtcreator")

        config = qibuild_cfg.configs["linux32"]
        self.assertEquals(config.name, "linux32")
        env_path = config.env.path
        self.assertEquals(env_path, "/path/to/swig")

    def test_several_configs(self):
        xml = """
<qibuild version="1">
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
  <config name="linux64">
    <env path="/path/to/swig64" />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        configs = qibuild_cfg.configs
        self.assertEquals(len(configs), 2)
        [linux32_cfg, linux64_cfg] = [configs["linux32"], configs["linux64"]]


        self.assertEquals(linux32_cfg.name, "linux32")
        self.assertEquals(linux64_cfg.name, "linux64")

        self.assertEquals(linux32_cfg.env.path, "/path/to/swig32")
        self.assertEquals(linux64_cfg.env.path, "/path/to/swig64")

    def test_default_from_conf(self):
        xml = """
<qibuild version="1">
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
  <config name="linux64">
    <env path="/path/to/swig64" />
  </config>
</qibuild>
"""
        local_xml = """
<qibuild version="1">
  <defaults config="linux32" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        qibuild_cfg.read_local_config(StringIO(local_xml))
        self.assertEquals(qibuild_cfg.local.defaults.config, "linux32")
        self.assertEquals(qibuild_cfg.active_config, "linux32")
        self.assertEquals(qibuild_cfg.env.path, "/path/to/swig32")

    def test_user_active_conf(self):
        xml = """
<qibuild version="1">
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
  <config name="linux64">
    <env path="/path/to/swig64" />
  </config>
</qibuild>
"""
        local_xml = """
<qibuild version="1">
  <defaults config="linux32" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml, user_config="linux64")
        qibuild_cfg.read_local_config(StringIO(local_xml))
        self.assertEquals(qibuild_cfg.local.defaults.config, "linux32")
        self.assertEquals(qibuild_cfg.active_config, "linux64")
        self.assertEquals(qibuild_cfg.env.path, "/path/to/swig64")

    def test_path_merging(self):
        xml = """
<qibuild version="1">
  <defaults>
    <env path="/path/to/foo" />
  </defaults>
  <config name="linux32">
    <env path="/path/to/swig32" />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml, user_config="linux32")
        excpected_path = qibuild.sh.to_native_path("/path/to/swig32")
        excpected_path += os.path.pathsep
        excpected_path += qibuild.sh.to_native_path("/path/to/foo")
        self.assertEquals(qibuild_cfg.env.path, excpected_path)

    def test_ide_selection(self):
        xml = """
<qibuild version="1">
  <defaults ide="qtcreator" />
  <ide name="qtcreator"
    path="/path/to/qtcreator"
  />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.ide.path, "/path/to/qtcreator")

    def test_add_env_config(self):
        xml = """
<qibuild version="1" />
"""
        qibuild_cfg = cfg_from_string(xml)
        config = qibuild.config.Config()
        config.name = "linux32"
        config.env.path = "/path/to/swig32"
        qibuild_cfg.add_config(config)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEquals(len(new_cfg.configs), 1)
        linux32_conf = new_cfg.configs["linux32"]
        self.assertEquals(linux32_conf.env.path, "/path/to/swig32")

    def test_add_cmake_config(self):
        qibuild_cfg = cfg_from_string("<qibuild />")
        config = qibuild.config.Config()
        config.name = "mac64"
        config.cmake.generator = "Xcode"
        qibuild_cfg.add_config(config)
        qibuild_cfg.set_default_config("mac64")
        local_xml = local_cfg_to_string(qibuild_cfg)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        new_cfg.read_local_config(StringIO(local_xml))
        self.assertEquals(new_cfg.cmake.generator, "Xcode")

    def test_default_cmake_generator(self):
        xml = """
<qibuild version="1">
  <defaults>
    <cmake generator="Visual Studio 10" />
  </defaults>
  <config name="win32-mingw">
    <cmake generator="NMake Makefiles" />
  </config>
</qibuild>
"""
        default_cfg = cfg_from_string(xml)
        self.assertEquals(default_cfg.cmake.generator, "Visual Studio 10")
        mingw_cfg  = cfg_from_string(xml, user_config="win32-mingw")
        self.assertEquals(mingw_cfg.cmake.generator, "NMake Makefiles")


    def test_set_default_config(self):
        xml = """
<qibuild version="1">
  <config name="linux32">
    <cmake
        generator="Unix Makefiles"
    />
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.cmake.generator, None)
        qibuild_cfg.set_default_config("linux32")
        local_xml = local_cfg_to_string(qibuild_cfg)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        new_cfg.read_local_config(StringIO(local_xml))
        self.assertEquals(new_cfg.cmake.generator, "Unix Makefiles")

    def test_change_default_config(self):
        xml = """
<qibuild version="1">
  <config name="linux32">
    <cmake
        generator="Unix Makefiles"
    />
  </config>
  <config name="win32-vs2010">
    <cmake
        generator="Visual Studio 10"
    />
  </config>
</qibuild>
"""
        local_xml = """
<qibuild version="1">
  <defaults config="linux32" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        qibuild_cfg.read_local_config(StringIO(local_xml))
        self.assertEquals(qibuild_cfg.cmake.generator, "Unix Makefiles")
        qibuild_cfg.set_default_config("win32-vs2010")
        local_xml = local_cfg_to_string(qibuild_cfg)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        new_cfg.read_local_config(StringIO(local_xml))
        self.assertEquals(new_cfg.cmake.generator, "Visual Studio 10")

    def test_add_ide(self):
        xml = """
<qibuild version="1">
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertEquals(qibuild_cfg.ide, None)
        ide = qibuild.config.IDE()
        ide.name = "qtcreator"
        qibuild_cfg.add_ide(ide)
        qibuild_cfg.set_default_ide("qtcreator")
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEquals(new_cfg.ide.name, "qtcreator")

    def test_adding_conf_twice(self):
        xml = """
<qibuild version="1">
  <config name="linux32" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        config = qibuild.config.Config()
        config.name = "linux32"
        config.cmake.generator = "Code::Blocks"
        qibuild_cfg.add_config(config)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEqual(new_cfg.configs["linux32"].cmake.generator,
            "Code::Blocks")


    def test_ide_from_config(self):
        xml = """
<qibuild version="1">
  <ide
    name = "Visual Studio"
  />
  <ide
    name = "QtCreator"
    path  = "/path/to/qtsdk/qtcreator"
  />
  <config
    name = "win32-vs2010"
    ide  = "Visual Studio"
  />
  <config
    name = "win32-mingw"
    ide  = "QtCreator"
  />
</qibuild>
"""
        qt_cfg = cfg_from_string(xml, "win32-vs2010")
        self.assertEqual(qt_cfg.ide.name, "Visual Studio")
        self.assertTrue(qt_cfg.ide.path is None)
        vc_cfg = cfg_from_string(xml, "win32-mingw")
        self.assertEqual(vc_cfg.ide.name, "QtCreator")
        self.assertEqual(vc_cfg.ide.path, "/path/to/qtsdk/qtcreator")


    def test_adding_ide_twice(self):
        xml = """
<qibuild version="1">
  <ide name="qtcreator" />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        ide = qibuild.config.IDE()
        ide.name = "qtcreator"
        ide.path = "/path/to/qtcreator"
        qibuild_cfg.add_ide(ide)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        self.assertEqual(new_cfg.ides["qtcreator"].path,
            "/path/to/qtcreator")


    def test_build_settings(self):
        xml = """
<qibuild version="1">
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertFalse(qibuild_cfg.build.incredibuild)
        self.assertTrue(qibuild_cfg.local.build.sdk_dir   is None)
        self.assertTrue(qibuild_cfg.local.build.build_dir is None)

        xml = """
<qibuild version="1">
    <build
        incredibuild="true"
    />
</qibuild>
"""
        local_xml = """
<qibuild version="1">
  <build
    sdk_dir="/path/to/sdk"
    build_dir="/path/to/build"
  />
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        self.assertTrue(qibuild_cfg.build.incredibuild)
        qibuild_cfg.read_local_config(StringIO(local_xml))
        self.assertEqual(qibuild_cfg.local.build.sdk_dir,
            qibuild.sh.to_native_path("/path/to/sdk"))
        self.assertEqual(qibuild_cfg.local.build.build_dir,
            qibuild.sh.to_native_path("/path/to/build"))

    def test_set_manifest_url(self):
        xml = """
<qibuild version="1">
</qibuild>
"""
        manifest_url = "http://example.com/qi/foo.xml"
        qibuild_cfg = cfg_from_string(xml)
        self.assertTrue(qibuild_cfg.local.manifest is None)
        qibuild_cfg.set_manifest_url(manifest_url)
        local_xml = local_cfg_to_string(qibuild_cfg)
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        new_cfg.read_local_config(StringIO(local_xml))
        self.assertFalse(new_cfg.local.manifest is None)
        self.assertEqual(new_cfg.local.manifest.url, manifest_url)


    def test_get_server_access(self):
        xml = """
<qibuild version="1">
  <server name="example.com">
    <access
      username="john"
      password="p4ssw0rd"
      root="root"
    />
  </server>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml)
        # Just make sure setting is kept:
        new_conf = cfg_to_string(qibuild_cfg)
        new_cfg = cfg_from_string(new_conf)
        server_name = "example.com"
        access = new_cfg.get_server_access(server_name)
        self.assertEqual(access.username, "john")
        self.assertEqual(access.password, "p4ssw0rd")
        self.assertEqual(access.root, "root")

        access = new_cfg.get_server_access("doesnotexists")
        self.assertTrue(access is None)

    def test_merge_settings_with_empty_active(self):
        qibuild_cfg = qibuild.config.QiBuildConfig(user_config="win32-vs2010")
        qibuild_cfg.defaults.cmake.generator = "NMake Makefiles"
        qibuild_cfg.configs['win32-vs2010'] = qibuild.config.Config()
        qibuild_cfg.merge_configs()
        self.assertEquals(qibuild_cfg.cmake.generator, "NMake Makefiles")

    def test_build_farm_config(self):
        xml = r"""
<qibuild version="1">
  <build/>
  <defaults>
    <env path="C:\Program Files\swigwin-2.0.1;C:\Program Files (x86)\dotNetInstaller\bin;C:\Program Files (x86)\Windows Installer XML v3.5\bin" bat_file="C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat"/>
    <cmake generator="NMake Makefiles"/>
  </defaults>
  <config name="win32-vs2010">
    <env/>
    <cmake/>
  </config>
</qibuild>
"""
        qibuild_cfg = cfg_from_string(xml,  user_config='win32-vs2010')
        self.assertEquals(qibuild_cfg.cmake.generator, "NMake Makefiles")


class ConvertTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tmp-configstore-test")
        self.cfg_path = os.path.join(self.tmp, "conf.cfg")

    def test_qibuild_cfg(self):
        qibuild_cfg = r"""[general]
config = vs2010
cmake.generator = Unix Makefiles
env.editor = vim
env.ide = QtCreator
env.path = c:\MinGW\bin;c:\Program Files\swig;
env.bat_file = c:\path\to\vsvarsall.bat
build.directory = "/path/to/build"
build.sdk_dir   = "/path/to/sdk"
build.incredibuild = yes
env.qtcreator.path = "/path/to/qtcreator"

[manifest]
url = "http://example.com/foo.manifest"

[config vs2010]
cmake.generator = "Visual Studio 10"
"""
        with open(self.cfg_path, "w") as fp:
            fp.write(qibuild_cfg)
        (qibuild_xml, local_xml) = qibuild.config.convert_qibuild_cfg(self.cfg_path)
        qibuild_cfg = cfg_from_string(qibuild_xml)
        qibuild_cfg.read_local_config(StringIO(local_xml))
        self.assertEqual(qibuild_cfg.defaults.cmake.generator, "Unix Makefiles")
        self.assertEqual(qibuild_cfg.env.editor, "vim")
        self.assertEqual(qibuild_cfg.ides["QtCreator"].path,
            "/path/to/qtcreator")
        self.assertEqual(qibuild_cfg.defaults.env.path,
            r"c:\MinGW\bin;c:\Program Files\swig;")
        self.assertEqual(qibuild_cfg.local.build.build_dir,
            "/path/to/build")
        self.assertEqual(qibuild_cfg.local.build.sdk_dir,
            "/path/to/sdk")
        self.assertEqual(qibuild_cfg.local.manifest.url,
             "http://example.com/foo.manifest")
        self.assertEqual(qibuild_cfg.configs["vs2010"].cmake.generator,
            "Visual Studio 10")
        self.assertEqual(qibuild_cfg.cmake.generator, "Visual Studio 10")

        unix_cfg = cfg_from_string(qibuild_xml, "foo")
        self.assertEqual(unix_cfg.cmake.generator, "Unix Makefiles")


    def test_xml_no_version(self):
        xml = """<qibuild>
  <defaults config="linux32">
    <cmake generator="Unix Makefiles" />
    <env path="/opt/swig/bin" />
  </defaults>
  <config name="linux32">
    <ide name="QtCreator" />
  </config>
  <ide name="QtCreator" path="/qtsdk/bin/qtcreator" />
</qibuild>
"""
        with open(self.cfg_path, "w") as fp:
            fp.write(xml)
        (qibuild_xml, local_xml) = qibuild.config.convert_qibuild_xml(self.cfg_path)
        qibuild_cfg = cfg_from_string(qibuild_xml)
        qibuild_cfg.read_local_config(StringIO(local_xml))
        self.assertEqual(qibuild_cfg.local.defaults.config, "linux32")



    def test_project_manifest(self):
        cfg = """[project foo]
depends = bar baz
rdepends = spam eggs
"""
        with open(self.cfg_path, "w") as fp:
            fp.write(cfg)
        project_xml = qibuild.config.convert_project_manifest(self.cfg_path)
        with open(self.cfg_path, "w") as fp:
            fp.write(project_xml)
        project_cfg = qibuild.config.ProjectConfig()
        project_cfg.read(self.cfg_path)
        self.assertEqual(project_cfg.name, "foo")
        self.assertEqual(project_cfg.depends, set(["bar", "baz"]))
        self.assertEqual(project_cfg.rdepends, set(["spam", "eggs"]))


    def tearDown(self):
        qibuild.sh.rm(self.tmp)


if __name__ == "__main__":
    unittest.main()




