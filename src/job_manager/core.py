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
import json
import logging
from typing import Dict

import multiprocessing as mp
from sqlalchemy.orm.exc import StaleDataError

from constants import Status
from models.job import Job
from models.mission import Mission
from models.task import Task
from network import request_manager
import settings
from utils.db_utils import session_commit_with_retry
from utils.deep_merge import deep_merge
from task_executor.core import TaskExecutor
from .dag import DAG, LogicTask


class JobManager:
    _dag: "DAG" = None

    def __init__(self, job_id: str, session=None):
        if session is None:
            from extensions import get_flask_session
            session = get_flask_session()
        self.session = session
        self.job_id = job_id

    def close(self):
        if self.session:
            self.session.close()
        logging.info("job manager session closed")

    @property
    def dag(self):
        if self._dag is None:
            self._dag = DAG(self.session, self.job_id)
        return self._dag

    def _update_dag(self):
        self._dag = DAG(self.session, self.job_id)

    def _get_mission(self, mission_name, mission_version):
        if mission_version == "latest":
            mission: "Mission" = self.session.query(Mission).filter_by(name=mission_name).order_by(
                Mission.version.desc()).first()
        else:
            mission: "Mission" = self.session.query(Mission).filter_by(name=mission_name,
                                                                       version=int(mission_version)).first()
        assert mission is not None, ValueError(f"mission {mission_name}@v{mission_version} not found")
        return mission

    def submit_job(self, params: Dict):
        # does not allow parallel jobs
        # running_jobs = self.session.query(Job).filter_by(status=Status.RUNN).all()
        # if running_jobs:
        #     raise Exception("parallel jobs not allowed, please wait until the last job finish")

        # decide mission
        mission_name = params.get("mission_name", "ecdh_psi_optimized")
        mission_version = params.get("mission_version", "latest")
        mission = self._get_mission(mission_name, mission_version)

        # get party info
        main_party = params.get("main_party", settings.PARTY)
        mission_dag = json.loads(mission.dag)
        join_parties = list({operator["party"] for operator in mission_dag["operators"]})

        # inform join parties to submit a new job with the same job id, mission name, and version
        if main_party == settings.PARTY:
            # set params
            params["main_party"] = main_party
            params["mission_name"] = mission.name
            params["mission_version"] = str(mission.version)
            params["job_id"] = self.job_id
            for party in join_parties:
                if party == settings.PARTY:
                    continue
                request_manager.submit(party, params)

        # create job
        mission_params = params.get("mission_params", {})
        job_context = {"common": {"__user_input": mission_params, "job_id": self.job_id}}
        for party in join_parties:
            job_context[party] = {}
        job = Job(job_id=self.job_id,
                  mission_name=mission.name,
                  mission_version=mission.version,
                  job_context=json.dumps(job_context),
                  main_party=main_party,
                  join_parties=json.dumps(join_parties),
                  status=Status.RUNN)
        # create tasks
        tasks = [
            Task(name=operator["name"],
                 job_id=self.job_id,
                 party=operator["party"],
                 args=json.dumps(operator.get("args", {})),
                 status=Status.INIT) for operator in mission_dag["operators"]
        ]

        # commit changes to db
        self.session.add(job)
        self.session.add_all(tasks)
        session_commit_with_retry(self.session)
        logging.info(f"created new job {self.job_id}:{mission_dag}@{mission_version}, job_context: {job_context}")

        # start tasks that are ready to run on your side
        self.trigger_job()

    def kill(self):
        job = self.session.query(Job).filter_by(job_id=self.job_id).first()
        assert job is not None, ValueError(f"job {self.job_id} not found")

        if job.main_party == settings.PARTY:
            join_parties = json.loads(job.join_parties)
            for party in join_parties:
                if party == settings.PARTY:
                    continue
                request_manager.kill(party, {"job_id": self.job_id})

        job.status = Status.FAIL
        tasks = self.session.query(Task).filter_by(job_id=self.job_id).all()
        assert tasks is not None, ValueError(f"tasks for job {self.job_id} not found")
        for task in tasks:
            if task.status == Status.RUNN:
                task.status = Status.FAIL
        session_commit_with_retry(self.session)

    def rerun(self):
        job = self.session.query(Job).filter_by(job_id=self.job_id).first()
        assert job is not None, ValueError(f"job {self.job_id} not found")

        # can only rerun failed or stopped jobs
        if job.status not in [Status.FAIL, Status.STOP]:
            return

        if job.main_party == settings.PARTY:
            join_parties = json.loads(job.join_parties)
            for party in join_parties:
                if party == settings.PARTY:
                    continue
                request_manager.rerun(party, {"job_id": self.job_id})

        job.status = Status.RUNN
        tasks = self.session.query(Task).filter_by(job_id=self.job_id).all()
        assert tasks is not None, ValueError(f"tasks for job {self.job_id} not found")
        for task in tasks:
            if task.status == Status.FAIL:
                task.status = Status.INIT
        session_commit_with_retry(self.session)
        self.trigger_job()

    def get_status(self) -> Dict:
        job = self.session.query(Job).filter_by(job_id=self.job_id).first()
        assert job, ValueError(f"job {self.job_id} not found")
        tasks = self.session.query(Task).filter_by(job_id=self.job_id).all()
        assert tasks, ValueError(f"tasks for job id {self.job_id} not found")
        task_status_map = {}
        for task in tasks:
            task_status_map[task.name] = Status.validate(task.status)

        progress = format(len(list(filter(lambda x: x.status == Status.SUCC, tasks))) / len(tasks), ".2%")
        return {"progress": progress, "job_status": job.status, "task_status": task_status_map}

    def update_task(self, task_name: str, task_status: str, external_context: Dict = None, max_retry=3):
        try:
            for i in range(max_retry):
                task_status = Status.validate(task_status)
                # only call this method on success or fail
                assert task_status in [Status.SUCC, Status.FAIL], ValueError(f"unexpected task status {task_status}")
                task = self.session.query(Task).filter_by(job_id=self.job_id, name=task_name).first()
                assert task is not None, ValueError(f"{self.job_id}.{task_name} not found")
                task.status = task_status

                job = self.session.query(Job).filter_by(job_id=self.job_id).first()
                assert job is not None, ValueError(f"{self.job_id} not found")
                job_context: Dict = json.loads(job.job_context)
                if external_context is not None:
                    deep_merge(job_context, external_context)
                    job.job_context = json.dumps(job_context)
                try:
                    session_commit_with_retry(self.session)
                except StaleDataError:
                    self.session.rollback()
                    if i < max_retry - 1:
                        continue
                    raise

            self.trigger_job()

            # broad task update
            if task.party == settings.PARTY:
                for party in json.loads(job.join_parties):
                    if party == settings.PARTY:
                        continue
                    params = {
                        "job_id": self.job_id,
                        "task_name": task_name,
                        "task_status": task_status,
                        # sync filtered job context to partner
                        "job_context": {
                            "common": job_context.get("common", {}),
                            party: job_context.get(party, {})
                        }
                    }
                    request_manager.update_task(party, params)
        except Exception as e:
            logging.exception("update task status fail after max retry")
            raise e

    def trigger_job(self):
        self._update_dag()
        status = self.dag.judge_job_status()
        if status == Status.RUNN:
            for task in self.dag.get_my_ready_tasks():
                self.start(task)
        else:
            job = self.session.query(Job).filter_by(job_id=self.job_id).first()
            job.status = status
            session_commit_with_retry(self.session)
            if status == Status.FAIL:
                for task in self.dag.get_my_running_tasks():
                    self.stop_task(task)

    def start(self, task: "LogicTask"):
        db_task = self.session.query(Task).filter_by(job_id=self.job_id, name=task.name).first()
        db_task.status = Status.RUNN
        try:
            session_commit_with_retry(self.session)
        except StaleDataError:
            logging.warning(f"{self.job_id}.{task.name} task status already changed")
            self.session.rollback()
            return
        task_executor = TaskExecutor(self.dag.mission_name, self.job_id, task)
        process = mp.Process(target=task_executor.start)
        process.start()

    def stop_task(self, task: "LogicTask"):
        pass
