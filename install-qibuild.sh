#!/bin/sh
## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
##

# Create a simple launcher for QiBuild scipts.
# They will install in /usr/local/bin, but
# sources will stay where they are.
# Note: on distros where /usr/bin/python is Python 3, you should
# set PYTHON env var to python2

DESTDIR="/usr/local/bin"

get_qibuild_path() {
  if readlink -f . >/dev/null 2>/dev/null ; then
      p=$(dirname "$(readlink -f ${0} 2>/dev/null)")
  else
      p=$(pwd)/$(dirname "${0}")
  fi
  echo $p
}

get_python() {
  for pybin in python python2; do
    ${pybin} --version 2>&1 | grep -q "2\.[6-7]\.*" \
      && echo ${pybin} && break;
    done
}

create_launcher() {
  full_path="$1"
  name="$2"
  shift
  shift
  args="$@"
  PYTHON=$(get_python)
  QIBUILD_PATH=$(get_qibuild_path)


  cat <<EOF >"${DESTDIR}/${name}"
#!/bin/sh

QIBUILD_PATH="${QIBUILD_PATH}"
${PYTHON} "\${QIBUILD_PATH}/${full_path}" ${args} "\$@"
EOF
  chmod 755 "${DESTDIR}/${name}"
  echo "Installed: ${DESTDIR}/${name}"
}


localinst=no
if ! mkdir -p "${DESTDIR}" 2>/dev/null ; then
  localinst=yes
fi

if ! touch "${DESTDIR}"/.tmp_test 2>/dev/null ; then
  localinst=yes
else
  rm -f "${DESTDIR}/.tmp_test"
fi

if [ "$localinst" = "yes" ] ; then
  echo WARNING: ${DESTDIR} is not writable
  echo =====================
  echo installing into ~/.local/bin
  echo You should add ~/.local/bin to your PATH
  echo =====================
  echo
  DESTDIR=~/.local/bin
  mkdir -p "${DESTDIR}"
fi

configure_qicd() {
  qibuild_path=$(get_qibuild_path)
  PYTHONPATH="${QIBUILD_PATH}/python"
  PYTHON=$(get_python)
  qicd_in=${QIBUILD_PATH}/tools/qicd.in.sh
  qicd=${QIBUILD_PATH}/tools/qicd.sh
  sed -e "s,@PYTHON@,${PYTHON}," ${qicd_in} > ${qicd}
  sed -i -e "s,@PYTHONPATH@,${PYTHONPATH}," ${qicd}
  echo Please add something like
  echo
  echo source ${qicd}
  echo
  echo To your ~/.profile to use qicd
}

create_launcher python/bin/qibuild      qibuild
create_launcher python/bin/qitoolchain  qitoolchain
create_launcher python/bin/qisrc        qisrc
create_launcher python/bin/qidoc        qidoc

#aliases
create_launcher python/bin/qibuild      qc           configure
create_launcher python/bin/qibuild      qm           make
create_launcher python/bin/qisrc        qp           pull --rebase
create_launcher python/bin/qibuild      qo           open

#qicd
configure_qicd
echo "Make sure ${DESTDIR} is in your PATH."
