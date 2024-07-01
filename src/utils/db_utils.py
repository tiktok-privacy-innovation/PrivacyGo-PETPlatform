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
import time

from sqlalchemy.exc import OperationalError


def session_commit_with_retry(session, max_retry=3):
    for i in range(max_retry):
        try:
            session.commit()
            # If commit() succeed, break the loop and return.
            return
        except OperationalError:
            session.rollback()
            if i < max_retry - 1:  # No need to sleep after the last attempt
                sleep_time = 0.001 * (2**i)  # exponential backoff, 1, 2, 4, ...
                time.sleep(sleep_time)
    # If all retries failed, or encounter unexpected exception, raise.
    raise
