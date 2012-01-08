#include <QDebug>
#include "ides_widget.h"
#include "ide_list_model.h"
#include "ui_ides_widget.h"

IdesWidget::IdesWidget(QWidget *parent):
    QWidget(parent),
    ui(new Ui::IdesWidget)
{
  ui->setupUi(this);
}

void IdesWidget::setIdesModel(QAbstractItemModel *model)
{
  QHeaderView* headerView = ui->idesView->horizontalHeader();
  headerView->setStretchLastSection(true);
  ui->idesView->setModel(model);
}

IdeListModel* IdesWidget::idesModel()
{
  return dynamic_cast<IdeListModel*>(ui->idesView->model());
}

void IdesWidget::onAdd()
{
  IdeListModel* model = idesModel();
  if (!model) {
    return;
  }
  const QModelIndex index = ui->idesView->currentIndex();
  model->insertRow(index.row());
}

void IdesWidget::onRemove()
{
  IdeListModel* model = idesModel();
  if (!model) {
    return;
  }
  const QModelIndex index = ui->idesView->currentIndex();
  model->removeRow(index.row());
}

IdesWidget::~IdesWidget()
{
  delete ui;
}
