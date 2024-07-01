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
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from .base import Base, BigIntOrInteger


class MissionContext(Base):
    __tablename__ = "privacy_platform_mission_context"

    id = Column(BigIntOrInteger, primary_key=True)
    config_key = Column(String(80), nullable=False)
    mission_name = Column(String(80), nullable=False)
    config_value = Column(Text, nullable=False)
    expire_time = Column(DateTime, nullable=False)

    create_time = Column(DateTime, default=datetime.utcnow)  # create_time field
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    version_id = Column(Integer, nullable=False, default=0)
    __mapper_args__ = {'version_id_col': version_id}
    __table_args__ = (UniqueConstraint('config_key', 'mission_name', name='uix_1'),)
