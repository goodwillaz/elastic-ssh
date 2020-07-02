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
from pathlib import Path
from shutil import which
from typing import Text, Optional

import botocore.session
import click
from click import UsageError
from prompt_toolkit.completion import PathCompleter
import questionary

from elastic_ssh.config import Config, KeyValidator
from elastic_ssh.instance import InstanceHelper
from elastic_ssh.ssh import SSH

pass_config = click.make_pass_decorator(Config)
logging.basicConfig()
logger = logging.getLogger('ssh.console')


@click.group(context_settings={"auto_envvar_prefix": "AWS_EC2"})
@click.pass_context
@click.option('-p', '--profile', default='default', help="Profile to use", show_default=True)
@click.option('-d', '--debug', is_flag=True)
@click.version_option('version')
def main(ctx, profile: Text, debug: bool):
    if debug:
        logging.getLogger('ssh').setLevel(logging.DEBUG)
        botocore.session.get_session().set_debug_logger()

    ctx.obj = Config.load(profile)


@main.command()
@pass_config
def configure(config: Config):
    bastion = InstanceHelper().select_instance(message='Choose bastion host', include_none=True)

    bastion_user = questionary.text(message="Bastion host user", default=config.bastion_user or "").ask()

    bastion_port = questionary.text(message="Bastion host port", default=config.bastion_port or "22").ask()

    instance_user = questionary.text(message="Default instance user", default=config.instance_user or "").ask()

    key = Path(questionary.text(
        message="Private SSH Key Path",
        default=str(config.key) if config.key is not None else "",
        validate=KeyValidator,
        completer=PathCompleter(expanduser=True)).ask())

    # Save all of the configuration options
    config.bastion = bastion
    config.bastion_port = bastion_port
    config.bastion_user = bastion_user
    config.instance_user = instance_user
    config.key = key


@main.command()
@click.argument('instance', required=False)
@click.option('-u', '--user', help="Instance SSH User")
@click.option('-p', '--port', help="Instance SSH Port")
@click.option('-k', '--key', help="Private SSH Key", type=click.Path(exists=True),
              callback=lambda _, __, value: Path(value).expanduser().resolve() if value else None)
@click.option('-c', '--command', help="Command to run on instance (instead of terminal session)")
@pass_config
def ssh(config: Config, instance: Optional[Text], **kwargs):
    if not Path(which('ssh')).exists():
        raise UsageError("The ssh executable could not be found on your PATH")

    if config.key is None and not kwargs['key']:
        raise UsageError(
            'No key is specified, please run \'aws-ec2 configure\' or specify the --key option')

    instance_helper = InstanceHelper()

    if instance is None:
        instance = instance_helper.select_instance()

    # Get the instance information
    SSH().ssh(instance=instance,
              private_key=kwargs['key'] or config.key,
              instance_user=kwargs['user'] or config.instance_user,
              bastion=config.bastion,
              bastion_user=config.bastion_user,
              bastion_port=config.bastion_port,
              command=kwargs['command'] or None,
              instance_port=kwargs['port'] or 22)


if __name__ == '__main__':
    main()
