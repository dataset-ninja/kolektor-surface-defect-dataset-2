import os
import sys

import supervisely as sly
from dataset_tools import ProjectRepo
from dotenv import load_dotenv

import src.settings as s
from src.convert import convert_and_upload_supervisely_project

# Create instance of supervisely API object.
load_dotenv(os.path.expanduser("~/ninja.env"))
load_dotenv("local.env")
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

# Creating stats, visualizations and texts for project.
project_repo = ProjectRepo(api, project_id, settings)
project_repo.build_stats()
project_repo.build_visualizations()
project_repo.build_texts()
