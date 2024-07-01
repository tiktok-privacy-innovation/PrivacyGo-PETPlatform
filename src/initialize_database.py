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
import os
import glob
import json
import platform

import yaml
from sqlalchemy import MetaData

from extensions import get_session_ins
from models.task import Task
from models.job import Job
from models.mission import Mission
from models.global_config import GlobalConfig
from models.mission_context import MissionContext


def initialize_database(url):
    with get_session_ins(url, create_tables=True) as session:
        # initialize GlobalConfig
        party = session.query(GlobalConfig).filter_by(config_key="party").first()
        if party is None:
            session.add(GlobalConfig(config_key="party", config_value="party_a"))
        party_address = session.query(GlobalConfig).filter_by(config_key="party_address").first()
        if party_address is None:
            session.add(
                GlobalConfig(config_key="party_address",
                             config_value=json.dumps({
                                 "party_a": {
                                     "petplatform": {
                                         "url": ""
                                     }
                                 },
                                 "party_b": {
                                     "petplatform": {
                                         "url": ""
                                     }
                                 }
                             })))

        # initialize Mission
        mission_template_dir = "../missions" if platform.system().lower() == "darwin" else "/app/missions"
        for _, filename in enumerate(glob.glob(os.path.join(mission_template_dir, '*.yml'))):
            with open(filename, "r") as rf:
                content = yaml.safe_load(rf.read())
                meta = content.get("meta", {})
                name = meta.get("name", os.path.basename(filename))
                version = meta.get("version", 1)
                mission = session.query(Mission).filter_by(name=name, version=version).first()
                if mission is None:
                    session.add(Mission(name=name, version=version, dag=json.dumps(content)))
        session.commit()


def clear_database(url):
    all_tables = [GlobalConfig, MissionContext, Mission, Job, Task]
    meta = MetaData()
    with get_session_ins(url) as session:
        meta.reflect(bind=session.bind)
        for table in all_tables:
            table_name = table.__tablename__
            if table_name in meta.tables:
                try:
                    session.query(table).delete()
                    session.commit()
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    import settings
    # clear_database(SQLALCHEMY_DATABASE_URI)
    initialize_database(settings.PLATFORM_DB_URI)
