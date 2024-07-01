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
from urllib.parse import urlparse, urlunparse


def remove_http_https(address):
    parsed = urlparse(address)
    return parsed.netloc + parsed.path


def remove_port(url):
    parsed = urlparse(url)
    netloc = parsed.hostname  # without port
    rebuilt = parsed._replace(netloc=netloc)
    return urlunparse(rebuilt)


def get_url_netloc(url):
    if '://' not in url:
        url = 'http://' + url
    result = urlparse(url)
    return result.netloc
