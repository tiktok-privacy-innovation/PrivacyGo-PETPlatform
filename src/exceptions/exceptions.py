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


class BaseError(Exception):

    def __init__(self, message, code=500):
        super().__init__(message)
        self.message = message
        self.code = code


class ValidationError(BaseError):

    def __init__(self, message):
        super().__init__(message, code=401)


class AuthorizationError(BaseError):

    def __init__(self, message):
        super().__init__(message, code=403)


class NotFoundError(BaseError):

    def __init__(self, message):
        super().__init__(message)
