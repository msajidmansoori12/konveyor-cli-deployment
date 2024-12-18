import os
import platform
import shutil
import subprocess
import json
import sys
import zipfile
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

def remove_old_images(version):
    """Removes old images before pulling new"""
    clean_images_command = f"for image in $(podman images|grep registry|grep {version}|awk '{{print $3}}'); do podman rmi $image --force; done"
    # print(clean_images_command)
    run_command(clean_images_command)

def generate_zip(version, build):
    """Generates zip with dependencies for local run"""
    extract_binary_command = f"{config.MISC_DOWNSTREAM_PATH}{config.EXTRACT_BINARY} {config.BUNDLE}{version}-{build} {config.NO_BREW}"
    run_command(extract_binary_command)

def generate_images_list(version, build):
    """Generates list of images and pulls them"""
    get_images_output_command = f"cd {config.MISC_DOWNSTREAM_PATH}; ./{config.GET_IMAGES_OUTPUT}{config.BUNDLE}{version}-{build} | grep -vi error"
    return run_command(get_images_output_command).stdout

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
        "MISC_DOWNSTREAM_PATH": config.MISC_DOWNSTREAM_PATH,
        "EXTRACT_BINARY": config.EXTRACT_BINARY,
        "GET_IMAGES_OUTPUT": config.GET_IMAGES_OUTPUT,
        "BUNDLE": config.BUNDLE,
        "NO_BREW": config.NO_BREW
    }

    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise SystemExit(f"Missing required configuration values: {', '.join(missing_vars)}")


def get_zip_folder_name(image_list):
    if isinstance(image_list, str):
        image_list = json.loads(image_list)

    for item in image_list["related_images"]:
        for key, value in item.items():
            if "mta-cli-rhel9" in key:
                _, major, minor = value["nvr"].rsplit("-", 2)
                return f"MTA-{major}-{minor}"

def get_zip_name(version):
    os_name = platform.system().lower()
    machine = platform.machine().lower()

    if "aarch64" in machine or "arm64" in machine:
        machine = "arm64"
    elif "x86_64" in machine or "amd64" in machine:
        machine = "amd64"
    else:
        machine = "unknown"

    return f"mta-{version}-cli-{os_name}-{machine}.zip"

def unpack_zip(zip_folder_name):
    # Finding full path where to unpack
    home_dir = os.path.expanduser("~")  # Getting home dir
    target_path = os.path.join(home_dir, ".kantra")
    zip_name = get_zip_name(zip_folder_name.split("-")[1])

    # Cleanup if .kantra exists
    if os.path.exists(target_path):
        shutil.rmtree(target_path)

    os.makedirs(target_path, exist_ok=True)

    # Concatenating full path
    zip_full_path = os.path.join(config.MISC_DOWNSTREAM_PATH, zip_folder_name, zip_name)
    print (zip_full_path)

    # Unpacking zip file
    with zipfile.ZipFile(zip_full_path, "r") as zip_ref:
        zip_ref.extractall(target_path)

    print(f"Zip {zip_name} unpacked successfully в {target_path}")