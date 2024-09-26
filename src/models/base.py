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
from sqlalchemy import Integer, BigInteger, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base


class BigIntOrInteger(TypeDecorator):
    impl = BigInteger
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'sqlite':
            return dialect.type_descriptor(Integer())
        else:
            return dialect.type_descriptor(BigInteger())


Base = declarative_base()
