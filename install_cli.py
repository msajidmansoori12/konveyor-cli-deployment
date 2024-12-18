import json

from config import set_config, VERSION
from utils import generate_zip, clean_images, validate_config, pull_tag_images, generate_images_list

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

    # Performing main action
    clean_images()
    generate_zip()
    image_list = generate_images_list()
    pull_tag_images(VERSION, image_list)

    # clean_images_command = "for image in $(podman images|grep registry|grep " + version + "|awk '{print $3}'); do podman rmi $image --force; done"
    # print (clean_images_command)
    # run_command(clean_images_command)
    #
    # # Generating zip file to be used with container-less CLI
    # extract_binary_command = misc_downstream_path + extract_binary + bundle + version + "-" + build + no_brew
    # print (extract_binary_command)
    # run_command(extract_binary_command)
    #
    # # Generate list of images and pulling images to docker
    # get_images_output_command = "cd " + misc_downstream_path + "; ./" +get_images_output + bundle + version + "-" + build + "|grep -vi error"
    # print (get_images_output_command)
    # result = run_command(get_images_output_command).stdout
    # pull_images(version, result)
