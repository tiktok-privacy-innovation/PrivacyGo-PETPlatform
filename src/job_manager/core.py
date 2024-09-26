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
import json
import logging
from typing import Dict, List

import multiprocessing as mp

from constants import Status
from job_manager.dag import DAG, LogicTask
from job_manager.task import TaskExecutor
from models.job import Job
from models.mission import Mission
from models.task import Task
from network.request import request_manager
import settings
from utils.db_utils import session_commit_with_retry
from utils.deep_merge import deep_merge


class JobManager:
    _dag: "DAG" = None

    def __init__(self, job_id: str):
        from extensions import get_session_maker
        self.session_maker = get_session_maker()
        self.job_id = job_id

    @property
    def dag(self):
        if self._dag is None:
            self._dag = DAG(self.job_id)
        return self._dag

    def _update_dag(self):
        self._dag = DAG(self.job_id)

    def _get_mission(self, mission_name, mission_version) -> "Mission":
        with self.session_maker() as session:
            if mission_version == "latest":
                mission: "Mission" = session.query(Mission).filter_by(name=mission_name).order_by(
                    Mission.version.desc()).first()
            else:
                mission: "Mission" = session.query(Mission).filter_by(name=mission_name,
                                                                      version=int(mission_version)).first()
            if mission is None:
                raise ValueError(f"mission {mission_name}@v{mission_version} not found")
        return mission

    def _create_job(self,
                    mission,
                    job_context,
                    main_party: str,
                    join_parties: List[str],
                    user_name: str = None) -> "Job":
        return Job(job_id=self.job_id,
                   mission_name=mission.name,
                   mission_version=mission.version,
                   job_context=json.dumps(job_context),
                   main_party=main_party,
                   join_parties=json.dumps(join_parties),
                   status=Status.RUNN,
                   user_name=user_name or "")

    def _create_tasks(self, mission_dag) -> List["Task"]:
        return [
            Task(name=operator["name"],
                 job_id=self.job_id,
                 party=operator["party"],
                 args=json.dumps(operator.get("args", {})),
                 status=Status.INIT) for operator in mission_dag["operators"]
        ]

    def submit(self, params: Dict, user_name: str = None):
        with self.session_maker() as session:
            # does not allow parallel jobs
            running_jobs = session.query(Job).filter_by(status=Status.RUNN).all()
            if len(running_jobs) >= settings.MAX_JOB_LIMIT:
                raise Exception("running jobs has reached the upper limit, please try again later")

            # decide mission
            mission_name = params.get("mission_name", "ecdh_psi_optimized")
            mission_version = params.get("mission_version", "latest")
            mission = self._get_mission(mission_name, mission_version)

            # decide parties
            main_party = params.get("main_party", settings.PARTY)
            mission_dag = json.loads(mission.dag)
            join_parties = list({operator["party"] for operator in mission_dag["operators"]})

            # decide job context
            mission_params = params.get("mission_params", {})
            job_context = {party: {} for party in join_parties}
            job_context["common"] = {"__user_input": mission_params, "job_id": self.job_id}

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

            # create job & task
            job = self._create_job(mission, job_context, main_party, join_parties, user_name)
            tasks = self._create_tasks(mission_dag)

            # commit changes to db
            session.add(job)
            session.add_all(tasks)
            session_commit_with_retry(session)
            logging.info(f"created new job {self.job_id}:{mission_dag}@{mission_version}, job_context: {job_context}")

        self.trigger_job()

    def rerun(self):
        with self.session_maker() as session:
            job = session.query(Job).filter_by(job_id=self.job_id).first()
            if job is None:
                raise ValueError(f"job {self.job_id} not found")

            # can only rerun failed or canceled job
            if job.status not in [Status.FAIL, Status.CANC]:
                return

            if job.main_party == settings.PARTY:
                join_parties = json.loads(job.join_parties)
                for party in join_parties:
                    if party == settings.PARTY:
                        continue
                    # request_manager.rerun(party, self.job_id)

            job.status = Status.RUNN
            tasks = session.query(Task).filter_by(job_id=self.job_id).all()
            if not tasks:
                raise ValueError(f"tasks for job {self.job_id} not found")
            for task in tasks:
                if task.status in [Status.FAIL, Status.CANC]:
                    task.reset()
            session_commit_with_retry(session)

        self.trigger_job()

    def cancel(self):
        with self.session_maker() as session:
            job = session.query(Job).filter_by(job_id=self.job_id).first()
            if job is None:
                raise ValueError(f"job {self.job_id} not found")

            if job.main_party == settings.PARTY:
                join_parties = json.loads(job.join_parties)
                for party in join_parties:
                    if party == settings.PARTY:
                        continue
                    request_manager.cancel(party, self.job_id)

            job.status = Status.CANC
            tasks = session.query(Task).filter_by(job_id=self.job_id).all()
            if not tasks:
                raise ValueError(f"tasks for job {self.job_id} not found")
            for task in tasks:
                if task.status == Status.RUNN:
                    task.cancel()
            session_commit_with_retry(session)

        self.trigger_job()

    def get_job_details(self) -> Dict:
        with self.session_maker() as session:
            job = session.query(Job).filter_by(job_id=self.job_id).first()
            if job is None:
                raise ValueError(f"job {self.job_id} not found")
            tasks = session.query(Task).filter_by(job_id=self.job_id).all()
            if not tasks:
                raise ValueError(f"tasks for job id {self.job_id} not found")
        sorted_tasks = sorted(tasks, key=lambda task: task.start_time or datetime.utcnow())
        task_details = [task.details() for task in sorted_tasks]
        progress = format(len(list(filter(lambda x: x.status == Status.SUCC, tasks))) / len(tasks), ".2%")
        return {"job_id": self.job_id, "progress": progress, "job_status": job.status, "task_details": task_details}

    def get_jobs(self, user_name: str, status: str = None, hours: int = None, limit: int = 10) -> List:
        with self.session_maker() as session:
            query = session.query(Job).filter(Job.user_name == user_name)
            if status is not None:
                query = query.filter(Job.status == status)
            if hours is not None:
                start_time = datetime.utcnow() - timedelta(hours=hours)
                query = query.filter(Job.create_time >= start_time)
            jobs = query.limit(limit).all()
            return [job.simple_to_dict() for job in jobs]

    def update_task(self, task_name: str, task_status: str, external_context: Dict = None, errors: str = None):
        with self.session_maker() as session:
            task_status = Status.validate(task_status)
            task = session.query(Task).filter_by(job_id=self.job_id, name=task_name).first()
            if task is None:
                raise ValueError(f"{self.job_id}.{task_name} not found")
            job = session.query(Job).filter_by(job_id=self.job_id).first()
            if job is None:
                raise ValueError(f"{self.job_id} not found")
            job_context: Dict = json.loads(job.job_context)

            if task_status == Status.RUNN:
                task.run()
            elif task_status == Status.SUCC:
                task.success()
                if external_context is not None:
                    deep_merge(job_context, external_context)
                    job.job_context = json.dumps(job_context)
            elif task_status == Status.FAIL:
                task.fail(errors)
            else:
                raise ValueError(f"unexpected task status {task_status}")
            session_commit_with_retry(session)

            # broadcast task update
            params = {"task_status": task_status}
            if task.party == settings.PARTY:
                for party in json.loads(job.join_parties):
                    if party == settings.PARTY:
                        continue
                    if task_status == Status.SUCC:
                        # sync filtered job context to partner
                        params["job_context"] = {
                            "common": job_context.get("common", {}),
                            party: job_context.get(party, {})
                        }
                    if task_status == Status.FAIL:
                        params["errors"] = errors
                    request_manager.update_task(party, self.job_id, task_name, params)

        if task_status in [Status.SUCC, Status.FAIL]:
            self.trigger_job()

    def trigger_job(self):
        # start tasks that are ready to run on your side
        with self.session_maker() as session:
            self._update_dag()
            status = self.dag.judge_job_status()
            if status == Status.RUNN:
                for task in self.dag.get_my_ready_tasks():
                    self.start_task(task)
            else:
                job = session.query(Job).filter_by(job_id=self.job_id).first()
                job.status = status
                session_commit_with_retry(session)
                if status in [Status.FAIL, Status.CANC]:
                    for task in self.dag.get_my_running_tasks():
                        self.stop_task(task)

    def start_task(self, task: "LogicTask"):
        task_executor = TaskExecutor(self.dag.mission_name, self.job_id, task)
        process = mp.Process(target=task_executor.start)
        process.start()

    def stop_task(self, task: "LogicTask"):
        pass
