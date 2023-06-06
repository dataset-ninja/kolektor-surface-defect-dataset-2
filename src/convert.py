# https://www.vicos.si/resources/kolektorsdd2/

import os

import numpy as np
import supervisely as sly
from cv2 import connectedComponents
from supervisely.io.fs import dir_exists, file_exists, get_file_ext, get_file_name
from tqdm import tqdm


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    dataset_path = "/Users/iwatkot/Downloads/ninja-datasets/KolektorSDD2"
    batch_size = 200
    mask_suffix = "_GT"
    # train_images_folder = "train"
    # test_images_folder = "test"

    def create_ann(image_path):
        labels = []

        mask_name = get_file_name(image_path) + mask_suffix + get_file_ext(image_path)
        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]
        mask_path = os.path.join(ds_path, mask_name)
        if file_exists(mask_path):
            mask_np = sly.imaging.image.read(mask_path)[:, :, 0]
            if len(np.unique(mask_np)) != 1:
                mask = mask_np == 255
                ret, curr_mask = connectedComponents(mask.astype("uint8"), connectivity=8)
                for i in range(1, ret):
                    obj_mask = curr_mask == i
                    curr_bitmap = sly.Bitmap(obj_mask)
                    curr_label = sly.Label(curr_bitmap, obj_class)
                    labels.append(curr_label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels)

    all_datasets = os.listdir(dataset_path)

    obj_class = sly.ObjClass("defect", sly.Bitmap)
    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(obj_classes=[obj_class])
    api.project.update_meta(project.id, meta.to_json())

    for curr_dataset in all_datasets:
        ds_path = os.path.join(dataset_path, curr_dataset)
        if dir_exists(ds_path):
            dataset = api.dataset.create(project.id, curr_dataset, change_name_if_conflict=True)

            items_names = os.listdir(ds_path)
            images_names = [item_name for item_name in items_names if mask_suffix not in item_name]

            progress = tqdm(total=len(images_names), desc="Create dataset {}".format(curr_dataset))

            for img_names_batch in sly.batched(images_names, batch_size=batch_size):
                images_pathes_batch = [
                    os.path.join(ds_path, image_name) for image_name in img_names_batch
                ]
                img_infos = api.image.upload_paths(dataset.id, img_names_batch, images_pathes_batch)
                img_ids = [im_info.id for im_info in img_infos]
                anns_batch = [create_ann(image_path) for image_path in images_pathes_batch]
                api.annotation.upload_anns(img_ids, anns_batch)

                progress.update(len(img_names_batch))

    return project
