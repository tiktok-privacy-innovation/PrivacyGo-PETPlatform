# Copyright 2024 TikTok Pte. Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import time
import unittest

from config.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):

    def setUp(self) -> None:
        self.party = "party_a"
        self.cm = ConfigManager(mission_name="psi", job_id="j_20240423182001_1234")

    def tearDown(self) -> None:
        self.cm.close()

    def test_global_config(self):
        party = self.cm.global_config.get("party")
        self.assertEqual(party, self.party)

    def test_mission_context(self):
        abc = self.cm.mission_context.get("abc")
        self.assertEqual(abc, None)
        self.cm.mission_context.set("abc", '123', expire_time=1)
        abc = self.cm.mission_context.get("abc")
        self.assertEqual(abc, '123')
        time.sleep(1.1)
        abc = self.cm.mission_context.get("abc")
        self.assertEqual(abc, None)

    def test_job_context(self):
        self.cm.job_context.set(key="a.b.c", value={"d": "123"}, party="common")
        abcd = self.cm.job_context.get("a.b.c.d")
        self.assertEqual(abcd, "123")
        abcd = self.cm.job_context.get("a.b.c.d", party=self.party)
        self.assertEqual(abcd, None)


if __name__ == '__main__':
    unittest.main()
