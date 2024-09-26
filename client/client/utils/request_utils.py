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
from typing import Dict

import requests
from requests.exceptions import Timeout


def send_request(method: str,
                 address: str,
                 endpoint: str,
                 params: Dict = None,
                 headers: Dict = None,
                 json: Dict = None,
                 data=None,
                 timeout=10,
                 return_json=True):
    url = "{address}/{endpoint}".format(address=address, endpoint=endpoint.lstrip('/'))
    request_headers = {"Content-Type": "application/json"}
    if headers:
        request_headers.update(headers)
    try:
        logging.debug(f"send {method} request to {url}, params={params}, json={json}, data={data}, headers={headers}")
        response = requests.request(method,
                                    url,
                                    params=params,
                                    json=json,
                                    data=data,
                                    headers=request_headers,
                                    timeout=timeout)
    except Timeout:
        logging.error(f"{method} request timed out: {address}/{endpoint}, headers={headers}, json={json}, data={data}")
        raise
    except Exception:
        logging.exception(f"{method} fail: {address}/{endpoint}, headers={headers}, json={json}, data={data}")
        raise

    if response.status_code >= 400:
        logging.error(f"{method} request error status {response.status_code}: "
                      f"{address}/{endpoint}, "
                      f"headers={headers}, "
                      f"json={json}, "
                      f"data={data}")
        response.raise_for_status()

    logging.debug(f"response: {response.json()}")
    return response.json() if return_json else response


def delete(address: str,
           endpoint: str,
           params: Dict = None,
           headers: Dict = None,
           json: Dict = None,
           timeout=10,
           return_json=True):
    return send_request("DELETE", address, endpoint, params, headers, json, None, timeout, return_json)


def get(address: str, endpoint: str, params: Dict = None, headers: Dict = None, timeout=10, return_json=False):
    return send_request("GET", address, endpoint, params, headers, None, None, timeout, return_json=return_json)


def patch(address: str,
          endpoint: str,
          params: Dict = None,
          headers: Dict = None,
          json: Dict = None,
          data=None,
          timeout=10,
          return_json=True):
    return send_request("PATCH", address, endpoint, params, headers, json, data, timeout, return_json)


def post(address: str,
         endpoint: str,
         params: Dict = None,
         headers: Dict = None,
         json: Dict = None,
         data=None,
         timeout=10,
         return_json=True):
    return send_request("POST", address, endpoint, params, headers, json, data, timeout, return_json)


def put(address: str,
        endpoint: str,
        params: Dict = None,
        headers: Dict = None,
        json: Dict = None,
        data=None,
        timeout=10,
        return_json=True):
    return send_request("PUT", address, endpoint, params, headers, json, data, timeout, return_json)
