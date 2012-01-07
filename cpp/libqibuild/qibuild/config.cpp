#include <qibuild/config.hpp>
#include "src/config_private.hpp"

namespace qibuild {
  namespace config {

Config::Config():
  m_impl(new ConfigPrivate())
{
}

Config::~Config()
{
  delete m_impl;
}

void Config::read(const QString &cfgPath)
{
  m_impl->read(cfgPath);
}

void Config::save(const QString &cfgPath) const
{
  m_impl->save(cfgPath);
}

void Config::setContent(const QString &content)
{
  m_impl->setContent(content);
}

QString Config::toString() const
{
  return m_impl->toString();
}

void Config::setEnvPath(const QString &path)
{
  m_impl->setEnvPath(path);
}

QString Config::envPath() const
{
  return m_impl->envPath();
}

void Config::setIncredibuild(bool on)
{
  m_impl->setIncredibuild(on);
}

bool Config::incredibuild() const
{
  return m_impl->incredibuild();
}

void Config::setSdkDir(const QString &path)
{
  m_impl->setSdkDir(path);
}

QString Config::sdkDir() const
{
  return m_impl->sdkDir();
}

void Config::setBuildDir(const QString &path)
{
  m_impl->setBuildDir(path);
}

QString Config::buildDir() const
{
  return m_impl->buildDir();
}

  } // namespace config
} // namespace qibuild
