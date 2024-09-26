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
from typing import Dict, List

from .utils.request_utils import get, post


class PlatformClient:

    def __init__(self, server_url: str, jwt_token: str):
        self._server_url = server_url
        self._jwt_token = jwt_token

    def __str__(self):
        return f"PlatformClient instance with server_url={self._server_url} and jwt_token={self._jwt_token}"

    def __repr__(self):
        return f"PlatformClient({self._server_url}, {self._jwt_token})"

    def _get_address(self) -> str:
        return self._server_url

    def _get_headers(self) -> Dict:
        return {"Authorization": f"Bearer {self._jwt_token}"}

    def submit(self, params: Dict) -> bool:
        address = self._get_address()
        headers = self._get_headers()
        response = post(address, "api/v1/jobs", json=params, headers=headers)
        if response.get("success") is not True:
            errors = response.get("error_message", "unknown errors")
            raise Exception(f"bad request: {errors}")
        return True

    def rerun(self, job_id: str) -> bool:
        address = self._get_address()
        headers = self._get_headers()
        response = post(address, f"api/v1/jobs/{job_id}/rerun", headers=headers)
        if response.get("success") is not True:
            errors = response.get("error_message", "unknown errors")
            raise Exception(f"bad request: {errors}")
        return True

    def cancel(self, job_id: str) -> bool:
        address = self._get_address()
        headers = self._get_headers()
        response = post(address, f"api/v1/jobs/{job_id}/cancel", headers=headers)
        if response.get("success") is not True:
            errors = response.get("error_message", "unknown errors")
            raise Exception(f"bad request: {errors}")
        return True

    def get(self, job_id: str) -> Dict:
        address = self._get_address()
        headers = self._get_headers()
        response = get(address, f"api/v1/jobs/{job_id}", headers=headers, return_json=True)
        if response.get("success") is not True:
            errors = response.get("error_message", "unknown errors")
            raise Exception(f"bad request: {errors}")
        return response["job"]

    def get_all(self, status: str = None, hours: int = 24, limit: int = 10) -> List:
        address = self._get_address()
        headers = self._get_headers()
        params = {"hours": hours, "limit": limit}
        if status is not None:
            if not isinstance(status, str):
                raise ValueError("status must be a string")
            params["status"] = status
        response = get(address, f"api/v1/jobs", headers=headers, params=params, return_json=True)
        if response.get("success") is not True:
            errors = response.get("error_message", "unknown errors")
            raise Exception(f"bad request: {errors}")
        return response["jobs"]
