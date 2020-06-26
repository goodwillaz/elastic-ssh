#!/usr/bin/env python

from setuptools import setup, find_namespace_packages
import elastic_ssh

setup(name="elastic-ssh",
      version=elastic_ssh.__version__,
      package_dir={'': '.'},
      packages=find_namespace_packages(where='elastic_ssh'),
      install_requires=[
            'questionary>=1.0,<2.0',
            'boto3>=1.10.0,<2.0',
            'click>=7',
            'click-default-group',
            'xdg'
      ],
      entry_points={
            'console_scripts': ['aws-ec2=elastic_ssh.console:main']
      })
