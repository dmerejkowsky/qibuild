#include <qibuild/config.hpp>

#include "config_private.hpp"

#include <QtXml>
#include <QDebug>

namespace qibuild {
  namespace config {


// Set a boolean attribue on the first child
// of the given element, create it if necessary
static void setElemBoolAttr(QDomElement &elem, const QString &name, bool value)
{
  elem.setAttribute(name, value ? "true" : "false");
}

static bool getElemBoolAttr(QDomElement &elem, const QString &name)
{
  QString value = elem.attribute(name, "false");
  if (value == "true" || value == "1") {
    return true;
  }
  return false;
}

QDomElement QiBuildConfigPrivate::findElement(QDomElement &parent, const QString &name) const
{
  QDomElement res;
  res = parent.firstChildElement(name);
  return res;
}

QDomElement QiBuildConfigPrivate::findOrCreate(QDomElement &parent, const QString &name)
{
  QDomElement res;
  res = findElement(parent, name);
  if (res.isNull()) {
     res = m_doc->createElement(name);
     parent.appendChild(res);
  }
  return res;
}


QiBuildConfigPrivate::QiBuildConfigPrivate()
{
  m_doc = new QDomDocument("qibuild");
}

QiBuildConfigPrivate::~QiBuildConfigPrivate()
{
  delete m_doc;
}

void QiBuildConfigPrivate::read(const QString &cfgPath)
{
  QFile cfgFile(cfgPath);
  QString content;
  if (cfgFile.open(QFile::ReadOnly)) {
    content = cfgFile.readAll();
  }
  setContent(content);
}

void QiBuildConfigPrivate::save(const QString &cfgPath) const
{
  QFile cfgFile(cfgPath);
  QString content = this->toString();
  if (cfgFile.open(QFile::WriteOnly)) {
    QTextStream out(&cfgFile);
    out << content;
  }
}

void QiBuildConfigPrivate::setContent(const QString &content)
{
  m_doc->setContent(content);
  parseIdes();
  parseConfigs();
}


QString QiBuildConfigPrivate::toString() const
{
  return m_doc->toString();
}

void QiBuildConfigPrivate::parseIdes() {
  QDomElement docElem = m_doc->documentElement();
  QDomNodeList ideNodes = docElem.elementsByTagName("ide");
  for (unsigned int i = 0; i < ideNodes.length(); i++) {
    QDomElement elem = ideNodes.at(i).toElement();
    Ide ide;
    ide.name = elem.attribute("name", "");
    ide.path = elem.attribute("path", "");
    m_ides.insert(ide.name, ide);
  }
}

void QiBuildConfigPrivate::parseConfigs() {
  QDomElement docElem = m_doc->documentElement();
  QDomNodeList configNodes = docElem.elementsByTagName("config");
  for (unsigned int i = 0; i < configNodes.length(); i++) {
    QDomElement configElem = configNodes.at(i).toElement();
    Config config;
    config.name = configElem.attribute("name", "");
    config.ide = configElem.attribute("ide", "");
    QDomElement cmakeElem = findElement(configElem, "cmake");
    if (! cmakeElem.isNull()) {
      config.cmake.generator = cmakeElem.attribute("generator", "");
    }
    QDomElement envElem = findElement(configElem, "env");
    if (! envElem.isNull()) {
      config.env.path = envElem.attribute("path", "");
      config.env.batFile = envElem.attribute("batFile", "");
    }
    m_configs.insert(config.name, config);
  }
}


void QiBuildConfigPrivate::setDefaultsEnvPath(const QString &path)
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement defaultsElem = findOrCreate(docElem, "defaults");
  QDomElement envElem = findOrCreate(defaultsElem, "env");
  envElem.setAttribute("path", path);
}

QString QiBuildConfigPrivate::defaultsEnvPath() const
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement defaultsElem = findElement(docElem, "defaults");
  if (defaultsElem.isNull())
    return "";
  QDomElement envElem = findElement(defaultsElem, "env");
  if (envElem.isNull())
    return "";
  return envElem.attribute("path", "");
}

void QiBuildConfigPrivate::setIncredibuild(bool on)
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findOrCreate(docElem, "build");
  setElemBoolAttr(buildElem, "incredibuild", on);
}

bool QiBuildConfigPrivate::incredibuild() const
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findElement(docElem, "build");
  if (buildElem.isNull())
    return false;
  return getElemBoolAttr(buildElem, "incredibuild");
}

void QiBuildConfigPrivate::setSdkDir(const QString &path)
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findOrCreate(docElem, "build");
  buildElem.setAttribute("sdk_dir", path);
}

QString QiBuildConfigPrivate::sdkDir() const
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findElement(docElem, "build");
  if (buildElem.isNull())
    return "";
  return buildElem.attribute("sdk_dir", "");
}

void QiBuildConfigPrivate::setBuildDir(const QString &path)
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findOrCreate(docElem, "build");
  buildElem.setAttribute("build_dir", path);
}

QString QiBuildConfigPrivate::buildDir() const
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findElement(docElem, "build");
  if (buildElem.isNull())
    return "";
  return buildElem.attribute("build_dir", "");
}

void QiBuildConfigPrivate::addIde(const Ide &ide)
{
  QDomElement docElem = m_doc->documentElement();
  QDomNodeList ideNodes = docElem.elementsByTagName("ide");
  // Look for mathing Ide in the tree:
  QDomElement ideElem;
  for (unsigned int i = 0; i < ideNodes.length(); i++) {
    QDomElement elem = ideNodes.at(i).toElement();
    if (elem.attribute("name", "") == ide.name) {
      ideElem = elem;
      break;
    }
  }
  if (ideElem.isNull()) {
    ideElem = m_doc->createElement("ide");
    docElem.appendChild(ideElem);
    m_ides.insert(ide.name, ide);
  }

  ideElem.setAttribute("name", ide.name);
  ideElem.setAttribute("path", ide.path);
}

QMap<QString, Ide> QiBuildConfigPrivate::ides() const
{
  return m_ides;
}

void QiBuildConfigPrivate::clearIdes()
{
  QDomElement docElem = m_doc->documentElement();
  QDomNodeList ideNodes = docElem.elementsByTagName("ide");
  for (unsigned int i = 0; i < ideNodes.length(); i++) {
    QDomNode ideNode = ideNodes.at(i);
    docElem.removeChild(ideNode);
  }
  m_ides.clear();
}

void QiBuildConfigPrivate::addConfig(const Config &config)
{
  QDomElement docElem = m_doc->documentElement();
  QDomNodeList configNodes = docElem.elementsByTagName("config");
  // Look for mathing Config in the tree:
  QDomElement configElem;
  for (unsigned int i = 0; i < configNodes.length(); i++) {
    QDomElement elem = configNodes.at(i).toElement();
    if (elem.attribute("name", "") == config.name) {
      configElem = elem;
      break;
    }
  }
  if (configElem.isNull()) {
    configElem = m_doc->createElement("config");
    configElem.setAttribute("name", config.name);
    docElem.appendChild(configElem);
    m_configs.insert(config.name, config);
  }

  configElem.setAttribute("ide", config.ide);

  QDomElement cmakeElem = findOrCreate(configElem, "cmake");
  cmakeElem.setAttribute("generator", config.cmake.generator);

  QDomElement envElem = findOrCreate(configElem, "env");
  envElem.setAttribute("path", config.env.path);
  envElem.setAttribute("bat_file", config.env.batFile);
}

QMap<QString, Config> QiBuildConfigPrivate::configs() const
{
  return m_configs;
}


  } // namespace config
} // namespace qibuild
