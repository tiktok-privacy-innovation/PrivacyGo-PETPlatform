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
import logging
import time
from typing import Dict

import requests

from .config import network_config


class RequestManager:

    def __init__(self):
        self.party_address: Dict = network_config.party_config

    def submit(self, party: str, params: Dict) -> bool:
        return self._action(party=party, endpoint="job/submit", json=params)

    def kill(self, party: str, params: Dict) -> bool:
        return self._action(party=party, endpoint="job/kill", json=params)

    def rerun(self, party: str, params: Dict) -> bool:
        return self._action(party=party, endpoint="job/rerun", json=params)

    def update_task(self, party, params: Dict):
        return self._action(party, endpoint="task/update", json=params)

    def _action(self, party: str, endpoint: str, json: Dict, max_retry: int = 3, timeout: int = 10) -> bool:
        address = self.party_address.get(party)["petplatform"]["url"]
        headers = self.party_address.get(party)["petplatform"].get("headers")
        for i in range(max_retry):
            try:
                response = self._post(address, endpoint, json, headers=headers, timeout=timeout)
                response.raise_for_status()
                if response.status_code == 204:
                    raise ConnectionError
                response_data = response.json()
                if not response_data['success']:
                    raise Exception(response_data["error_message"])
                return True
            except Exception:
                if i < max_retry - 1:
                    sleep_time = 0.001 * (2**i)
                    time.sleep(sleep_time)
        raise Exception("request fail")

    def _post(self, address: str, endpoint: str, json: Dict, data=None, headers=None, timeout=10):
        url = f"{address}/{endpoint}"
        post_headers = {"Content-Type": "application/json"}
        if headers is not None:
            post_headers.update(headers)
        try:
            logging.info(f"send post request to {url}, json={json}, data={data}, headers={headers}")
            response = requests.post(url, json=json, data=data, headers=post_headers, timeout=timeout)
            logging.info(f"response: {response.json()}")
            return response
        except Exception as e:
            logging.exception(f"post fail: {address}/{endpoint}, headers={headers}, json={json}, data={data}")
            raise e


request_manager = RequestManager()
