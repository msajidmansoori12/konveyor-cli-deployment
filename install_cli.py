import argparse
import json

from config import set_config
from utils import generate_zip, remove_old_images, validate_config, pull_tag_images, generate_images_list, unpack_zip, \
    get_zip_name, get_zip_folder_name

# version="7.2.0"
# build="35"
# misc_downstream_path="/home/igor/github.com/misc-downstream/"
# extract_binary="mta-cli-binary-extract.py "
# get_images_output="get-image-build-details.py "
# bundle = "--bundle mta-operator-bundle-container-"
# no_brew = " --no-brew"


CONFIG_FILE = "config.json"

def load_config():
    """Loads config from JSON-file."""
    with open(CONFIG_FILE, "r") as f:
        configuration = json.load(f)
    set_config(configuration)

#TODO: Create parameters file to use login/password or login/ssh key's path. Make key priority if both are present
#TODO: IP should be accepted as CLI argument
#TODO: if IP is missing same code should be performed locally, if present - remotely.

if __name__ == "__main__":
    load_config()
    validate_config()

    parser = argparse.ArgumentParser(
        description="Deploys and prepares MTA CLI either locally or remotely.")
    parser.add_argument('--mta_version', required=True, help="The MTA version to use.")
    parser.add_argument('--build', required=True, help="Build number to use")
    args = parser.parse_args()

    VERSION = args.mta_version
    BUILD = args.build

    print(f"MTA Version: {VERSION}")

    # Performing main action
    remove_old_images(VERSION)
    image_list = generate_images_list(VERSION, BUILD)
    pull_tag_images(VERSION, image_list)
    generate_zip(VERSION, BUILD)
    zip_folder_name = get_zip_folder_name(image_list)
    unpack_zip(zip_folder_name)

