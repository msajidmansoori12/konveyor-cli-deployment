import os
import shutil
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

def run_command(command, fail_on_failure=True):
    """
    Runs command in terminal
    :param command: Command that will be performed
    :param fail_on_failure: flag if run should be terminated on failure or not
    :return: output of command performed
    """
    try:
        logging.info(f"Executing command: {command}")
        return subprocess.run(command, shell=True, check=fail_on_failure, stdout=subprocess.PIPE, encoding='utf-8')
    except Exception as err:
        logging.error(f"Command failed: {err}")
        raise SystemExit("There was an issue running a command: {}".format(err))

def read_file(output_file):
    """
    Opens a file for reading
    :param output_file:
    :return: opened file's content
    """
    try:
        with open(output_file, 'r') as file:
            return file.read()
    except Exception as err:
        raise SystemExit(f"There was an error opening file: {err}")

def convert_to_json(file):
    """
    Converts incoming string to JSON format
    :param file: String to be converted
    :return: JSON
    """
    try:
        return json.loads(file)
    except Exception as err:
        raise SystemExit(f"There was an error converting string to JSON format: {err}")

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
    except subprocess.CalledProcessError as e:
        print(f"Error while performing command: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def generate_images_list(version, build):
    """
    Generates list of images and pulls them
    :param version: MTA version, for example 7.2.0
    :param build: build number
    :return: String containing list of images. Can be converted to JSON after that.
    """
    get_images_output_command = f"cd {config.MISC_DOWNSTREAM_PATH}; ./{config.GET_IMAGES_OUTPUT}{config.BUNDLE}{version}-{build} | grep -vi error"
    return run_command(get_images_output_command).stdout

def connect_ssh(ip_address, command):
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

def get_home_dir():
    """
    Gets home folder path of the user script is running from
    :return: String contains folder name
    """
    home_dir = os.path.expanduser("~")  # Getting home dir
    return os.path.join(home_dir, ".kantra")

def clear_folder (path):
    """
    Clears folder by removing it with all content and creating it again
    :param path: Path of the folder to be cleared
    """
    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path, exist_ok=True)
