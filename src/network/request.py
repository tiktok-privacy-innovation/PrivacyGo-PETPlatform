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
from typing import Dict

import settings
from network.config import network_config
from utils.request_utils import post, patch


class RequestManager:

    def __init__(self):
        self.party_address: Dict = network_config.party_config

    def _get_address(self, party: str) -> str:
        if party not in self.party_address:
            raise ValueError(f"invalid party {party}")
        return self.party_address.get(party)["address"]

    def _get_headers(self, party: str) -> Dict:
        if party not in self.party_address:
            raise ValueError(f"invalid party {party}")
        headers = {"Authorization": f"Bearer {settings.JWT_TOKEN}"}
        headers.update(self.party_address[party].get("headers", {}))
        return headers

    def submit(self, party: str, params: Dict):
        address = self._get_address(party)
        headers = self._get_headers(party)
        response = post(address, "api/v1/jobs", json=params, headers=headers)
        if not response.get("success", False):
            errors = response.get("error_message", "unknown errors")
            raise Exception(f"bad request: {errors}")

    def rerun(self, party: str, job_id: str):
        address = self._get_address(party)
        headers = self._get_headers(party)
        response = post(address, f"api/v1/jobs/{job_id}/rerun", headers=headers)
        if not response.get("success", False):
            errors = response.get("error_message", "unknown errors")
            raise Exception(f"bad request: {errors}")

    def cancel(self, party: str, job_id: str):
        address = self._get_address(party)
        headers = self._get_headers(party)
        response = post(address, f"api/v1/jobs/{job_id}/cancel", headers=headers)
        if not response.get("success", False):
            errors = response.get("error_message", "unknown errors")
            raise Exception(f"bad request: {errors}")

    def update_task(self, party, job_id: str, task_name: str, params: Dict):
        address = self._get_address(party)
        headers = self._get_headers(party)
        response = patch(address, f"api/v1/tasks/{job_id}/{task_name}", json=params, headers=headers)
        if not response.get("success", False):
            errors = response.get("error_message", "unknown errors")
            raise Exception(f"bad request: {errors}")


request_manager = RequestManager()
