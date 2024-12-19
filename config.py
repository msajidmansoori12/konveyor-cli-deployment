# config.py
VERSION = None
BUILD = None
MISC_DOWNSTREAM_PATH = None
EXTRACT_BINARY = None
GET_IMAGES_OUTPUT = None
BUNDLE = None
NO_BREW = None

def set_config(config):
    """Loads config from JSON file and assigns constants"""
    global VERSION, BUILD, MISC_DOWNSTREAM_PATH, EXTRACT_BINARY, GET_IMAGES_OUTPUT, BUNDLE, NO_BREW

    MISC_DOWNSTREAM_PATH = config["misc_downstream_path"]
    EXTRACT_BINARY = config["extract_binary"]
    GET_IMAGES_OUTPUT = config["get_images_output"]
    BUNDLE = config["bundle"]
    NO_BREW = config["no_brew"]
