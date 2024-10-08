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
import logging.config

import flask
from flask_sqlalchemy import SQLAlchemy

from models.base import Base
import settings
from views.default_views import default_views
from views.v1 import v1

logging.config.dictConfig(settings.LOGGING_CONFIG)
app = flask.Flask(__name__)
app.register_blueprint(default_views)
app.register_blueprint(v1)
app.config['SQLALCHEMY_DATABASE_URI'] = settings.PLATFORM_DB_URI
db = SQLAlchemy(app=app, model_class=Base)

if __name__ == '__main__':
    # Never run debug mode in production environment!
    app.run(debug=False)
