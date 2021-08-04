#!/usr/bin/env python

from setuptools import setup, find_namespace_packages
import elastic_ssh

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="elastic-ssh",
      long_description=long_description,
      long_description_content_type='text/markdown',
      version=elastic_ssh.__version__,
      packages=find_namespace_packages(include=['elastic*']),
      install_requires=[
            'questionary>=1.0,<2.0',
            'boto3>=1.10.0,<2.0',
            'click>=7',
            'click-default-group',
            'xdg'
      ],
      entry_points={
            'console_scripts': ['aws-ec2=elastic_ssh.console:main']
      },
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
      ],
      python_requires='>=3.5'
)
