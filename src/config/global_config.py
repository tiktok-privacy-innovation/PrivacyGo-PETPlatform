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
from typing import Union, Iterable, Dict

from models.global_config import GlobalConfig as GlobalConfigTable


class GlobalConfig:

    def __init__(self, session):
        self.session = session

    def get(self, key: str) -> Union[str, None]:
        record = self.session.query(GlobalConfigTable).filter_by(config_key=key).first()
        return record.config_value if record else None

    def get_all(self, keys: Iterable[str]) -> Dict[str, str]:
        ret = {}
        for key in keys:
            record = self.session.query(GlobalConfigTable).filter_by(config_key=key).first()
            ret[key] = record.config_value if record else None
        return ret
