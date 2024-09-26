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
import json

import click
from dotenv import load_dotenv, set_key

from client.client import PlatformClient

load_dotenv()


@click.group()
@click.pass_context
def cli(ctx):
    server_url = os.getenv("SERVER_URL", None)
    jwt_token = os.getenv("JWT_TOKEN", None)
    if ctx.invoked_subcommand != "init":
        if not server_url or not jwt_token:
            click.echo("Server URL or JWT token not set. Please run the 'init' command to set them.")
            ctx.exit()
        else:
            ctx.ensure_object(dict)
            ctx.obj["client"] = PlatformClient(server_url, jwt_token)


@cli.command(help="Initialize server_url and jwt_token")
@click.option("--server-url", prompt="Please enter server url", help="Server URL.")
@click.option("--jwt-token", prompt="Please enter jwt token", help="Client validation token.")
@click.pass_context
def init(ctx, server_url, jwt_token):
    # Save the values to .env file
    set_key(".env", "SERVER_URL", server_url)
    set_key(".env", "JWT_TOKEN", jwt_token)
    click.echo("Server URL and JWT token have been set.")

    ctx.ensure_object(dict)
    ctx.obj["client"] = PlatformClient(server_url, jwt_token)


@cli.command(help="submit a new job")
@click.option("--json-file", type=click.Path(exists=True), default=None, help="path to a json file")
@click.option("--json-string", type=str, default=None, help="parameters as a json string")
@click.pass_context
def submit(ctx, json_file, json_string):
    client = ctx.obj["client"]
    if json_file is not None:
        try:
            with open(json_file, "r") as f:
                params = json.load(f)
        except Exception as e:
            raise click.UsageError(f"not a valid json format file: {e}")
    elif json_string is not None:
        try:
            params = json.loads(json_string)
        except Exception as e:
            raise click.UsageError(f"not a valid json format string: {e}")
    else:
        raise click.UsageError("you must provide either --json-file or --json-string.")

    success = client.submit(params)
    click.echo(success)


@cli.command(help="cancel a running job")
@click.argument("job-id")
@click.pass_context
def cancel(ctx, job_id):
    client = ctx.obj["client"]
    success = client.cancel(job_id)
    click.echo(success)


@cli.command(help="rerun a failed/canceled job")
@click.argument("job-id")
@click.pass_context
def rerun(ctx, job_id):
    client = ctx.obj["client"]
    success = client.rerun(job_id)
    click.echo(success)


@cli.command(help="get job info")
@click.argument("job-id")
@click.pass_context
def get_job(ctx, job_id):
    client = ctx.obj["client"]
    job = client.get(job_id)
    click.echo(job)


@cli.command(help="list a limited number of jobs submitted in the past hours with given status")
@click.option(
    "--status",
    type=str,
    default=None,
    help="only jobs with the given status will be shown, accept values e.g. [RUNNING, SUCCESS, FAILED, CANCELED]")
@click.option("--hours", type=int, default=24, help="only the jobs submitted within the past given hours will be shown")
@click.option("--limit", type=int, default=10, help="only show jobs within the given limit")
@click.pass_context
def get_jobs(ctx, status, hours, limit):
    client = ctx.obj["client"]
    response = client.get_all(status, hours, limit)
    click.echo(response)


if __name__ == "__main__":
    cli(obj={})
