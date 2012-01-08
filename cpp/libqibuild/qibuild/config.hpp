#ifndef QIBUILD_CONFIG_HPP
#define QIBUILD_CONFIG_HPP

#include <QMap>
#include <QString>

namespace qibuild {
  namespace config {

class QiBuildConfigPrivate;

struct Ide {
  QString name;
  QString path;
};

struct CMake {
  QString generator;
};

struct Env {
  QString path;
  QString batFile;
};

struct Config {
  QString name;
  CMake cmake;
  Env env;
  QString ide;
};



class QiBuildConfig {
  public:
    QiBuildConfig();
    virtual ~QiBuildConfig();
    // To use with file paths:
    void read(const QString &cfgPath);
    void save(const QString &cfgPath) const;

    // To use with QString:
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
    void addIde(const Ide &ide);
    void clearIdes();
    QMap<QString, Ide> ides() const;
    void addConfig(const Config &config);
    QMap<QString, Config> configs() const;


  private:
    QiBuildConfigPrivate* m_impl;
};


 } // namespace config
} // namespace qibuild

#endif // QIBUILD_CONFIG_HPP
