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
from datetime import datetime, timedelta
import os
import glob
import json
import platform

import yaml
from sqlalchemy import MetaData

from extensions import get_session_maker
from models.task import Task
from models.job import Job
from models.mission import Mission
from models.global_config import GlobalConfig
from models.mission_context import MissionContext
from models.user import User, Status


def create_users():
    return [
        User(name="user_0", status=Status.normal, role="OPERATOR"),
        User(name="user_1", status=Status.normal, role="OPERATOR")
    ]


def create_missions():
    missions = []
    mission_template_dir = "./test/missions" if platform.system().lower() == "darwin" else "/app/missions"
    for idx, filename in enumerate(glob.glob(os.path.join(mission_template_dir, '*.yml'))):
        with open(filename, "r") as rf:
            content = yaml.safe_load(rf.read())
            meta = content.get("meta", {})
            name = meta.get("name", os.path.basename(filename))
            version = meta.get("version", 1)
            missions.append(Mission(name=name, version=version, dag=json.dumps(content)))
    return missions


def create_jobs():
    job_context = json.dumps({"party_a": {}, "party_b": {}, "common": {"__user_input": {}, "job_id": "j_1234"}})
    join_parties = json.dumps(["party_a", "party_b"])

    jobs = [
        Job(job_id="j_1234",
            mission_name="psi",
            mission_version=1,
            job_context=job_context,
            main_party="party_a",
            join_parties=join_parties,
            status="RUNNING",
            user_name="user_0"),
        Job(job_id="j_1235",
            mission_name="psi",
            mission_version=1,
            job_context=job_context,
            main_party="party_a",
            join_parties=join_parties,
            status="FAILED",
            user_name="user_0"),
        Job(job_id="j_1236",
            mission_name="psi",
            mission_version=1,
            job_context=job_context,
            main_party="party_a",
            join_parties=join_parties,
            status="SUCCESS",
            user_name="user_0"),
        Job(job_id="j_1237",
            mission_name="psi",
            mission_version=1,
            job_context=job_context,
            main_party="party_a",
            join_parties=join_parties,
            status="SUCCESS",
            user_name="user_1")
    ]

    tasks = [
        Task(name="psi_a", job_id="j_1234", party="party_a", status="RUNNING", start_time=datetime.utcnow()),
        Task(name="psi_b", job_id="j_1234", party="party_b", status="RUNNING", start_time=datetime.utcnow()),
        Task(name="psi_a",
             job_id="j_1235",
             party="party_a",
             status="FAILED",
             start_time=datetime.utcnow(),
             end_time=datetime.utcnow() + timedelta(seconds=5),
             errors="error 0"),
        Task(name="psi_b", job_id="j_1235", party="party_b", status="RUNNING", start_time=datetime.utcnow()),
        Task(
            name="psi_a",
            job_id="j_1236",
            party="party_a",
            status="SUCCESS",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(seconds=5),
        ),
        Task(
            name="psi_b",
            job_id="j_1236",
            party="party_b",
            status="SUCCESS",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(seconds=6),
        ),
        Task(
            name="psi_a",
            job_id="j_1237",
            party="party_a",
            status="SUCCESS",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(seconds=5),
        ),
        Task(
            name="psi_b",
            job_id="j_1237",
            party="party_b",
            status="SUCCESS",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(seconds=6),
        ),
    ]
    return jobs, tasks


def initialize_database(url):
    with get_session_maker(url, create_tables=True)() as session:
        users = create_users()
        missions = create_missions()
        jobs, tasks = create_jobs()
        session.add_all(users)
        session.add_all(missions)
        session.add_all(jobs)
        session.add_all(tasks)
        session.commit()


def clear_database(url):
    all_tables = [GlobalConfig, MissionContext, Mission, Job, Task, User]
    meta = MetaData()
    with get_session_maker(url)() as session:
        meta.reflect(bind=session.bind)
        for table in all_tables:
            table_name = table.__tablename__
            if table_name in meta.tables:
                session.query(table).delete()
                session.commit()


if __name__ == '__main__':
    import settings
    clear_database(settings.PLATFORM_DB_URI)
    initialize_database(settings.PLATFORM_DB_URI)
