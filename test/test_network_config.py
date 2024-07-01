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
import os
import unittest


class TestNetworkConfig(unittest.TestCase):

    def setUp(self) -> None:
        os.environ["PARTY"] = "party_a"
        self.join_parties = ["party_a", "party_b"]
        self.passphrase = "test_network_config"

    def tearDown(self) -> None:
        pass

    def test_network_config(self):
        import settings
        from network.config import NetworkConfig
        settings.CONFIG_FILE = "./configfiles/party.json"
        network_config = NetworkConfig()

        socket_config = network_config.generate(join_parties=self.join_parties, passphrase=self.passphrase)
        self.assertEqual(
            socket_config, {
                "network_mode": "petnet",
                "network_scheme": "socket",
                "parties": {
                    "party_a": {
                        "address": ["127.0.0.1:49702"]
                    },
                    "party_b": {
                        "address": ["127.0.0.2:60082"]
                    }
                }
            })

        settings.NETWORK_SCHEME = "agent"
        agent_config = network_config.generate(join_parties=self.join_parties, passphrase=self.passphrase)
        self.assertEqual(
            agent_config, {
                "network_mode": "petnet",
                "network_scheme": "agent",
                "shared_topic": "test_network_config",
                "parties": {
                    "party_a": {
                        "address": ["127.0.0.1:1235"]
                    },
                    "party_b": {
                        "address": ["127.0.0.2:1235"]
                    }
                }
            })
