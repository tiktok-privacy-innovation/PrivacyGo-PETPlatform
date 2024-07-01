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

    def __init__(self, session, job_id: str):
        self.session = session
        self.job_id = job_id

    def get(self, key: str, party: str = None) -> Union[str, Dict, None]:
        job = self.session.query(Job).filter_by(job_id=self.job_id).first()
        assert job is not None, ValueError(f"{self.job_id} not found")
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
        keys, updated_context = key.split("."), {party: {}}
        cursor = updated_context[party]
        for k in keys[:-1]:
            cursor[k] = {}
            cursor = cursor[k]
        cursor[keys[-1]] = value
        for _ in range(max_retry):
            job = self.session.query(Job).filter_by(job_id=self.job_id).first()
            assert job is not None, ValueError(f"{self.job_id} not found")
            job_context: Dict = json.loads(job.job_context)
            assert party in job_context, ValueError(f"party {party} not found")
            assert isinstance(job_context[party], dict), ValueError(f"job_context[{party}] is not a dict")
            deep_merge(job_context, updated_context)
            job.job_context = json.dumps(job_context)
            try:
                session_commit_with_retry(self.session)
                return True
            except StaleDataError:
                # This happens when two jobs try to modify the same record,
                # this modification fails due to the optimistic lock.
                # Retry until reach max retry times.
                self.session.rollback()
                continue
        return False

    def get_all(self) -> Dict:
        job = self.session.query(Job).filter_by(job_id=self.job_id).first()
        assert job is not None, ValueError(f"{self.job_id} not found")
        context: Dict = json.loads(job.job_context)
        return context

    def set_all(self, configs: Dict[str, Union[str, Dict, List]], party: str = "common", max_retry=3):
        for k in configs:
            assert "." not in k, ValueError(f"unexpected special character '.' in key {k}")
        for _ in range(max_retry):
            job = self.session.query(Job).filter_by(job_id=self.job_id).first()
            assert job is not None, ValueError(f"{self.job_id} not found")
            job_context: Dict = json.loads(job.job_context)
            assert party in job_context, ValueError(f"party {party} not found")
            assert isinstance(job_context[party], dict), ValueError(f"job_context[{party}] is not a dict")
            deep_merge(job_context[party], configs)
            job.job_context = json.dumps(job_context)
            try:
                session_commit_with_retry(self.session)
                return True
            except StaleDataError:
                self.session.rollback()
                continue
        return False
