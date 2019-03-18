'''timeman config'''

import json
from os import environ
from os.path import join

from timeman.constants import *

def get_default_profile():
    default_profile_path = join(
        environ[DEFAULT_CONFIG_DIR_ENVIRONMENT_VARIABLE_NAME],
        DEFAULT_PROFILE_FNAME)
    with open(default_profile_path) as f:
        return json.load(f)
