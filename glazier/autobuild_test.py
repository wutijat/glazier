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
"""Unit tests for autobuild."""

from absl.testing import absltest
from pyfakefs import fake_filesystem
from glazier import autobuild
import mock


class LogFatalError(Exception):
  pass


class BuildInfoTest(absltest.TestCase):

  @mock.patch.object(autobuild, 'logs', autospec=True)
  def setUp(self, logs):
    super(BuildInfoTest, self).setUp()
    self.autobuild = autobuild.AutoBuild()
    autobuild.logging = logs.logging
    autobuild.logging.fatal.side_effect = LogFatalError()
    self.filesystem = fake_filesystem.FakeFilesystem()
    autobuild.os = fake_filesystem.FakeOsModule(self.filesystem)

  def testLogFatal(self):
    with self.assertRaises(LogFatalError):
      autobuild._LogFatal('image failed')
    autobuild.logging.fatal.assert_called_with(f'{autobuild._FAILURE_MSG}',
                                               'image failed')

  def testLogFatalCode(self):
    with self.assertRaises(LogFatalError):
      autobuild._LogFatal('image failed', 1234)
    autobuild.logging.fatal.assert_called_with(f'{autobuild._FAILURE_MSG}#1234',
                                               'image failed')

  @mock.patch.object(autobuild.winpe, 'check_winpe', autospec=True)
  def testSetupTaskList(self, wpe):
    # Host
    tasklist = autobuild.constants.SYS_TASK_LIST
    wpe.return_value = False
    self.assertEqual(self.autobuild._SetupTaskList(), tasklist)
    autobuild.FLAGS.preserve_tasks = True
    self.assertEqual(self.autobuild._SetupTaskList(), tasklist)

    # WinPE
    self.filesystem.CreateFile(autobuild.constants.WINPE_TASK_LIST)
    wpe.return_value = True
    tasklist = autobuild.constants.WINPE_TASK_LIST
    self.assertEqual(self.autobuild._SetupTaskList(), tasklist)
    self.assertTrue(autobuild.os.path.exists(tasklist))
    autobuild.FLAGS.preserve_tasks = False
    self.assertEqual(self.autobuild._SetupTaskList(), tasklist)
    self.assertFalse(autobuild.os.path.exists(tasklist))

  @mock.patch.object(autobuild.title, 'set_title', autospec=True)
  @mock.patch.object(autobuild.winpe, 'check_winpe', autospec=True)
  @mock.patch.object(autobuild.runner, 'ConfigRunner', autospec=True)
  @mock.patch.object(autobuild.builder, 'ConfigBuilder', autospec=True)
  @mock.patch.object(autobuild.buildinfo.BuildInfo, 'BeyondCorp', autospec=True)
  def testRunBuild(self, bc, builder, runner, wpe, st):
    bc.return_value = False
    wpe.return_value = False
    self.autobuild.RunBuild()
    self.assertTrue(st.called)

    # ConfigBuilderError
    builder.side_effect = autobuild.builder.ConfigBuilderError
    self.assertRaises(LogFatalError, self.autobuild.RunBuild)
    # ConfigRunnerError
    builder.side_effect = None
    runner.side_effect = autobuild.runner.ConfigRunnerError
    self.assertRaises(LogFatalError, self.autobuild.RunBuild)

  @mock.patch.object(autobuild, 'AutoBuild', autospec=True)
  def testMainError(self, ab):
    ab.return_value.RunBuild.side_effect = KeyboardInterrupt
    self.assertRaises(LogFatalError, autobuild.main, 'something')

  @mock.patch.object(autobuild, 'AutoBuild', autospec=True)
  def testMainException(self, ab):
    ab.return_value.RunBuild.side_effect = Exception
    with self.assertRaises(LogFatalError):
      autobuild.main('something')


if __name__ == '__main__':
  absltest.main()
