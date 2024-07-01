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


class TimeDuration:
    SECOND = 1
    MINUTE = 60 * SECOND
    HOUR = MINUTE * 60
    DAY = 24 * HOUR
    WEEK = 7 * DAY
    MONTH = 30 * DAY
    YEAR = 365 * DAY


class Status:
    INIT = "INIT"
    RUNN = "RUNNING"
    STOP = "STOPPED"
    FAIL = "FAILED"
    SUCC = "SUCCESS"

    allowed_status = [INIT, RUNN, STOP, FAIL, SUCC]

    @classmethod
    def validate(cls, status: str):
        assert status in cls.allowed_status, ValueError(f"invalid status key {status}")
        return status
