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
from dataclasses import dataclass
import json
from typing import List, Dict

from constants import Status
from models.job import Job
from models.mission import Mission
from models.task import Task
import settings


@dataclass
class LogicTask:
    name: str
    party: str
    args: Dict
    status: str
    depends: List[str]
    class_name: str
    class_path: str


class DAG:

    def __init__(self, job_id):
        self.mission_name = None
        self.mission_version = None
        self.job_id = job_id
        self._init_dag()

    def _init_dag(self):
        from extensions import get_session_maker
        session_maker = get_session_maker()
        with session_maker() as session:
            job: "Job" = session.query(Job).filter_by(job_id=self.job_id).first()
            self.mission_name, self.mission_version = job.mission_name, job.mission_version
            mission: "Mission" = session.query(Mission).filter_by(name=self.mission_name,
                                                                  version=self.mission_version).first()
            tasks: List[Task] = session.query(Task).filter_by(job_id=self.job_id).all()

        dag: Dict = json.loads(mission.dag)
        self.tasks = {
            v["name"]:
                LogicTask(v["name"], v["party"], v.get("args", {}), "", v.get("depends", []), v['class'],
                          v['class_path']) for v in dag["operators"]
        }
        diff_set = set(self.tasks.keys()).difference(set([v.name for v in tasks]))
        assert len(diff_set) == 0, ValueError(f"task missed: {diff_set}")

        # update task status
        for task in tasks:
            self.tasks[task.name].status = task.status

    def get_my_ready_tasks(self) -> List["LogicTask"]:
        ready_tasks = []
        for task in self.tasks.values():
            if task.party != settings.PARTY:
                continue
            if task.status != Status.INIT:
                continue
            is_ready = True
            for dep_name in task.depends:
                assert dep_name in self.tasks, ValueError(f"{dep_name} not included in dag")
                dep = self.tasks.get(dep_name)
                if dep.status != Status.SUCC:
                    is_ready = False
                    break
            if is_ready:
                ready_tasks.append(task)
        return ready_tasks

    def get_my_running_tasks(self) -> List["LogicTask"]:
        running = []
        for task in self.tasks.values():
            if task.party != settings.PARTY:
                continue
            if task.status == Status.RUNN:
                running.append(task)
        return running

    def judge_job_status(self) -> "Status":
        num_init, num_running, num_success, num_failed, num_canceled = 0, 0, 0, 0, 0
        for task in self.tasks.values():
            if task.status in [Status.FAIL]:
                num_failed += 1
            if task.status in [Status.CANC]:
                num_canceled += 1
            if task.status in [Status.SUCC]:
                num_success += 1
            if task.status in [Status.INIT]:
                num_init += 1
            if task.status in [Status.RUNN]:
                num_running += 1
        if num_failed > 0:
            # some tasks failed or stopped
            return Status.FAIL
        elif num_canceled > 0:
            return Status.CANC
        elif num_success == len(self.tasks):
            # all tasks success
            return Status.SUCC
        else:
            return Status.RUNN
