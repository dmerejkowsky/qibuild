#ifndef IDES_WIDGET_H
#define IDES_WIDGET_H

#include <QWidget>
#include <QAbstractItemModel>

class IdeListModel;

namespace Ui {
  class IdesWidget;
}

class IdesWidget : public QWidget
{
  Q_OBJECT

  public:
    explicit IdesWidget(QWidget *parent=0);
    virtual ~IdesWidget();

    // Just shortcuts to get access to the model
    // from ui's IdesView
    void setIdesModel(QAbstractItemModel *model);
    IdeListModel* idesModel();


  protected slots:
    void onAdd();
    void onRemove();

  private:
    Ui::IdesWidget *ui;

};

#endif // IDES_WIDGET_H
