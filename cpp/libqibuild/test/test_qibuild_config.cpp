#include <gtest/gtest.h>
#include <qibuild/config.hpp>

#include <QDebug>

using namespace qibuild::config;

TEST(qibuild_config, incredibuildSetting)
{
  // false by default
  const QString input = "<qibuild />";
  Config config;
  config.setContent(input);
  ASSERT_EQ(false, config.incredibuild());

  // now should be set to true
  config.setIncredibuild(true);
  const QString input2 = config.toString();
  Config config2;
  config2.setContent(input2);
  ASSERT_EQ(true, config2.incredibuild()) << config2.toString().toStdString();

  // now should be explicitely set to false
  config2.setIncredibuild(false);
  const QString input3 = config2.toString();
  Config config3;
  config3.setContent(input3);
  ASSERT_EQ(false, config3.incredibuild());
}

TEST(qibuild_config, envPathSetting)
{
  // empty by default
  const QString input = "<qibuild />";
  Config config;
  config.setContent(input);
  ASSERT_EQ("", config.envPath());

  // set it:
  config.setEnvPath("/usr/local/bin");
  const QString input2 = config.toString();
  Config config2;
  config2.setContent(input2);
  ASSERT_EQ("/usr/local/bin", config2.envPath().toStdString());
}

TEST(qibuild_config, changeBuildDir)
{
  // Read build dir from conf:
  const QString input =
      "<qibuild>"
      " <build build_dir=\"/path/to/build\" /> "
      "</qibuild>" ;
  Config config;
  config.setContent(input);
  ASSERT_EQ("/path/to/build", config.buildDir().toStdString());

  // Change it
  config.setBuildDir("/path/to/build2");
  const QString input2 = config.toString();
  Config config2;
  config2.setContent(input2);
  ASSERT_EQ("/path/to/build2", config.buildDir().toStdString()) << input2.toStdString();
}

TEST(qibuild_config, sdkDirSetting)
{
  // empty by default
  const QString input = "<qibuild />";
  Config config;
  config.setContent(input);
  ASSERT_EQ("", config.sdkDir());

  // set it:
  config.setSdkDir("/path/to/sdk");
  const QString input2 = config.toString();
  Config config2;
  config2.setContent(input2);
  ASSERT_EQ("/path/to/sdk", config2.sdkDir().toStdString());

  // change it:
  config2.setSdkDir("/path/to/sdk2");
  const QString input3 = config2.toString();
  Config config3;
  config3.setContent(input3);
  ASSERT_EQ("/path/to/sdk2", config3.sdkDir().toStdString());
}

