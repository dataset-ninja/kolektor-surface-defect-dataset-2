import json
import os
import sys

import dataset_tools as dtools
import supervisely as sly
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
os.makedirs("./stats/", exist_ok=True)
os.makedirs("./visualizations/", exist_ok=True)
s.check_before_upload()

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

project_id = project_info.id

# How the app will work: from instance or from local directory and check if all fields in settings.py are filled.
from_instance = True  # ToDo: Automatically detect if app is running from instance or locally.
s.check_after_upload()

# * Step 1: Read project and project meta
# ? Option 1: From supervisely instance

if from_instance:
    sly.logger.info("The app in the instance mode. Will download data from Supervisely.")

    project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))

    if s.CLASS2COLOR:
        sly.logger.info("Classes colors are specified in settings.py. Will update project meta.")

        items = []
        for obj_class in project_meta.obj_classes.items():
            if obj_class.name in s.CLASS2COLOR:
                items.append(obj_class.clone(color=s.CLASS2COLOR[obj_class.name]))
            else:
                items.append(obj_class)
        project_meta = sly.ProjectMeta(obj_classes=items)
        api.project.update_meta(project_id, project_meta)

        sly.logger.info("Successfully changed classes colors and updated project meta.")

    datasets = api.dataset.get_list(project_id)

    sly.logger.info(
        f"Prepared project meta and read {len(datasets)} datasets for project with id={project_id}."
    )

# ? Option 2: From local directory (! Not implemented yet)
# project_path = os.environ["LOCAL_DATA_DIR"]
# sly.download(api, project_id, project_path, save_image_info=True, save_images=False)
# project_meta = sly.Project(project_path, sly.OpenMode.READ).meta
# datasets = None

# * Step 2: Get download link
download_sly_url = dtools.prepare_download_link(project_info)
dtools.update_sly_url_dict(
    {
        s.PROJECT_NAME: {
            "id": project_id,
            "download_sly_url": download_sly_url,
            "download_original_url": s.DOWNLOAD_ORIGINAL_URL,
        }
    }
)
sly.logger.info(f"Prepared download link: {download_sly_url}")


# * Step 3: Update project custom data
sly.logger.info("Updating project custom data...")
custom_data = {
    #####################
    # ! required fields #
    #####################
    "name": s.PROJECT_NAME,
    "fullname": s.PROJECT_NAME_FULL,
    "cv_tasks": s.CV_TASKS,
    "annotation_types": s.ANNOTATION_TYPES,
    "industries": s.INDUSTRIES,
    "release_year": s.RELEASE_YEAR,
    "homepage_url": s.HOMEPAGE_URL,
    "license": s.LICENSE,
    "license_url": s.LICENSE_URLS[s.LICENSE],
    "preview_image_id": s.PREVIEW_IMAGE_ID,
    "github_url": s.GITHUB_URL,
    "github": s.GITHUB_URL[s.GITHUB_URL.index("dataset-ninja") :],
    "download_sly_url": download_sly_url,
    #####################
    # ? optional fields #
    #####################
    "download_original_url": s.DOWNLOAD_ORIGINAL_URL,
    # "paper": # Union[None, str],
    # "citation_url": None,
    # "organization_name": # Union[None, str, list],
    # "organization_url": # Union[None, str, list],
    # "tags": [],
}

# * Update custom data and retrieve updated project info and custom data from instance.
api.project.update_custom_data(project_id, custom_data)
project_info = api.project.get_info_by_id(project_id)
custom_data = project_info.custom_data
sly.logger.info("Successfully updated project custom data.")


def build_stats():
    sly.logger.info("Starting to build stats...")

    stats = [
        dtools.ClassBalance(project_meta),
        dtools.ClassCooccurrence(project_meta, force=False),
        dtools.ClassesPerImage(project_meta, datasets),
        dtools.ObjectsDistribution(project_meta),
        dtools.ObjectSizes(project_meta),
        dtools.ClassSizes(project_meta),
    ]
    heatmaps = dtools.ClassesHeatmaps(project_meta)
    classes_previews = dtools.ClassesPreview(project_meta, project_info.name, force=False)
    previews = dtools.Previews(project_id, project_meta, api, team_id)

    for stat in stats:
        if not sly.fs.file_exists(f"./stats/{stat.basename_stem}.json"):
            stat.force = True
        if (
            isinstance(stat, dtools.ClassCooccurrence)
            and len(project_meta.obj_classes.items()) == 1
        ):
            stat.force = False
    stats = [stat for stat in stats if stat.force]

    if not sly.fs.file_exists(f"./stats/{heatmaps.basename_stem}.png"):
        heatmaps.force = True
    if not sly.fs.file_exists(f"./visualizations/{classes_previews.basename_stem}.webm"):
        classes_previews.force = True
    if not api.file.dir_exists(team_id, f"/dataset/{project_id}/renders/"):
        previews.force = True
    vstats = [stat for stat in [heatmaps, classes_previews, previews] if stat.force]

    dtools.count_stats(
        project_id,
        stats=stats + vstats,
        sample_rate=1,
    )

    sly.logger.info("Saving stats...")
    for stat in stats:
        with open(f"./stats/{stat.basename_stem}.json", "w") as f:
            json.dump(stat.to_json(), f)
        stat.to_image(f"./stats/{stat.basename_stem}.png")

    if len(vstats) > 0:
        if heatmaps.force:
            heatmaps.to_image(f"./stats/{heatmaps.basename_stem}.png", draw_style="outside_black")
        if classes_previews.force:
            classes_previews.animate(f"./visualizations/{classes_previews.basename_stem}.webm")
        if previews.force:
            previews.close()

    sly.logger.info("Successfully built and saved stats.")


