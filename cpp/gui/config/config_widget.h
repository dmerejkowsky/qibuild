#ifndef QIBUILD_CONFIG_WIDGET_H
#define QIBUILD_CONFIG_WIDGET_H

#include <QWidget>
#include <QAbstractButton>

class IdesWidget;

namespace Ui {
  class ConfigWidget;
}

namespace qibuild{
  namespace config {
    class QiBuildConfig;
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
  qibuild::config::QiBuildConfig *m_config;
  QString m_cfgPath;
  IdesWidget *m_idesWidget;

};


#endif // QIBUILD_CONFIG_WIDGET_H
