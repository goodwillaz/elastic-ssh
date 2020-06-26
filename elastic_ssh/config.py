# Copyright 2020 Goodwill of Central and Northern Arizona
#
# Licensed under the BSD 3-Clause (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from configparser import ConfigParser
from pathlib import Path
from typing import Text, Any

from prompt_toolkit.validation import Validator, ValidationError
from xdg import XDG_CONFIG_HOME

logger = logging.getLogger('ssh.config')
CONFIG_PATH = Path(XDG_CONFIG_HOME) / 'aws-ec2' / 'config'


def _config_writer(f):
    def writer(*args):
        logger.debug("Updating %s to %s", f.__name__, args[1])
        f(*args)

        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CONFIG_PATH.open('w') as configfile:
            logger.debug("Writing to config file: %s", CONFIG_PATH)
            args[0].write(configfile)

    return writer


class Config(ConfigParser):
    def __init__(self, profile, **kwargs):
        logger.debug('Using %s profile for configuration', profile)
        self.profile = profile
        super().__init__(**kwargs)

    @staticmethod
    def load(profile='default'):
        config = Config(profile)
        logger.debug("Loading configuration from %s", CONFIG_PATH)
        config.read(str(CONFIG_PATH))
        return config

    @property
    def bastion(self):
        return self.get(self.profile, 'bastion', fallback=None)

    @bastion.setter
    @_config_writer
    def bastion(self, bastion: Any):
        # Update the config
        if not self.has_section(self.profile):
            self[self.profile] = {}

        self[self.profile]['bastion'] = '' if not bastion else bastion

    @property
    def bastion_user(self):
        return self.get(self.profile, 'bastion_user', fallback=None)

    @bastion_user.setter
    @_config_writer
    def bastion_user(self, user: Text):
        # Update the config
        if not self.has_section(self.profile):
            self[self.profile] = {}

        self[self.profile]['bastion_user'] = user

    @property
    def bastion_port(self):
        return self.get(self.profile, 'bastion_port', fallback=None)

    @bastion_port.setter
    @_config_writer
    def bastion_port(self, user: Text):
        # Update the config
        if not self.has_section(self.profile):
            self[self.profile] = {}

        self[self.profile]['bastion_port'] = user

    @property
    def key(self):
        key = self.get(self.profile, 'key', fallback=None)
        return Path(key).expanduser().resolve() if key is not None else key

    @key.setter
    @_config_writer
    def key(self, key: Path):
        # Update the config
        if not self.has_section(self.profile):
            self[self.profile] = {}

        self[self.profile]['key'] = str(key)

    @property
    def instance_user(self):
        return self.get(self.profile, 'instance_user', fallback=None)

    @instance_user.setter
    @_config_writer
    def instance_user(self, user: Text):
        # Update the config
        if not self.has_section(self.profile):
            self[self.profile] = {}

        self[self.profile]['instance_user'] = user


class KeyValidator(Validator):
    def validate(self, document):
        key = Path(document.text).expanduser()

        if not key.is_file():
            raise ValidationError(
                message="Path is not a file", cursor_position=len(document.text)
            )

        if not key.with_name('{name}.pub'.format(name=key.name)).is_file():
            raise ValidationError(
                message="Matching public key not found ({name})".format(
                    name=key.with_name('{name}.pub'.format(name=key.name))),
                cursor_position=len(document.text)
            )
