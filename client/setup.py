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
from setuptools import setup, find_packages

setup(
    name='petplatform-client',
    version='0.1.0',
    description='SDK and Commandline Tools for PETPlatform',
    author="PrivacyGo-PETPlatform",
    author_email="privacygo-petplatform@tiktok.com",
    packages=find_packages('.', exclude=['tests']),
    package_dir={'': '.'},
    install_requires=['click', 'python-dotenv', 'requests'],
    entry_points={
        'console_scripts': ['petplatform-cli=client.cli:cli'],
    },
)
