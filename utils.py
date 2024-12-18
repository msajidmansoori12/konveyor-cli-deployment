import subprocess
import json
import sys

import paramiko
import logging
import config


# Function to run a shell command
# def run_command(command):
#     process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     stdout, stderr = process.communicate()
#     if process.returncode != 0:
#         raise Exception(f"Command failed with error: {stderr.decode('utf-8')}")
#     return stdout.decode('utf-8')

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers = [
        logging.StreamHandler(sys.stdout)  # Redirecting to stdout
    ]
)

def run_command(command):
    try:
        logging.info(f"Executing command: {command}")
        return subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, encoding='utf-8')
    except Exception as err:
        logging.error(f"Command failed: {err}")
        raise SystemExit("There was an issue running a command: {}".format(err))

def read_output_file(output_file):
    with open(output_file, 'r') as file:
        file_content = file.read()
    data_dict = json.loads(file_content)
    return data_dict


def pull_tag_images(mta_version, output_file):
    """Pulls and tags images from the list it gets"""
    # TODO: Add try/catch to json.load here
    related_images = json.loads(output_file).get('related_images_pullspecs', None)
    if related_images:  # If related images are present then proceed
        keywords = ['java', 'generic', 'dotnet', 'cli']
        for image in related_images:
            if any(keyword in image for keyword in keywords):  # Check if the image contains any of the keywords.
                print(f"Image : {image}")
                # Pull image from registry-proxy.engineer.redhat.com
                proxy_image_url = 'registry-proxy.engineering.redhat.com/rh-osbs/mta-{}'.format(image.split('/')[-1])
                pull_command = f'podman pull {proxy_image_url} --tls-verify=false'
                print(f'Pulling image: {proxy_image_url}')
                run_command(pull_command)
                print('Pull successful')
                tag_image = image.split('@sha')[-2]
                print(f'Tagging image {proxy_image_url} to {tag_image}:{mta_version}')
                tag_command = f'podman tag {proxy_image_url} {tag_image}:{mta_version}'  #Tag image to correct version
                run_command(tag_command)
                print('Tagging complete...')

def clean_images():
    """Removes old images before pulling new"""
    clean_images_command = f"for image in $(podman images|grep registry|grep {config.VERSION}|awk '{{print $3}}'); do podman rmi $image --force; done"
    # print(clean_images_command)
    run_command(clean_images_command)

def generate_zip():
    """Generates zip with dependencies for local run"""
    extract_binary_command = f"{config.MISC_DOWNSTREAM_PATH}{config.EXTRACT_BINARY} {config.BUNDLE}{config.VERSION}-{config.BUILD} {config.NO_BREW}"
    run_command(extract_binary_command)

def generate_images_list():
    """Generates list of images and pulls them"""
    get_images_output_command = f"cd {config.MISC_DOWNSTREAM_PATH}; ./{config.GET_IMAGES_OUTPUT}{config.BUNDLE}{config.VERSION}-{config.BUILD} | grep -vi error"
    return run_command(get_images_output_command).stdout
    # pull_images(config.VERSION, result)

# def main():
#     parser = argparse.ArgumentParser(
#         description="Process podman images and download zip files based on repository type.")
#     parser.add_argument('--mta_version', required=True, help="The MTA version to use.")
#     parser.add_argument('--image_output_file', required=True,
#                         help='The file containing related_images for bundle, generated using get-image-build-details.py')
#     args = parser.parse_args()
#
#     mta_version = args.mta_version
#
#     print(f"MTA Version: {mta_version}")
#
#     pull_images(args.mta_version, args.image_output_file)
#

def connect_ssh(ip_address, command):
    # SSH_HOST = 'host.example.com'
    # SSH_USER = 'admin_user'
    # SSH_KEY = '/home/user/.ssh/id_rsa'
    # SSH_PASSWORD = ''

    SSH_HOST = ip_address
    SSH_USER = 'igor'
    SSH_KEY = None
    try:
        with paramiko.SSHClient() as client:
            client.load_system_host_keys()
            client.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY)
            _stdin, stdout, _stderr = client.exec_command(command)
            for line in iter(lambda: stdout.readline(2048).rstrip(), ""):
                print(line)
            stderr = _stderr.read()
            if len(stderr) > 0:
                raise SystemExit(stderr)
    except Exception as err:
        raise SystemExit("There was an issue with ssh command: {}".format(err))

def validate_config():
    """Ensures that required configuration variables are set."""
    required_vars = {
        "VERSION": config.VERSION,
        "BUILD": config.BUILD,
        "MISC_DOWNSTREAM_PATH": config.MISC_DOWNSTREAM_PATH,
        "EXTRACT_BINARY": config.EXTRACT_BINARY,
        "GET_IMAGES_OUTPUT": config.GET_IMAGES_OUTPUT,
        "BUNDLE": config.BUNDLE,
        "NO_BREW": config.NO_BREW
    }

    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise SystemExit(f"Missing required configuration values: {', '.join(missing_vars)}")
