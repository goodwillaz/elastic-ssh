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

import json
import logging
import os
from pathlib import Path
from shutil import which
from typing import Text, Optional

import boto3
from botocore.exceptions import ClientError
from click import UsageError

from elastic_ssh.instance import InstanceHelper


class SSH(object):

    def __init__(self, ssh_exec: Text = which('ssh')):
        self.logger = logging.getLogger('ssh.ssh')
        self.instance_helper = InstanceHelper()
        self.ssh_exec = ssh_exec

    def ssh(self, instance: Text, private_key: Path, instance_user: Text = 'ec2-user',
            bastion: Optional[Text] = None, bastion_user: Optional[Text] = None, bastion_port: int = 22,
            command: Optional[Text] = None, instance_port: int = 22):

        self.logger.debug('Using key-pair at %s', private_key)
        public_key = private_key.with_name('{name}.pub'.format(name=private_key.name)).resolve()

        # Non-conditional args, we'll always use them
        ssh_args = ['-t', '-i', str(private_key), '-p', str(instance_port)]

        # If we have a bastion and the instance we want is not the bastion and it's not public, use the bastion
        if bastion and bastion_user and instance != bastion:
            bastion_az, bastion_public_dns, _ = self.__instance_info(bastion)
            self.__send_ssh_key(
                InstanceId=bastion,
                InstanceOSUser=bastion_user,
                AvailabilityZone=bastion_az,
                SSHPublicKey=public_key.read_text()
            )
            ssh_args.extend(['-o', 'ProxyCommand ssh -W %h:%p -p {port} -i {key} {user}@{host}'.format(
                port=bastion_port,
                key=str(private_key),
                user=bastion_user,
                host=bastion_public_dns)])

        instance_az, instance_public_dns, instance_private_dns = self.__instance_info(instance)

        self.__send_ssh_key(
            InstanceId=instance,
            InstanceOSUser=instance_user,
            AvailabilityZone=instance_az,
            SSHPublicKey=public_key.read_text()
        )

        ssh_args.append('{user}@{host}'.format(
            user=instance_user, host=instance_public_dns if instance_public_dns != '' else instance_private_dns))

        if command is not None:
            ssh_args.append(command)

        self.logger.debug('SSH arguments - %s', json.dumps(ssh_args))

        os.execvp(self.ssh_exec, ssh_args)

    def __send_ssh_key(self, **kwargs):
        self.logger.debug('Loading public key onto %s for %s', kwargs['InstanceId'], kwargs['InstanceOSUser'])
        try:
            response = boto3.client('ec2-instance-connect').send_ssh_public_key(**kwargs)
            if not response['Success']:
                raise UsageError('Unable to add SSH key to %s (%s)'.format(kwargs['InstanceId'], response['RequestId']))
        except ClientError as e:
            raise UsageError(e)

    def __instance_info(self, instance: Text):
        self.logger.debug('Looking up information for %s', instance)
        try:
            result = self.instance_helper.get_instance(instance)
        except ClientError as e:
            raise UsageError(e)

        return (result['Placement']['AvailabilityZone'].strip(),
                result['PublicDnsName'].strip(),
                result['PrivateDnsName'].strip())
