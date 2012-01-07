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

QDomElement ConfigPrivate::findElement(QDomElement &parent, const QString &name) const
{
  QDomElement res;
  res = parent.firstChildElement(name);
  return res;
}

QDomElement ConfigPrivate::findOrCreate(QDomElement &parent, const QString &name)
{
  QDomElement res;
  res = findElement(parent, name);
  if (res.isNull()) {
     res = m_doc->createElement(name);
     parent.appendChild(res);
  }
  return res;
}


ConfigPrivate::ConfigPrivate()
{
  m_doc = new QDomDocument("qibuild");
}

ConfigPrivate::~ConfigPrivate()
{
  delete m_doc;
}

void ConfigPrivate::read(const QString &cfgPath)
{
  QFile cfgFile(cfgPath);
  QString content;
  if (cfgFile.open(QFile::ReadOnly)) {
    content = cfgFile.readAll();
  }
  m_doc->setContent(content);
}

void ConfigPrivate::save(const QString &cfgPath) const
{
  QFile cfgFile(cfgPath);
  QString content = this->toString();
  if (cfgFile.open(QFile::WriteOnly)) {
    QTextStream out(&cfgFile);
    out << content;
  }
}

void ConfigPrivate::setContent(const QString &content)
{
  m_doc->setContent(content);
}


QString ConfigPrivate::toString() const
{
  return m_doc->toString();
}

void ConfigPrivate::setEnvPath(const QString &path)
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement defaultsElem = findOrCreate(docElem, "defaults");
  QDomElement envElem = findOrCreate(defaultsElem, "env");
  envElem.setAttribute("path", path);
}

QString ConfigPrivate::envPath() const
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

void ConfigPrivate::setIncredibuild(bool on)
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findOrCreate(docElem, "build");
  setElemBoolAttr(buildElem, "incredibuild", on);
}

bool ConfigPrivate::incredibuild() const
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findElement(docElem, "build");
  if (buildElem.isNull())
    return false;
  return getElemBoolAttr(buildElem, "incredibuild");
}

void ConfigPrivate::setSdkDir(const QString &path)
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findOrCreate(docElem, "build");
  buildElem.setAttribute("sdk_dir", path);
}

QString ConfigPrivate::sdkDir() const
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findElement(docElem, "build");
  if (buildElem.isNull())
    return "";
  return buildElem.attribute("sdk_dir", "");
}

void ConfigPrivate::setBuildDir(const QString &path)
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findOrCreate(docElem, "build");
  buildElem.setAttribute("build_dir", path);
}

QString ConfigPrivate::buildDir() const
{
  QDomElement docElem = m_doc->documentElement();
  QDomElement buildElem = findElement(docElem, "build");
  if (buildElem.isNull())
    return "";
  return buildElem.attribute("build_dir", "");
}


  } // namespace config
} // namespace qibuild
