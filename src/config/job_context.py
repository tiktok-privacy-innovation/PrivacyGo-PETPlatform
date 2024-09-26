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
from typing import Union, Dict, List

from sqlalchemy.orm.exc import StaleDataError

from models.job import Job
import settings
from utils.db_utils import session_commit_with_retry
from utils.deep_merge import deep_merge


class JobContext:

    def __init__(self, job_id: str):
        from extensions import get_session_maker
        self.session_maker = get_session_maker()
        self.job_id = job_id

    def get(self, key: str, party: str = None) -> Union[str, Dict, None]:
        with self.session_maker() as session:
            job = session.query(Job).filter_by(job_id=self.job_id).first()
            if job is None:
                raise ValueError(f"{self.job_id} not found")
        context: Dict = json.loads(job.job_context)
        # select search domain
        search_domain = [settings.PARTY, "common"] if party is None else [party]
        keys = key.split(".")
        for domain in search_domain:
            if domain not in context:
                continue
            # search the target key recursively
            target, found = context[domain], True
            for k in keys:
                if not isinstance(target, dict) or k not in target:
                    found = False
                    break
                else:
                    target = target[k]
            if found:
                return target
        # key not found in local party or common
        return None

    def set(self, key: str, value: Union[str, Dict, List], party: str, max_retry=3) -> bool:
        with self.session_maker() as session:
            keys, updated_context = key.split("."), {party: {}}
            cursor = updated_context[party]
            for key in keys[:-1]:
                cursor[key] = {}
                cursor = cursor[key]
            cursor[keys[-1]] = value
            for i in range(max_retry):
                job = session.query(Job).filter_by(job_id=self.job_id).first()
                assert job is not None, ValueError(f"{self.job_id} not found")
                job_context: Dict = json.loads(job.job_context)
                assert party in job_context, ValueError(f"party {party} not found")
                assert isinstance(job_context[party], dict), ValueError(f"job_context[{party}] is not a dict")
                deep_merge(job_context, updated_context)
                job.job_context = json.dumps(job_context)
                try:
                    session_commit_with_retry(session)
                    return True
                except StaleDataError:
                    continue
            return False

    def set_all(self, configs: Dict[str, Union[str, Dict, List]], party: str = "common", max_retry=3):
        with self.session_maker() as session:
            for k in configs:
                assert "." not in k, ValueError(f"unexpected special character '.' in key {k}")
            for i in range(max_retry):
                job = session.query(Job).filter_by(job_id=self.job_id).first()
                assert job is not None, ValueError(f"{self.job_id} not found")
                job_context: Dict = json.loads(job.job_context)
                assert party in job_context, ValueError(f"party {party} not found")
                assert isinstance(job_context[party], dict), ValueError(f"job_context[{party}] is not a dict")
                deep_merge(job_context[party], configs)
                job.job_context = json.dumps(job_context)
                try:
                    session_commit_with_retry(session)
                    return True
                except StaleDataError:
                    continue
            return False
