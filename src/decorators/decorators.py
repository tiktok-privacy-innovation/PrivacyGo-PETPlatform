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
from flask import g, request, jsonify
from functools import wraps
import jwt
import logging

from exceptions.exceptions import BaseError, ValidationError, AuthorizationError
from extensions import get_session_maker
from models.user import User, Role
from models.job import Job
import settings

session_maker = get_session_maker()


def jwt_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        headers = request.headers

        if "Authorization" in headers:
            token = headers["Authorization"].replace("Bearer ", "")
        if not token:
            raise ValidationError("JWT token is missing")
        try:
            payload = jwt.decode(token, settings.SECRET, algorithms=["HS256"])
            if "name" not in payload:
                raise ValueError
            with session_maker() as session:
                user = session.query(User).filter_by(name=payload["name"]).first()
                if user and user.validate():
                    g.validated_user = user.to_dict()
                else:
                    raise
        except Exception:
            raise ValidationError("JWT token is invalid")

        return f(*args, **kwargs)

    return wrapper


def check_job_permission(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if not hasattr(g, "validated_user") or "name" not in g.validated_user:
                raise ValueError
            user_name = g.validated_user["name"]
            job_id = kwargs.get("job_id")
            if not job_id.startswith("j_"):
                raise ValueError(f"invalid job_id {job_id} in request path")
            with session_maker() as session:
                job = session.query(Job).filter_by(job_id=job_id).first()
                if job is None or job.user_name != user_name:
                    raise
        except Exception:
            raise AuthorizationError("Unauthorized operation")

        return f(*args, **kwargs)

    return wrapper


def is_node(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if not hasattr(g, "validated_user") or g.validated_user["role"] != Role.node:
                raise ValueError
        except Exception:
            raise AuthorizationError("Unauthorized operation")

        return f(*args, **kwargs)

    return wrapper


def log_and_handle_exceptions(f):

    def log_and_return_error(error, code):
        logging.exception(str(error))
        return jsonify({
            "success": False,
            "error_message": str(error),
        }), code

    @wraps(f)
    def wrapper(*args, **kwargs):

        try:
            body = request.get_json()
        except Exception:
            body = ""
        try:
            logging.info(f"Request to {request.url} with headers {request.headers} and body {body}")
            response, code = f(*args, **kwargs)
            logging.info(f"Response with status {response.status_code} and body {response.get_json()}")
            return response, code
        except BaseError as e:
            return log_and_return_error(e, e.code)
        except Exception as e:
            return log_and_return_error(e, 500)

    return wrapper
