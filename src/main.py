import argparse
import json
import os
import sys

import supervisely as sly
from dataset_tools import ProjectRepo
from dotenv import load_dotenv

import src.settings as s
from src.convert import convert_and_upload_supervisely_project

# Create instance of supervisely API object.
load_dotenv(os.path.expanduser("~/ninja.env"))
current_path = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(current_path)
load_dotenv(os.path.join(parent_path, "local.env"))
api = sly.Api.from_env()
team_id = sly.env.team_id()
workspace_id = sly.env.workspace_id()
server_address = os.getenv("SERVER_ADDRESS")
sly.logger.info(
    f"Connected to Supervisely. Server address: {server_address}, team_id: {team_id}, workspace_id: {workspace_id}."
)

# Create directories for result stats and visualizations and check if all fields in settings.py are filled.
sly.fs.mkdir("./stats")
sly.fs.mkdir("./visualizations")
s.check_names()

# Trying to retreive project info from instance by name.
project_info = api.project.get_info_by_name(workspace_id, s.PROJECT_NAME)
if not project_info:
    # If project doesn't found on instance, create it and use new project info.
    project_info = convert_and_upload_supervisely_project(api, workspace_id, s.PROJECT_NAME)
    sly.logger.info(f"Project {s.PROJECT_NAME} not found on instance. Created new project.")
    sly.logger.info("Now you can explore created project and choose 'preview_image_id'.")
    sys.exit(0)
else:
    sly.logger.info(f"Found project {s.PROJECT_NAME} on instance, will use it.")

# Preparing project settings.
project_id = project_info.id
settings = s.get_settings()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload dataset to instance.")
    parser.add_argument(
        "--forces", type=json.loads, default="{}", help="Which parameters to force."
    )

    args = parser.parse_args()
    forces = args.forces

    sly.logger.info(f"Script is starting with forces: {forces}")

    force_stats = forces.get("force_stats")
    force_visuals = forces.get("force_visuals")
    force_texts = forces.get("force_texts")

    project_repo = ProjectRepo(api, project_id, settings)
    project_repo.build_stats(force=force_stats)
    project_repo.build_visualizations(force=force_visuals)
    project_repo.build_texts(force=force_texts)

    sly.logger.info("Script finished.")
