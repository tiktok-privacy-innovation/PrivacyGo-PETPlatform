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
from typing import Any, Union, Dict, List


def is_existing_dir(pathlike: str):
    return os.path.isdir(pathlike)


def is_existing_file(pathlike: str):
    return os.path.isfile(pathlike)


def is_existing_dir_or_file(pathlike: str):
    return os.path.exists(pathlike)


def validated_pathlike(pathlike: Any, safe_workdir: str) -> Union[str, Any]:
    if not isinstance(pathlike, str) or not is_existing_dir_or_file(pathlike):
        return pathlike
    safe_workdir_abs = os.path.abspath(safe_workdir)
    # If filepath is a directory, return the absolute path of safe_workdir
    if is_existing_dir(pathlike):
        return safe_workdir_abs
    else:
        basename = os.path.basename(pathlike)
        return os.path.join(safe_workdir_abs, basename)


def traverse_and_validate(d: Union[Dict, List, str, int, float, bool], safe_workdir: str):
    # Check if safe_workdir is an existing directory
    if not is_existing_dir(safe_workdir):
        raise NotADirectoryError(safe_workdir)
    for k, v in d.items():
        if isinstance(v, dict):
            traverse_and_validate(v, safe_workdir)
        elif isinstance(v, list):
            d[k] = [
                traverse_and_validate(i, safe_workdir) if isinstance(i, dict) else validated_pathlike(i, safe_workdir)
                for i in v
            ]
        else:
            d[k] = validated_pathlike(v, safe_workdir)
    return d
