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
import platform

# --------------------------------------- Logging ---------------------------------------
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'petplatform.log' if platform.system().lower() == "darwin" else '/app/logs/petplatform.log',
            'formatter': 'default'
        }
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': "INFO"
    }
}

PLATFORM_DB_URI = os.environ.get("PLATFORM_DB_URI", "sqlite:////app/db/petplatform.db")
PARTY: str = os.environ.get("PARTY")
if PARTY is None:
    raise EnvironmentError("env PARTY not found")

CONFIG_FILE = os.environ.get("CONFIG_FILE", "/app/parties/party.json")
SAFE_WORK_DIR = os.environ.get("SAFE_WORK_DIR", "/app/data/")
NETWORK_SCHEME = os.environ.get("NETWORK_SCHEME", "agent")
PORT_LOWER_BOUND = int(os.environ.get("PORT_LOWER_BOUND", "49152"))
PORT_UPPER_BOUND = int(os.environ.get("PORT_UPPER_BOUND", "65535"))
