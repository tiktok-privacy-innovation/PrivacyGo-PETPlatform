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

from sqlalchemy import Column, String, DateTime

from .base import Base, BigIntOrInteger


class Status:
    normal = "Normal"
    revoked = "Revoked"


class Role:
    operator = "Operator"
    node = "Node"
    admin = "Admin"

    _roles = [operator, node, admin]

    @classmethod
    def validate(cls, role: str):
        if role.upper() not in cls._roles:
            raise ValueError(f"invalid user role {role}")
        return role.upper()


class User(Base):
    __tablename__ = "privacy_platform_user"

    id = Column(BigIntOrInteger, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    status = Column(String(80), default=Status.normal, nullable=False)
    role = Column(String(80), nullable=False)

    create_time = Column(DateTime, default=datetime.utcnow)  # create_time field
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"name": self.name, "status": self.status, "role": self.role}

    def validate(self):
        return self.status == Status.normal
