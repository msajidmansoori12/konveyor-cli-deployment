import os

import config
from utils.images import remove_old_images, generate_images_list, pull_tag_images
from utils.utils import read_file, get_home_dir
from utils.zip import generate_zip, get_zip_folder_name, get_zip_name, unpack_zip


def run_local_deployment(data):
    version = data["version"]
    build = data["build"]
    image_output_file = data["args_image_output_file"]
    arg_dependency_file = data["args_dependency_file"]
    print(f"Deploying MTA Version: {version}-{build}")
    remove_old_images(version)
    if not image_output_file:
        image_list = generate_images_list(version, build)
    else:
        image_list = read_file(image_output_file)
    pull_tag_images(version, image_list)
    if not arg_dependency_file:
        generate_zip(version, build)
        zip_folder_name = get_zip_folder_name(image_list)
        zip_name = get_zip_name(zip_folder_name.split("-")[1])
        full_zip_name = os.path.join(config.MISC_DOWNSTREAM_PATH, zip_folder_name, zip_name)
        print (full_zip_name)
    else:
        full_zip_name=arg_dependency_file
        print (full_zip_name)
    target_path = get_home_dir()
    unpack_zip(full_zip_name, target_path)