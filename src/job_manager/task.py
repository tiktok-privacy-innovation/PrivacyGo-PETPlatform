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
import importlib
import logging
import re
import time
from typing import Dict

from constants import Status
from job_manager.dag import LogicTask
from network.config import network_config
import settings
from utils.deep_merge import deep_merge
from utils.path_utils import traverse_and_validate


class TaskExecutor:

    def __init__(self, mission_name, job_id: str, task: "LogicTask"):
        self.mission_name = mission_name
        self.job_id = job_id
        self.task_name = task.name
        self.party = task.party
        self.class_path = task.class_path
        self.class_name = task.class_name
        self.args = task.args
        self.start_time = time.time()

    def start(self):
        from job_manager.core import JobManager
        from config.config_manager import ConfigManager
        config_manager = ConfigManager(mission_name=self.mission_name, job_id=self.job_id)
        job_manager = JobManager(job_id=self.job_id)
        success, errors = False, None
        try:
            job_manager.update_task(self.task_name, Status.RUNN)
            operator_class = self._load_class()
            assert operator_class, RuntimeError(f"fail to load operator {self.class_name} from {self.class_path}")
            configmap = self._parse_configmap(config_manager)
            args_value_map: Dict = self._parse_args(config_manager=config_manager)
            logging.info(f"ready to execute {self.job_id}.{self.task_name}, args: {args_value_map}")
            operator = operator_class(party=self.party, config_manager=config_manager, **args_value_map)
            success = operator.run(configmap=configmap)
        except Exception as e:
            logging.exception(f"execute task {self.job_id}.{self.task_name} fail")
            errors = str(e)
        finally:
            exec_time = time.time() - self.start_time
            logging.info(
                f"{self.job_id}.{self.task_name} finish, success: {success}, exec time: {exec_time}, errors: {errors}")
            try:
                job_manager.update_task(self.task_name, Status.SUCC if success else Status.FAIL, errors=errors)
            except Exception:
                logging.exception(f"update task status fail")

    def _load_class(self):
        module = importlib.import_module(self.class_path)
        my_class = getattr(module, self.class_name)
        return my_class

    def _parse_configmap(self, config_manager) -> Dict:
        job_context: Dict = config_manager.job_context.get_all()
        join_parties = set(job_context.keys())
        join_parties.remove("common")

        configmap = {}
        user_input = job_context["common"].pop("__user_input", {})
        for party in join_parties:
            configmap[party] = job_context[party]
            party_config = user_input.pop(party, {})
            deep_merge(configmap[party], party_config)
        configmap["common"] = job_context["common"]
        deep_merge(configmap["common"], user_input)
        # add network config
        net_config = network_config.generate(join_parties, f"{self.job_id}.{self.class_path}.{self.class_name}")
        configmap["common"].update(net_config)
        return self._validated_params(configmap)

    def _validated_params(self, params: Dict):
        return traverse_and_validate(params, safe_workdir=settings.SAFE_WORK_DIR)

    def _parse_args(self, config_manager) -> Dict:
        parsed_args = {}
        for args_key, args_value in self.args.items():
            if isinstance(args_value, str):
                if args_value.startswith("$"):
                    # args_value in the form "${job_context.a.b.c}"
                    real_key: str = re.findall(r'\${(.*?)}', args_value)[0]
                    if real_key.startswith("job_context."):
                        args_value = config_manager.job_context.get(real_key[len("job_context."):])
                    elif real_key.startswith("mission_context."):
                        args_value = config_manager.mission_context.get(real_key[len("mission_context."):])
                    elif real_key.startswith("global_config."):
                        args_value = config_manager.global_config.get(real_key[len("global_config."):])
                    else:
                        raise Exception("no real args key context find")
            parsed_args[args_key] = args_value
        return parsed_args
