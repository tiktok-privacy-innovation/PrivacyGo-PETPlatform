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
from typing import Union
from datetime import datetime, timedelta

from sqlalchemy.orm.exc import StaleDataError

from constants import TimeDuration
from models.mission_context import MissionContext as MissionContextTable
from utils.db_utils import session_commit_with_retry


class MissionContext:

    def __init__(self, mission_name: str):
        from extensions import get_session_maker
        self.session_maker = get_session_maker()
        self.mission_name = mission_name

    def get(self, key: str) -> Union[str, None]:
        with self.session_maker() as session:
            record = session.query(MissionContextTable).filter_by(config_key=key,
                                                                  mission_name=self.mission_name).first()
            if record is None:
                return None
            if record.expire_time < datetime.utcnow():
                return None
            return record.config_value

    def set(self, key: str, value: str, expire_time=TimeDuration.DAY) -> bool:
        with self.session_maker() as session:
            utcnow = datetime.utcnow()
            new_expire_time = utcnow + timedelta(seconds=expire_time)
            record = session.query(MissionContextTable).filter_by(config_key=key,
                                                                  mission_name=self.mission_name).first()
            if record is None:  # create
                record = MissionContextTable(config_key=key,
                                             mission_name=self.mission_name,
                                             config_value=value,
                                             expire_time=new_expire_time)
                session.add(record)
            else:  # update
                record.config_value = value
                record.expire_time = new_expire_time
            try:
                session_commit_with_retry(session)
                return True
            except StaleDataError:
                # This happens when two jobs try to modify the same record,
                # this modification fails due to the optimistic lock.
                # We leave it the caller to handle, he may try to read it again.
                session.rollback()
                return False
