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
import logging

from flask import request, jsonify, Blueprint

from job_manager.core import JobManager
import settings
from utils.id_utils import generate_job_id

default_views = Blueprint('default_views', __name__)


@default_views.route("/")
def index_view():
    return jsonify({
        "message": f"{settings.PARTY} app server is running!",
    }), 200


@default_views.route("/job/submit", methods=["POST"])
def submit_job():
    try:
        params = request.json
        job_id = params.get("job_id", generate_job_id())
        job_manager = JobManager(job_id)
        job_manager.submit(params)

        return jsonify({"success": True, "job_id": job_id}), 200
    except Exception as e:
        logging.exception(f"submit job error: {e}")
        return jsonify({"success": False, "error_message": str(e)}), 500


@default_views.route("/job/rerun", methods=["POST"])
def rerun_job():
    try:
        params = request.json
        job_id = params["job_id"]
        job_manager = JobManager(job_id)
        job_manager.rerun()

        return jsonify({"success": True}), 200
    except Exception as e:
        logging.exception(f"submit job error: {e}")
        return jsonify({"success": False, "error_message": str(e)}), 500


@default_views.route("/job/kill", methods=["POST"])
def kill_job():
    try:
        params = request.json
        job_id = params["job_id"]
        job_manager = JobManager(job_id)
        job_manager.cancel()

        return jsonify({"success": True}), 200
    except Exception as e:
        logging.exception(f"submit job error: {e}")
        return jsonify({"success": False, "error_message": str(e)}), 500


@default_views.route("/job/status", methods=["GET"])
def get_status():
    try:
        params = request.args
        job_id = params["job_id"]
        job_manager = JobManager(job_id)
        status = job_manager.get_job_details()
        return jsonify({"success": True, "status": status}), 200
    except Exception as e:
        logging.exception(f"get job status error: {e}")
        return jsonify({"success": False, "error_message": str(e)}), 500


@default_views.route("/task/update", methods=["POST"])
def update_task():
    try:
        params = request.json
        job_id = params["job_id"]
        task_name = params["task_name"]
        task_status = params["task_status"]
        job_context = params.get("job_context")
        job_manager = JobManager(job_id)
        job_manager.update_task(task_name=task_name, task_status=task_status, external_context=job_context)
        return jsonify({"success": True})
    except Exception as e:
        logging.exception(f"update task status error: {e}")
        return jsonify({"success": False, "error_message": str(e)}), 500
