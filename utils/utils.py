import os
import random
import shutil
import string
import subprocess
import json
import sys
import paramiko
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers = [
        logging.StreamHandler(sys.stdout)  # Redirecting to stdout
    ]
)

# def run_command(command, fail_on_failure=True, client=None):
#     """
#     Runs command either locally or on a remote machine via SSH
#     :param command: Command that will be performed
#     :param fail_on_failure: Flag if run should be terminated on failure or not
#     :param client: Paramiko SSH client (optional)
#     :return: output of command performed
#     """
#     try:
#         if client:
#             logging.info(f"Executing remote command: {command}")
#             # Remote execution via SSH
#             _stdin, stdout, _stderr = client.exec_command(command)
#             stdout_result = stdout.read().decode('utf-8')
#             stderr_result = _stderr.read().decode('utf-8')
#
#             if stderr_result and fail_on_failure:
#                 raise Exception(stderr_result)
#
#             return stdout_result
#         else:
#             # Local execution
#             logging.info(f"Executing command: {command}")
#             result = subprocess.run(command, shell=True, check=fail_on_failure, stdout=subprocess.PIPE, encoding='utf-8')
#             return result.stdout
#     except subprocess.CalledProcessError as err:
#         logging.error(f"Local command failed: {err}")
#         if fail_on_failure:
#             raise SystemExit("There was an issue running a command: {}".format(err))
#     except Exception as err:
#         logging.error(f"Remote command failed: {err}")
#         if fail_on_failure:
#             raise SystemExit("There was an issue running a command: {}".format(err))

def run_command(command, fail_on_failure=True, client=None):
    """
    Runs command either locally or on a remote machine via SSH
    :param command: Command that will be performed
    :param fail_on_failure: Flag if run should be terminated on failure or not
    :param client: Paramiko SSH client (optional)
    :return: output of command performed
    """
    try:
        logging.info(f"Executing command: {command}")
        if client:
            # Remote execution via SSH
            _stdin, stdout, _stderr = client.exec_command(command)
            stdout_result = stdout.read().decode('utf-8')
            stderr_result = _stderr.read().decode('utf-8')

            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0 and fail_on_failure:
                raise Exception(stderr_result)

            # Return both stdout and stderr to handle non-critical messages
            return stdout_result, stderr_result
        else:
            # Local execution
            result = subprocess.run(command, shell=True, check=fail_on_failure, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
            if result.returncode != 0 and fail_on_failure:
                raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)

            # Return both stdout and stderr to handle non-critical messages
            return result.stdout, result.stderr
    except subprocess.CalledProcessError as err:
        logging.error(f"Local command failed: {err}")
        if fail_on_failure:
            raise SystemExit("There was an issue running a command: {}".format(err))
    except Exception as err:
        logging.error(f"Remote command failed: {err}")
        if fail_on_failure:
            raise SystemExit("There was an issue running a command: {}".format(err))

def read_file(output_file):
    """
    Opens a file for reading
    :param output_file:
    :return: opened file's content
    """
    try:
        with open(output_file, 'r') as file:
            logging.info(f"File opened successfully: {output_file}")
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
        json_file = json.loads(file)
        logging.info("String was converted to JSON successfully!")
        return json_file
    except Exception as err:
        raise SystemExit(f"There was an error converting string to JSON format: {err}")

def connect_ssh(ip_address):
    SSH_HOST = ip_address
    SSH_USER = 'igor'
    SSH_KEY = None
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, username=SSH_USER, key_filename=SSH_KEY)
        return client
    except Exception as err:
        client.close()
        raise SystemExit("There was an issue connecting to host by ssh: {}".format(err))

def run_command_ssh(client, command):
    try:
        _stdin, stdout, _stderr = client.exec_command(command)
        for line in iter(lambda: stdout.readline(2048).rstrip(), ""):
            print(line)
        stderr = _stderr.read()
        if len(stderr) > 0:
            raise SystemExit(stderr)
    except Exception as err:
        raise SystemExit("There was an issue with ssh command: {}".format(err))


def get_target_dependency_path():
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
        try:
            shutil.rmtree(path)
            logging.info(f"Folder was removed successfully: {path}")
        except Exception as err:
            logging.error(f"Error {err} when trying to delete folder: {path}")

    try:
        os.makedirs(path, exist_ok=True)
        logging.info(f"Folder was created successfully: {path}")
    except Exception as err:
        logging.error(f"Couldn't create a folder: {path}")
        raise SystemExit ("There was an issue creating a folder: {}".format(err))

def create_random_folder(base_path):
    """
    Creates a random folder with a name of 8 characters inside the specified path.

    :param base_path: Path where the folder will be created
    :return: Full path to the created folder
    """
    # Ensure the base path exists
    os.makedirs(base_path, exist_ok=True)

    # Generate a random folder name with 8 characters
    folder_name = ''.join(random.choices(string.ascii_letters, k=8))
    full_path = os.path.join(base_path, folder_name)

    # Create the folder
    os.makedirs(full_path)

    return full_path