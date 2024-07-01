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
import logging

from extensions import get_session_ins
from .global_config import GlobalConfig
from .job_context import JobContext
from .mission_context import MissionContext


class ConfigManager:
    """
    A demo code to show how to use ConfigManager for
    class BaseTask:
        def __init__(self, mission_name: str, job_id: str):
            self.config_manager = ConfigManager(mission_name, job_id)

        def handle(self):
            party = self.config_manager.global_config.get('party')
            encrypt_key = self.config_manager.mission_context.get('encrypt_key')
            if encrypt_key is None:
                encrypt_key = 'dsqklvvemiwocsajl='
                self.config_manager.mission_context.set('encrypt_key', encrypt_key, expire_time=3600)
            input_table = self.config_manager.job_context.get('input_table', party=party)
            output_table = 'abc'
            self.config_manager.job_context.set('output_table', output_table, party=party)
    """

    def __init__(self, mission_name: str, job_id: str):
        self.mission_name = mission_name
        self.job_id = job_id

        self._session = None
        self._global_config = None
        self._mission_context = None
        self._job_context = None

    @property
    def session(self):
        if self._session is None:
            self._session = get_session_ins()
        return self._session

    @property
    def global_config(self):
        if self._global_config is None:
            self._global_config = GlobalConfig(self.session)
        return self._global_config

    @property
    def mission_context(self):
        if self._mission_context is None:
            self._mission_context = MissionContext(self.session, self.mission_name)
        return self._mission_context

    @property
    def job_context(self):
        if self._job_context is None:
            self._job_context = JobContext(self.session, self.job_id)
        return self._job_context

    def close(self):
        if self._session:
            self._session.close()
        logging.info("config manager session closed")
