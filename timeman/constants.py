'''timeman constants'''

import datetime
from pytaskcoach import DEFAULT_DATETIME_FMT

SECS_PER_DAY = 86400
SECS_PER_HOUR = 3600
MICROSECS_PER_SEC = 1000000

EFFORT_KEYS_SORTED = ('category', 'start', 'end', 'effort', 'task')

DEFAULT_TIMEDELTA = datetime.timedelta(weeks=1)

DEFAULT_PROFILE_NAME = 'default'
PROFILE_EXT = 'json'
DEFAULT_PROFILE_FNAME = '.'.join((DEFAULT_PROFILE_NAME, PROFILE_EXT))

DEFAULT_CONFIG_DIR_ENVIRONMENT_VARIABLE_NAME = 'TIMEMAN'

PROFILE_TASKCOACH_CONFIG_DIRS_KEY = 'taskcoach_cfg_dirs'
PROFILE_ATIMETRACKER_CONFIG_DIRS_KEY = 'atimetracker_cfg_dirs'