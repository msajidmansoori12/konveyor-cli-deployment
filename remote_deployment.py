import logging

from utils.images import remove_old_images, generate_images_list, pull_tag_images
from utils.utils import connect_ssh, run_command_ssh, read_file


def run_remote_deployment(data):
    version = data["version"]
    build = data["build"]
    image_output_file = data["args_image_output_file"]
    arg_dependency_file = data["args_dependency_file"]
    ip_address = data["args_ip_address"]

    client = connect_ssh(ip_address)
    remove_old_images(version, client)

    if not image_output_file:
        logging.info(f"Generating images list for {version}-{build}")
        image_list = generate_images_list(version, build)
    else:
        logging.info(f"Using images list provided as CLI argument: {image_output_file}")
        image_list = read_file(image_output_file)
    pull_tag_images(version, image_list, client)


    # run_command_ssh(client, "uname -a")
    client.close()