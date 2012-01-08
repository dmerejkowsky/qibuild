#include <QDebug>
#include <QFileDialog>
#include <config_widget.h>
#include <qibuild/config.hpp>

#include "ides/ides_widget.h"
#include "ides/ide_list_model.h"

#include "ui_config_widget.h"

ConfigWidget::ConfigWidget(QWidget *parent):
  QWidget(parent),
  ui(new Ui::ConfigWidget),
  m_config(new qibuild::config::QiBuildConfig())
{
  ui->setupUi(this);
  m_idesWidget = new IdesWidget(this);
  ui->tabWidget->addTab(m_idesWidget, "Ides Configuration");
}

void ConfigWidget::setCfgPath(const QString &path)
{
  m_cfgPath = path;
  m_config->read(path);
  ui->buildLineEdit->setText(m_config->buildDir());
  ui->sdkLineEdit->setText(m_config->sdkDir());
  ui->incredibuildCheckBox->setChecked(m_config->incredibuild());
  ui->envPathLineEdit->setText(m_config->defaultsEnvPath());
  IdeListModel* ideListModel = new IdeListModel(this);
  ideListModel->readConfig(m_config);
  m_idesWidget->setIdesModel(ideListModel);
}

void ConfigWidget::save()
{
  m_config->setBuildDir(ui->buildLineEdit->text());
  m_config->setSdkDir(ui->sdkLineEdit->text());
  m_config->setIncredibuild(ui->incredibuildCheckBox->checkState());
  m_config->setDefaultsEnvPath(ui->envPathLineEdit->text());

  IdeListModel* ideListModel = m_idesWidget->idesModel();
  if (ideListModel) {
    ideListModel->updateConfig(m_config);
  }
  m_config->save(m_cfgPath);
}

void ConfigWidget::onBrowseBuildDir()
{
  QString buildDir = QFileDialog::getExistingDirectory(this);
  QLineEdit* buildLineEdit = ui->buildLineEdit;
  buildLineEdit->setText(buildDir);
}

void ConfigWidget::onBrowseSdkDir()
{
  QString sdkDir = QFileDialog::getExistingDirectory(this);
  QLineEdit* sdkLineEdit = ui->sdkLineEdit;
  sdkLineEdit->setText(sdkDir);
}

void ConfigWidget::onButtonBoxClicked(QAbstractButton *button)
{
  if (button->text() == "OK") {
    save();
  }
  close();
}

ConfigWidget::~ConfigWidget()
{
  delete ui;
}
