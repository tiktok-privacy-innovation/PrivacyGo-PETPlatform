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
from constants import Status


class Task(Base):
    __tablename__ = "privacy_platform_task"

    id = Column(BigIntOrInteger, primary_key=True)
    name = Column(String(80), nullable=False)
    job_id = Column(String(80), nullable=False)
    party = Column(String(80), nullable=False)
    args = Column(Text, nullable=True)
    status = Column(String(80), nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    errors = Column(Text, nullable=True)

    create_time = Column(DateTime, default=datetime.utcnow)  # create_time field
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    version_id = Column(Integer, nullable=False, default=0)
    __mapper_args__ = {'version_id_col': version_id}
    __table_args__ = (UniqueConstraint('name', 'job_id', name='uix_1'),)

    def details(self):
        details = {
            "name": self.name,
            "status": self.status,
            "start_time": self.start_time or "NA",
            "end_time": self.end_time or "NA"
        }
        if self.status == Status.FAIL and self.errors:
            details["errors"] = self.errors
        return details

    def reset(self):
        self.status = Status.INIT
        self.start_time = self.end_time = self.errors = None

    def run(self):
        self.status = Status.RUNN
        self.start_time = datetime.utcnow()

    def cancel(self):
        self.status = Status.CANC
        self.end_time = datetime.utcnow()

    def success(self):
        self.status = Status.SUCC
        self.end_time = datetime.utcnow()

    def fail(self, errors: str = None):
        self.status = Status.FAIL
        self.end_time = datetime.utcnow()
        self.errors = errors or ""
