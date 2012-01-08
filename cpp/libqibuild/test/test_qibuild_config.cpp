#include <gtest/gtest.h>
#include <qibuild/config.hpp>

#include <QDebug>

using namespace qibuild::config;

TEST(QiBuildConfig, incredibuildSetting)
{
  // false by default
  const QString input = "<qibuild />";
  QiBuildConfig config;
  config.setContent(input);
  ASSERT_EQ(false, config.incredibuild());

  // now should be set to true
  config.setIncredibuild(true);
  const QString input2 = config.toString();
  QiBuildConfig config2;
  config2.setContent(input2);
  ASSERT_EQ(true, config2.incredibuild()) << config2.toString().toStdString();

  // now should be explicitely set to false
  config2.setIncredibuild(false);
  const QString input3 = config2.toString();
  QiBuildConfig config3;
  config3.setContent(input3);
  ASSERT_EQ(false, config3.incredibuild());
}

TEST(QiBuildConfig, defaultsEnvPathSetting)
{
  // empty by default
  const QString input = "<qibuild />";
  QiBuildConfig config;
  config.setContent(input);
  ASSERT_EQ("", config.defaultsEnvPath());

  // set it:
  config.setDefaultsEnvPath("/usr/local/bin");
  const QString input2 = config.toString();
  QiBuildConfig config2;
  config2.setContent(input2);
  ASSERT_EQ("/usr/local/bin", config2.defaultsEnvPath().toStdString());
}

TEST(QiBuildConfig, changeBuildDir)
{
  // Read build dir from conf:
  const QString input =
      "<qibuild>"
      " <build build_dir=\"/path/to/build\" /> "
      "</qibuild>" ;
  QiBuildConfig config;
  config.setContent(input);
  ASSERT_EQ("/path/to/build", config.buildDir().toStdString());

  // Change it
  config.setBuildDir("/path/to/build2");
  const QString input2 = config.toString();
  QiBuildConfig config2;
  config2.setContent(input2);
  ASSERT_EQ("/path/to/build2", config.buildDir().toStdString()) << input2.toStdString();
}

TEST(QiBuildConfig, sdkDirSetting)
{
  // empty by default
  const QString input = "<qibuild />";
  QiBuildConfig config;
  config.setContent(input);
  ASSERT_EQ("", config.sdkDir());

  // set it:
  config.setSdkDir("/path/to/sdk");
  const QString input2 = config.toString();
  QiBuildConfig config2;
  config2.setContent(input2);
  ASSERT_EQ("/path/to/sdk", config2.sdkDir().toStdString());

  // change it:
  config2.setSdkDir("/path/to/sdk2");
  const QString input3 = config2.toString();
  QiBuildConfig config3;
  config3.setContent(input3);
  ASSERT_EQ("/path/to/sdk2", config3.sdkDir().toStdString());
}

TEST(QiBuildConfig, ideSettings)
{
  const QString input = "<qibuild />";
  QiBuildConfig config;
  config.setContent(input);
  QMap<QString, Ide> ides = config.ides();
  ASSERT_TRUE(ides.empty());

  // Add an IDE:
  Ide qtcreator;
  qtcreator.name = "QtCreator";
  qtcreator.path = "/path/to/qtsdk/bin/qtcreator";
  config.addIde(qtcreator);
  const QString input2 = config.toString();
  QiBuildConfig config2;
  config2.setContent(input2);
  ides = config2.ides();
  ASSERT_TRUE(ides.contains("QtCreator")) << input2.toStdString();

  // Clear the list
  config2.clearIdes();
  const QString input3 = config2.toString();
  QiBuildConfig config3;
  config3.setContent(input3);
  ides = config3.ides();
  ASSERT_TRUE(ides.empty());
}

TEST(QiBuildConfig, configSettings)
{
  const QString input = "<qibuild />";
  QiBuildConfig config;
  config.setContent(input);
  QMap<QString, Config> configs = config.configs();
  Config actualConfig;
  ASSERT_TRUE(configs.empty());

  // Add a config:
  Config mingw;
  mingw.cmake.generator = "MinGW Makefiles";
  mingw.name = "mingw32";
  config.addConfig(mingw);
  const QString input2 = config.toString();
  QiBuildConfig config2;
  config2.setContent(input2);
  configs = config2.configs();
  ASSERT_TRUE(configs.contains("mingw32")) << input2.toStdString();
  actualConfig = *(configs.find("mingw32"));
  ASSERT_EQ("mingw32",         actualConfig.name.toStdString());
  ASSERT_EQ("MinGW Makefiles", actualConfig.cmake.generator.toStdString());

  // Add a path to the config
  mingw.env.path = "c:\\MinGW\\bin";
  config2.addConfig(mingw);
  const QString input3 = config2.toString();
  QiBuildConfig config3;
  config3.setContent(input3);
  configs = config3.configs();
  ASSERT_TRUE(configs.contains("mingw32"));
  actualConfig = *(configs.find("mingw32"));
  ASSERT_EQ("mingw32",         actualConfig.name.toStdString());
  ASSERT_EQ("MinGW Makefiles", actualConfig.cmake.generator.toStdString());
  ASSERT_EQ("c:\\MinGW\\bin",  actualConfig.env.path.toStdString());

  // Change the path
  mingw.env.path = "c:\\QtSDK\\mingw\\bin";
  config3.addConfig(mingw);
  const QString input4 = config3.toString();
  QiBuildConfig config4;
  config4.setContent(input4);
  configs = config4.configs();
  ASSERT_TRUE(configs.contains("mingw32"));
  actualConfig = *(configs.find("mingw32"));
  ASSERT_EQ("mingw32",                actualConfig.name.toStdString());
  ASSERT_EQ("MinGW Makefiles",        actualConfig.cmake.generator.toStdString());
  ASSERT_EQ("c:\\QtSDK\\mingw\\bin",  actualConfig.env.path.toStdString());
}

TEST(QiBuildConfig, ideConfigs)
{
  const QString input =
    "<qibuild>"
      "<config name=\"mingw32\" ide=\"Visual Studio 10\" />"
    "</qibuild>";

  QiBuildConfig config;
  config.setContent(input);
  QMap<QString, Config> configs = config.configs();
  ASSERT_TRUE(configs.contains("mingw32"));
  Config actualConfig;
  actualConfig = *(configs.find("mingw32"));
  ASSERT_EQ("Visual Studio 10", actualConfig.ide);

  // Change ide
  Config mingw32;
  mingw32.name = "mingw32";
  mingw32.ide = "QtCreator";
  config.addConfig(mingw32);

  const QString input2 = config.toString();
  QiBuildConfig config2;
  config2.setContent(input2);
  configs = config2.configs();
  ASSERT_TRUE(configs.contains("mingw32"));
  actualConfig = *(configs.find("mingw32"));
  ASSERT_EQ("QtCreator", actualConfig.ide);
}
