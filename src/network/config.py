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
import hashlib
import json
from typing import Iterable
from pathlib import Path
import logging

import settings
from utils.url_utils import get_url_netloc


class NetworkConfig:

    def __init__(self):
        self.party_config = {}
        configfile = Path(settings.CONFIG_FILE)
        if configfile.exists() and configfile.is_file():
            self.party_config = json.loads(configfile.read_text())
        else:
            logging.warning(f"fail to load party config from {configfile}")

    def generate(self, join_parties: Iterable, passphrase):
        if settings.NETWORK_SCHEME == "agent":
            config = self._agent_config(join_parties, passphrase)
        else:
            config = self._socket_config(join_parties, passphrase)
        return config

    def _socket_config(self, join_parties: Iterable, passphrase):
        parties = {}
        for party in join_parties:
            port = self._get_random_port(seed=f"{passphrase}.{party}",
                                         lb=settings.PORT_LOWER_BOUND,
                                         ub=settings.PORT_UPPER_BOUND)
            address = get_url_netloc(self.party_config[party]["petplatform"]["url"])
            address_no_port = address.split(":")[0]
            parties[party] = {"address": [address_no_port + f":{port}"]}
        return {"network_mode": "petnet", "network_scheme": "socket", "parties": parties}

    def _agent_config(self, join_parties: Iterable, prefix):
        parties = {}
        for party in join_parties:
            address = get_url_netloc(self.party_config[party]["petnet"][0]["url"])
            parties[party] = {"address": [address]}
        return {"network_mode": "petnet", "network_scheme": "agent", "shared_topic": prefix, "parties": parties}

    def _get_random_port(self, seed: str, lb: int = 49152, ub: int = 65535) -> int:
        if not (0 <= lb < ub <= 65536):
            raise ValueError(f"invalid port range: {lb}-{ub}")
        sha256 = hashlib.sha256()
        sha256.update(seed.encode("utf-8"))
        digest = sha256.hexdigest()
        big_int = int(digest, 16)
        mapped_port = lb + (big_int % (ub - lb))
        return mapped_port


network_config = NetworkConfig()

if __name__ == '__main__':
    print(network_config._agent_config(["party_a", "party_b"], "prefix"))