def build_visualizations():
    sly.logger.info("Starting to build visualizations...")

    renderers = [
        dtools.Poster(project_id, project_meta, force=False),
        dtools.SideAnnotationsGrid(project_id, project_meta),
    ]
    animators = [
        dtools.HorizontalGrid(project_id, project_meta),
        dtools.VerticalGrid(project_id, project_meta, force=False),
    ]

    for vis in renderers + animators:
        if not sly.fs.file_exists(f"./visualizations/{vis.basename_stem}.png"):
            vis.force = True
    renderers, animators = [r for r in renderers if r.force], [a for a in animators if a.force]

    for a in animators:
        if not sly.fs.file_exists(f"./visualizations/{a.basename_stem}.webm"):
            a.force = True
    animators = [a for a in animators if a.force]

    # ? Download fonts from: https://fonts.google.com/specimen/Fira+Sans
    dtools.prepare_renders(
        project_id,
        renderers=renderers + animators,
        sample_cnt=40,
    )

    sly.logger.info("Saving visualizations...")

    for vis in renderers + animators:
        vis.to_image(f"./visualizations/{vis.basename_stem}.png")
    for a in animators:
        a.animate(f"./visualizations/{a.basename_stem}.webm")

    sly.logger.info("Successfully built and saved visualizations.")


def build_summary():
    sly.logger.info("Starting to build summary...")

    summary_data = dtools.get_summary_data_sly(project_info)

    classes_preview = None
    if sly.fs.file_exists("./visualizations/classes_preview.webm"):
        classes_preview = (
            f"{custom_data['github_url']}/raw/main/visualizations/classes_preview.webm"
        )

    summary_content = dtools.generate_summary_content(
        summary_data,
        vis_url=classes_preview,
    )

    with open("SUMMARY.md", "w") as summary_file:
        summary_file.write(summary_content)

    sly.logger.info("Successfully built and saved summary.")


def build_citation():
    sly.logger.info("Starting to build citation...")

    citation_content = s.CITATION_TEMPLATE.format(
        project_name_full=s.PROJECT_NAME_FULL,
        project_name=s.PROJECT_NAME,
        homepage_url=s.HOMEPAGE_URL,
    )

    with open("CITATION.md", "w") as citation_file:
        citation_file.write(citation_content)

    sly.logger.info("Successfully built and saved citation.")
    sly.logger.warning("You must update CITATION.md manually.")


def build_license():
    sly.logger.info("Starting to build license...")

    license_content = s.LICENSE_TEMPLATE.format(
        project_name_full=s.PROJECT_NAME_FULL,
        license_text=s.LICENSE_TEXTS[s.LICENSE],
        license_url=s.LICENSE_URLS[s.LICENSE],
    )

    with open("LICENSE.md", "w") as license_file:
        license_file.write(license_content)

    sly.logger.info("Successfully built and saved license.")


def build_readme():
    sly.logger.info("Starting to build readme...")

    readme_content = s.README_TEMPLATE.format(
        project_name_full=s.PROJECT_NAME_FULL,
        project_name=s.PROJECT_NAME,
        cv_tasks=", ".join(s.CV_TASKS),
    )

    with open("README.md", "w") as readme_file:
        readme_file.write(readme_content)

    sly.logger.info("Successfully built and saved readme.")


def main():
    pass

    build_stats()
    build_visualizations()
    build_summary()
    build_citation()
    build_license()
    build_readme()

    sly.logger.info("Script finished successfully.")
    sly.logger.warning("If needed EXPERT.md should be created and filled manually.")


if __name__ == "__main__":
    main()
