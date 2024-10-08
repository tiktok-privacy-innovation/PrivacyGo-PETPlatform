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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import settings


def get_engine(db_uri=None, create_tables=False):
    db_uri = db_uri or settings.PLATFORM_DB_URI
    engine = create_engine(db_uri)
    if create_tables:
        from models.base import Base
        from models.global_config import GlobalConfig
        from models.job import Job
        from models.mission import Mission
        from models.mission_context import MissionContext
        from models.task import Task
        from models.user import User
        Base.metadata.create_all(engine)
    return engine


def get_session_maker(db_uri=None, create_tables=False):
    engine = get_engine(db_uri, create_tables)
    return sessionmaker(bind=engine)
