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

from boto3 import client
from botocore.exceptions import ClientError
from click import UsageError
from questionary import Choice, select


class InstanceHelper(object):
    def __init__(self):
        self.ec2 = client('ec2')

    def get_instance(self, instance):
        try:
            result = self.ec2.describe_instances(
                Filters=[
                    {
                        'Name': 'instance-state-code',
                        'Values': [
                            '16'
                        ]
                    }
                ],
                InstanceIds=[
                    instance
                ]
            )
        except ClientError as e:
            raise UsageError(e)

        if len(result['Reservations']) == 0:
            raise KeyError("Instance not found")

        return result['Reservations'][0]['Instances'][0]

    def select_instance(self, message='Choose an instance', include_none=False):
        page_size = 7 if include_none else 8

        paginator = self.ec2.get_paginator('describe_instances')
        page_iterator = paginator.paginate(
            Filters=[{'Name': 'instance-state-code', 'Values': ['16']}],  # Instances in a running state only
            PaginationConfig={'PageSize': page_size},
        )

        try:
            for page in page_iterator:
                choices = list(map(InstanceHelper.__create_choice, page['Reservations']))

                if 'NextToken' in page:
                    choices.append('More')
                if include_none:
                    choices.append(Choice(title='None', value=False))

                choices.append('Cancel')

                answer = select(
                    message,
                    choices,
                    use_shortcuts=True,
                    instruction=' ',
                ).ask()

                if answer == 'More':
                    # Clear the previous line
                    print("\033[A                             \033[A")
                elif answer == 'Cancel' or answer is None:
                    exit(1)
                else:
                    return answer
        except ClientError as e:
            raise UsageError(e)

    @staticmethod
    def __create_choice(instances):
        # Find a name tag
        tags = [tag for tag in instances['Instances'][0]['Tags'] if tag['Key'] == 'Name']

        return Choice(
            title=instances['Instances'][0]['InstanceId'] + (' (' + tags[0]['Value'] + ')' if len(tags) == 1 else ''),
            value=instances['Instances'][0]['InstanceId']
        )
