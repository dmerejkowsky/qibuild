#include <QApplication>
#include <QMainWindow>
#include "ides/ides_widget.h"
#include "ides/ide_list_model.h"

#include <qibuild/config.hpp>
using namespace qibuild::config;

int main(int argc, char* argv[])
{
  QApplication app(argc, argv);
  QMainWindow mainWindow;
  IdesWidget* idesWidget = new IdesWidget();
  IdeListModel* idesListModel = new IdeListModel(&mainWindow);
  Ide qtcreator;
  qtcreator.name = "QtCreator";
  qtcreator.path = "/usr/bin/qtcreator";
  idesListModel->addIde(qtcreator);
  idesWidget->setIdesModel(idesListModel);
  mainWindow.setCentralWidget(idesWidget);
  mainWindow.show();
  int exit = app.exec();
  delete idesListModel;
  return exit;
}
