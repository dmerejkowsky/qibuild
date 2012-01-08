include(qibuild/modules/qt-tools)
include_directories("." ${CMAKE_CURRENT_BINARY_DIR})

qt4_wrap_cpp(_moc
  ide_list_model.h
  ides_widget.h
)

qt4_wrap_ui(_uic
  ides_widget.ui
)

qi_create_lib(qibuild_ides_view
  ${_moc}
  ${_uic}
  ide_list_model.h
  ide_list_model.cpp
  ides_widget.h
  ides_widget.cpp
)


qi_use_lib(qibuild_ides_view
  qibuild_config
  QT_QTCORE QT_QTGUI)

qi_stage_lib(qibuild_ides_view)

qi_create_bin(test_qibuild_ides_view
  test_qibuild_ides_view.cpp
)

qi_use_lib(test_qibuild_ides_view
  qibuild_ides_view)
