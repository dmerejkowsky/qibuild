include(qibuild/modules/qt-tools)
include_directories("." ${CMAKE_CURRENT_BINARY_DIR})

qt4_wrap_ui(_ui
  config_widget.ui
)

qt4_wrap_cpp(_moc
  config_widget.h
)

qi_create_bin(qibuild-config-gui
  ${_ui}
  ${_moc}
  config_widget.h
  config_widget.cpp
  main.cpp
)

qi_use_lib(qibuild-config-gui
  qibuild_config
  QT_QTCORE QT_QTGUI)

