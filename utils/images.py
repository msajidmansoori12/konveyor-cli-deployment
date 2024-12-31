import logging
import subprocess

import config
from utils.utils import run_command, convert_to_json


def pull_tag_images(mta_version, output_file):
    """
    Pulls and tags images from the list it gets
    :param mta_version: MTA version to be deployed
    :param output_file: Output with list of images to be pulled. Can be generated and forwarded here or provided as CLI parameter
    """
    related_images = convert_to_json(output_file).get('related_images_pullspecs', None)
    if related_images:  # If related images are present then proceed
        keywords = ['java', 'generic', 'dotnet', 'cli']
        for image in related_images:
            if any(keyword in image for keyword in keywords):  # Check if the image contains any of the keywords.
                logging.info(f"Image : {image}")
                # Pull image from registry-proxy.engineer.redhat.com
                proxy_image_url = 'registry-proxy.engineering.redhat.com/rh-osbs/mta-{}'.format(image.split('/')[-1])
                pull_command = f'podman pull {proxy_image_url} --tls-verify=false'
                logging.info(f'Pulling image: {proxy_image_url}')
                run_command(pull_command)
                logging.info('Pull successful')
                tag_image = image.split('@sha')[-2]
                logging.info(f'Tagging image {proxy_image_url} to {tag_image}:{mta_version}')
                tag_command = f'podman tag {proxy_image_url} {tag_image}:{mta_version}'  #Tag image to correct version
                run_command(tag_command)
                logging.info(f'Tagging {image} is completed...')

def remove_old_images(version):
    """
    Removes old images before pulling new
    :param version: MTA version to be cleaned up
    """
    try:
        result = run_command("podman images")

        # Filtering lines that contain "registry" and version
        images = []
        for line in result.stdout.splitlines():
            columns = line.split()
            if "registry" in line and version in line:
                # Third column -  IMAGE ID
                if len(columns) >= 3:
                    images.append(columns[2])

        # Deleting images gotten after filtering
        for image in images:
            run_command(f"podman rmi {image} --force", False)
            logging.info(f"Image {image} was removed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error while performing command: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

def generate_images_list(version, build):
    """
    Generates list of images and pulls them
    :param version: MTA version, for example 7.2.0
    :param build: build number
    :return: String containing list of images. Can be converted to JSON after that.
    """
    get_images_output_command = f"cd {config.MISC_DOWNSTREAM_PATH}; ./{config.GET_IMAGES_OUTPUT}{config.BUNDLE}{version}-{build} | grep -vi error"
    return run_command(get_images_output_command).stdout