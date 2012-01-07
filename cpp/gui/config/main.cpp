#include <QtGui/QApplication>
#include <iostream>
#include "config_widget.h"

int main(int argc, char *argv[])
{
    if(argc < 2) {
      std::cerr << "Usage: qibuild-config-gui XML_CONFIG" << std::endl;
      exit(2);
    }
    QString cfgPath = argv[1];
    QApplication app(argc, argv);
    ConfigWidget configWidget;
    configWidget.setCfgPath(cfgPath);
    configWidget.show();
    return app.exec();
}


