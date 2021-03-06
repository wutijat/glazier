# Lint as: python3
# Copyright 2019 Google Inc. All Rights Reserved.
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
"""Tests for glazier.lib.winpe."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import absltest

from glazier.lib import constants
from glazier.lib import identifier

import mock
from pyfakefs import fake_filesystem

TEST_UUID = identifier.uuid.UUID('12345678123456781234567812345678')
TEST_SERIAL = '1A19SEL90000R90DZN7A'
TEST_ID = TEST_SERIAL + '-' + str(TEST_UUID)[:7]


class IdentifierTest(absltest.TestCase):

  def setUp(self):
    super(IdentifierTest, self).setUp()
    mock_wmi = mock.patch.object(
        identifier.hw_info.wmi_query, 'WMIQuery', autospec=True)
    self.addCleanup(mock_wmi.stop)
    mock_wmi.start()
    self.fs = fake_filesystem.FakeFilesystem()
    identifier.open = fake_filesystem.FakeFileOpen(self.fs)
    identifier.os = fake_filesystem.FakeOsModule(self.fs)

  @mock.patch.object(identifier.hw_info.HWInfo, 'BiosSerial', autospec=True)
  @mock.patch.object(identifier.uuid, 'uuid4', autospec=True)
  def test_generate_id(self, mock_uuid, mock_serial):
    mock_uuid.return_value = str(TEST_UUID)[:7]
    mock_serial.return_value = TEST_SERIAL
    self.assertEqual(identifier._generate_id(), TEST_ID)

  @mock.patch.object(identifier.registry, 'set_value', autospec=True)
  @mock.patch.object(identifier, '_generate_id', autospec=True)
  def test_set_id(self, genid, sv):
    genid.return_value = TEST_ID
    identifier._set_id()
    sv.assert_called_with('image_id', TEST_ID, path=constants.REG_ROOT)
    self.assertEqual(identifier._set_id(), TEST_ID)

  @mock.patch.object(identifier.registry, 'set_value', autospec=True)
  def test_set_reg_error(self, sv):
    sv.side_effect = identifier.registry.Error
    self.assertRaises(identifier.Error, identifier._set_id)

  @mock.patch.object(identifier.registry, 'set_value', autospec=True)
  def test_check_file(self, sv):
    self.fs.create_file(
        '/%s/build_info.yaml' % identifier.constants.SYS_CACHE,
        contents='{BUILD: {opt 1: true, TIMER_opt 2: some value, image_id: 12345}}\n'
    )
    identifier._check_file()
    sv.assert_called_with('image_id', 12345, path=constants.REG_ROOT)
    self.assertEqual(identifier._check_file(), 12345)

  def test_check_file_no_id(self):
    self.fs.create_file(
        '/%s/build_info.yaml' % identifier.constants.SYS_CACHE,
        contents='{BUILD: {opt 1: true, TIMER_opt 2: some value, image_num: 12345}}\n'
    )
    self.assertRaises(identifier.Error, identifier._check_file)

  @mock.patch.object(identifier.registry, 'set_value', autospec=True)
  def test_check_file_reg_error(self, sv):
    self.fs.create_file(
        '/%s/build_info.yaml' % identifier.constants.SYS_CACHE,
        contents='{BUILD: {opt 1: true, TIMER_opt 2: some value, image_id: 12345}}\n'
    )
    sv.side_effect = identifier.registry.Error
    self.assertRaises(identifier.Error, identifier._check_file)

  def test_check_file_no_file(self):
    self.assertRaises(identifier.Error, identifier._check_file)

  @mock.patch.object(identifier.registry, 'get_value', autospec=True)
  def test_check_id_get(self, gv):
    gv.return_value = TEST_ID
    self.assertEqual(identifier.check_id(), TEST_ID)

  @mock.patch.object(identifier.registry, 'get_value', autospec=True)
  @mock.patch.object(identifier.winpe, 'check_winpe', autospec=True)
  def test_check_id_get_error(self, wpe, gv):
    wpe.return_value = False
    gv.side_effect = identifier.registry.Error
    self.assertRaises(identifier.Error, identifier.check_id)

  @mock.patch.object(identifier, '_set_id', autospec=True)
  @mock.patch.object(identifier.registry, 'get_value', autospec=True)
  @mock.patch.object(identifier.winpe, 'check_winpe', autospec=True)
  def test_check_id_set(self, wpe, gv, setid):
    gv.return_value = None
    wpe.return_value = True
    identifier.check_id()
    self.assertTrue(setid.called)

  @mock.patch.object(identifier, '_check_file', autospec=True)
  @mock.patch.object(identifier.registry, 'get_value', autospec=True)
  @mock.patch.object(identifier.winpe, 'check_winpe', autospec=True)
  def test_check_id_file(self, wpe, gv, checkfile):
    gv.return_value = None
    wpe.return_value = False
    checkfile.return_value = TEST_ID
    self.assertEqual(identifier.check_id(), TEST_ID)


if __name__ == '__main__':
  absltest.main()
