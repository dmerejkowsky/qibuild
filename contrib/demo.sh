#!/bin/bash

# Run a demo of qiBuild possibilities

MANIFEST_URL="git://sd-20870.dedibox.fr/demo/manifest.git"

step () {
  echo
  echo "running:"
  echo ">" "$@"
  echo -n "> "
  read -r
  "$@"
  if [[ $? -ne 0 ]]; then
    echo "Oups. Something went wrong. Feel free to open a bug report"
    exit 1
  fi
}

main () {

  echo "Welcome to qiBuild demo. When prompted, press enter to continue"
  echo

  echo "Making sure qibuild in installed"

  qibuild --version

  if [[ $? -ne 0 ]] ; then
    echo "Problem while running qibuild. Aborting"
    exit 1
  fi

  echo "Preparing demo directory"

  mkdir demo
  if [[ $? -ne 0 ]] ; then
    echo "Make sure to remove demo/ folder"
    exit 1
  fi

  cd demo || exit 1

  step qisrc init "${MANIFEST_URL}"
  step qibuild configure hello
  step qibuild make hello
  step qipy bootstrap
  cd hello || exti 1
  step qipy run py.test test/test_hello.py

}

main
