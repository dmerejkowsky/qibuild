#ifndef QIBUILD_CONFIG_PRIVATE_HPP
#define QIBUILD_CONFIG_PRIVATE_HPP

#include <QString>
#include <QtXml>

namespace qibuild {
  namespace config {

class ConfigPrivate {
  public:
    ConfigPrivate();
    virtual ~ConfigPrivate();

    void read(const QString &cfgPath);
    void save(const QString &cfgPath) const;

    void setContent(const QString &content);
    QString toString() const;

    void setEnvPath(const QString &path);
    QString envPath() const;
    void setIncredibuild(bool on);
    bool incredibuild() const;
    void setSdkDir(const QString &sdkDir);
    QString sdkDir() const;
    void setBuildDir(const QString &path);
    QString buildDir() const;

  private:
    QDomElement findElement(QDomElement &parent, const QString &name) const;
    QDomElement findElement(const QString &name) const;
    QDomElement findOrCreate(QDomElement &parent, const QString &name);
    QDomElement findOrCreate(const QString &name);
    QDomDocument *m_doc;
};


 } // namespace config
} // namespace qibuild

#endif // QIBUILD_CONFIG_PRIVATE_HPP
