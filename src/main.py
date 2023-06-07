import json
import os

import dataset_tools as dtools
import supervisely as sly
from dotenv import load_dotenv

from src.convert import convert_and_upload_supervisely_project

# * Names of the project that will appear on instance and on Ninja webpage.
PROJECT_NAME = "Kolektor Surface-Defect"
PROJECT_NAME_FULL = "Kolektor Surface-Defect Dataset 2"

load_dotenv(os.path.expanduser("~/ninja.env"))
load_dotenv("local.env")
api = sly.Api.from_env()
team_id = sly.env.team_id()
workspace_id = sly.env.workspace_id()

os.makedirs("./stats/", exist_ok=True)
os.makedirs("./visualizations/", exist_ok=True)

# * Trying to retreive project info from instance by name.
project_info = api.project.get_info_by_name(workspace_id, PROJECT_NAME)
if not project_info:
    # * If project doesn't found on instance, create it and use new project info.
    project_info = convert_and_upload_supervisely_project(api, workspace_id, PROJECT_NAME)

project_id = project_info.id

# 1a initialize sly api way
# project_id = sly.env.project_id()
project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))
datasets = api.dataset.get_list(project_id)


# 1b initialize sly localdir way
# project_path = os.environ["LOCAL_DATA_DIR"]
# sly.download(api, project_id, project_path, save_image_info=True, save_images=False)
# project_meta = sly.Project(project_path, sly.OpenMode.READ).meta
# datasets = None

# custom_data = project_info.custom_data


# 2. get download link
download_sly_url = dtools.prepare_download_link(project_info)
dtools.update_sly_url_dict({project_id: download_sly_url})


# 3. upload custom data

custom_data = {
    # required fields
    "name": PROJECT_NAME,
    "fullname": PROJECT_NAME_FULL,
    "cv_tasks": ["semantic segmentation"],
    "annotation_types": ["semantic segmentation"],
    "industries": ["general domain"],  # ! Not sure
    "release_year": 2021,
    "homepage_url": "https://www.vicos.si/resources/kolektorsdd2/",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/legalcode/",
    "preview_image_id": 222859,
    "github_url": None,  # ! Doesn't have github page
    "citation_url": "https://prints.vicos.si/publications/385",
    "download_sly_url": download_sly_url,
    # optional fields
    "download_original_url": "https://go.vicos.si/kolektorsdd2",
    # "paper": None,
    # "organization_name": None,
    # "organization_url": None,
    # "tags": [],
    "github": "dataset-ninja/kolektor-surface-defect-dataset-2",
}
api.project.update_custom_data(project_id, custom_data)


project_info = api.project.get_info_by_id(project_id)
custom_data = project_info.custom_data


def build_stats():
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

    print("Saving stats...")
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

    print("Stats done")


def build_visualizations():
    renderers = [
        dtools.Poster(project_id, project_meta, force=False),
        dtools.SideAnnotationsGrid(project_id, project_meta),  # ! Return after bug fix
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

    # Download fonts from https://fonts.google.com/specimen/Fira+Sans
    dtools.prepare_renders(
        project_id,
        renderers=renderers + animators,
        sample_cnt=40,
    )
    print("Saving visualization results...")
    for vis in renderers + animators:
        vis.to_image(f"./visualizations/{vis.basename_stem}.png")
    for a in animators:
        a.animate(f"./visualizations/{a.basename_stem}.webm")
    print("Visualizations done")


def build_summary():
    print("Building summary...")
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
    print("Done.")


def main():
    pass
    build_stats()
    build_visualizations()
    build_summary()


if __name__ == "__main__":
    main()
