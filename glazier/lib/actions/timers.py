# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Actions to set imaging timers."""

from glazier.lib import constants
from glazier.lib.actions.base import BaseAction
from glazier.lib.actions.registry import RegAdd


class Error(Exception):
  pass


class SetTimer(BaseAction):
  """Create an imaging timer."""

  def Run(self):
    timer = str(self._args[0])

    self._build_info.TimerSet(timer)
    key_name = 'TIMER_' + timer
    key_value = str(self._build_info.TimerGet(timer))
    timer_key = ['HKLM',
                 constants.REG_ROOT,
                 key_name,
                 key_value,
                 'REG_SZ']

    ra = RegAdd(timer_key, self._build_info)
    ra.Run()

  def Validate(self):
    self._ListOfStringsValidator(self._args)
