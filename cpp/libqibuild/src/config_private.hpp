#ifndef QIBUILD_CONFIG_PRIVATE_HPP
#define QIBUILD_CONFIG_PRIVATE_HPP

#include <QString>
#include <QtXml>

namespace qibuild {
  namespace config {

struct Ide;
struct Config;

class QiBuildConfigPrivate {
  public:
    QiBuildConfigPrivate();
    virtual ~QiBuildConfigPrivate();

    void read(const QString &cfgPath);
    void save(const QString &cfgPath) const;

    void setContent(const QString &content);
    QString toString() const;

    void setDefaultsEnvPath(const QString &path);
    QString defaultsEnvPath() const;
    void setIncredibuild(bool on);
    bool incredibuild() const;
    void setSdkDir(const QString &sdkDir);
    QString sdkDir() const;
    void setBuildDir(const QString &path);
    QString buildDir() const;
    void addIde(const Ide& ide);
    QMap<QString, Ide> ides() const;
    void clearIdes();
    void addConfig(const Config& config);
    QMap<QString, Config> configs() const;

  private:
    void parseIdes();
    void parseConfigs();

    QDomElement findElement(QDomElement &parent, const QString &name) const;
    QDomElement findOrCreate(QDomElement &parent, const QString &name);
    QDomDocument *m_doc;

    QMap<QString, Ide> m_ides;
    QMap<QString, Config> m_configs;
};


 } // namespace config
} // namespace qibuild

#endif // QIBUILD_CONFIG_PRIVATE_HPP
