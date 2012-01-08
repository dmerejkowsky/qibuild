#include <qibuild/config.hpp>
#include "src/config_private.hpp"

namespace qibuild {
  namespace config {

QiBuildConfig::QiBuildConfig():
  m_impl(new QiBuildConfigPrivate())
{
}

QiBuildConfig::~QiBuildConfig()
{
  delete m_impl;
}

void QiBuildConfig::read(const QString &cfgPath)
{
  m_impl->read(cfgPath);
}

void QiBuildConfig::save(const QString &cfgPath) const
{
  m_impl->save(cfgPath);
}

void QiBuildConfig::setContent(const QString &content)
{
  m_impl->setContent(content);
}

QString QiBuildConfig::toString() const
{
  return m_impl->toString();
}

void QiBuildConfig::setDefaultsEnvPath(const QString &path)
{
  m_impl->setDefaultsEnvPath(path);
}

QString QiBuildConfig::defaultsEnvPath() const
{
  return m_impl->defaultsEnvPath();
}

void QiBuildConfig::setIncredibuild(bool on)
{
  m_impl->setIncredibuild(on);
}

bool QiBuildConfig::incredibuild() const
{
  return m_impl->incredibuild();
}

void QiBuildConfig::setSdkDir(const QString &path)
{
  m_impl->setSdkDir(path);
}

QString QiBuildConfig::sdkDir() const
{
  return m_impl->sdkDir();
}

void QiBuildConfig::setBuildDir(const QString &path)
{
  m_impl->setBuildDir(path);
}

QString QiBuildConfig::buildDir() const
{
  return m_impl->buildDir();
}

void QiBuildConfig::addIde(const Ide &ide)
{
  m_impl->addIde(ide);
}

QMap<QString, Ide> QiBuildConfig::ides() const
{
  return m_impl->ides();
}

void QiBuildConfig::clearIdes()
{
  m_impl->clearIdes();
}

void QiBuildConfig::addConfig(const Config &config)
{
  m_impl->addConfig(config);
}

QMap<QString, Config> QiBuildConfig::configs() const
{
  return m_impl->configs();
}

  } // namespace config
} // namespace qibuild
