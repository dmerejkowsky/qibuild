#ifndef QIBUILD_CONFIG_WIDGET_H
#define QIBUILD_CONFIG_WIDGET_H

#include <QWidget>
#include <QAbstractButton>

namespace Ui {
  class ConfigWidget;
}

namespace qibuild{
  namespace config {
    class Config;
  }
}

class ConfigWidget : public QWidget
{
  Q_OBJECT

public:
  explicit ConfigWidget(QWidget *parent = 0);
  ~ConfigWidget();
  void setCfgPath(const QString &path);
  void save();

protected slots:
  void onBrowseSdkDir();
  void onBrowseBuildDir();
  void onButtonBoxClicked(QAbstractButton*);

private:
  Ui::ConfigWidget *ui;
  qibuild::config::Config *m_config;
  QString m_cfgPath;

};


#endif // QIBUILD_CONFIG_WIDGET_H
