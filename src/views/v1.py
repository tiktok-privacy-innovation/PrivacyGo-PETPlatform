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
from flask import g, request, jsonify, Blueprint

from constants import Status
from decorators.decorators import jwt_required, is_node, check_job_permission, log_and_handle_exceptions
from job_manager.core import JobManager
from utils.id_utils import generate_job_id

v1 = Blueprint('v1_views', __name__)


@v1.route("/api/v1/jobs", methods=["POST"])
@log_and_handle_exceptions
@jwt_required
def submit():
    user_name = g.validated_user["name"]
    params = request.json
    job_id = params.get("job_id", generate_job_id())
    job_manager = JobManager(job_id)
    job_manager.submit(params, user_name)

    return jsonify({"success": True, "job_id": job_id}), 200


@v1.route("/api/v1/jobs/<job_id>/rerun", methods=["POST"])
@log_and_handle_exceptions
@jwt_required
@check_job_permission
def rerun(job_id):
    job_manager = JobManager(job_id)
    job_manager.rerun()
    return jsonify({"success": True}), 200


@v1.route("/api/v1/jobs/<job_id>/cancel", methods=["POST"])
@log_and_handle_exceptions
@jwt_required
@check_job_permission
def cancel(job_id):
    job_manager = JobManager(job_id)
    job_manager.cancel()
    return jsonify({"success": True}), 200


@v1.route("/api/v1/jobs/<job_id>", methods=["GET"])
@log_and_handle_exceptions
@jwt_required
@check_job_permission
def get(job_id):
    job_manager = JobManager(job_id)
    job_details = job_manager.get_job_details()
    return jsonify({"success": True, "job": job_details}), 200


@v1.route("/api/v1/jobs", methods=["GET"])
@log_and_handle_exceptions
@jwt_required
def get_all():
    user_name = g.validated_user["name"]
    args = request.args
    status = args.get("status")
    if status is not None:
        status = Status.validate(status)
    hours = args.get("hours")
    if hours is not None:
        hours = int(hours)
        if hours < 1:
            raise ValueError("hours must be a positive integer")
    limit = args.get("limit", "10")
    if limit is not None:
        limit = int(limit)
        if limit < 1:
            raise ValueError("limit must be a positive integer")
    job_manager = JobManager("")
    jobs = job_manager.get_jobs(user_name=user_name, status=status, hours=hours, limit=limit)
    return jsonify({"success": True, "jobs": jobs}), 200


@v1.route("/api/v1/tasks/<job_id>/<task_name>", methods=["PATCH"])
@log_and_handle_exceptions
@jwt_required
@is_node
def update_task(job_id, task_name):
    params = request.json
    task_status = params["task_status"]
    job_context = params.get("job_context")
    errors = params.get("errors")
    job_manager = JobManager(job_id)
    job_manager.update_task(task_name=task_name, task_status=task_status, external_context=job_context, errors=errors)
    return jsonify({"success": True}), 200
