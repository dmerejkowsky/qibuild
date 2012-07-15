## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

function qicd {
  PYTHONPATH="@PYTHONPATH@"
  PYTHON="@PYTHON@"
  p=$($PYTHON -c 'import qisrc.qicd; qisrc.qicd.main()' $1)
  if [[ $? -ne 0 ]]; then
    return
  fi
  cd ${p}
}
