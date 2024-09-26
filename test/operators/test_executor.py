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
import unittest

from job_manager.dag import LogicTask
from job_manager.task import TaskExecutor
from constants import Status


class TestTaskExecutor(unittest.TestCase):

    def setUp(self) -> None:
        task = LogicTask(name="test_operator",
                         party="party_a",
                         args={},
                         status=Status.INIT,
                         depends=[],
                         class_name="TestOperator",
                         class_path="test.operators.test_operator")
        self.task_executor = TaskExecutor(mission_name="test_mission", job_id="j_test", task=task)

    def test_operator(self):
        # todo
        pass
