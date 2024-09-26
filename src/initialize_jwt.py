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
import secrets

import jwt


def generate_secret():
    return secrets.token_hex(32)


def generate_token(secret, payload, algorithm='HS256'):
    return jwt.encode(payload, secret, algorithm)


if __name__ == '__main__':
    import os

    # Generate a secure random string of 32 bytes
    # jwt_secret = generate_secret()
    # print(jwt_secret)

    secret = os.environ.get('secret')
    print(generate_token(secret, {'name': 'test_account_1'}))
    print(generate_token(secret, {'name': 'cn_node_1'}))
    print(generate_token(secret, {'name': 'va_node_1'}))

    print(generate_token(secret, {'name': 'user_0'}))
