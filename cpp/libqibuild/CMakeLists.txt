project(libqibuild)

include_directories(".")
qi_create_lib(qibuild_config
  qibuild/config.cpp
  qibuild/config.hpp
  src/config_private.cpp
  src/config_private.hpp)

qi_use_lib(qibuild_config QT_QTCORE QT_QTXML QT_QTXMLPATTERNS)
qi_stage_lib(qibuild_config
  DEPEND QT_QTCORE)

add_subdirectory(test)
