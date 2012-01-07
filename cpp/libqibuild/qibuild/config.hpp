#ifndef QIBUILD_CONFIG_HPP
#define QIBUILD_CONFIG_HPP

#include <QString>

namespace qibuild {
  namespace config {

class ConfigPrivate;

class Config {
  public:
    Config();
    virtual ~Config();
    // To use with file paths:
    void read(const QString &cfgPath);
    void save(const QString &cfgPath) const;

    // To use with QString:
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
    ConfigPrivate* m_impl;
};


 } // namespace config
} // namespace qibuild

#endif // QIBUILD_CONFIG_HPP
