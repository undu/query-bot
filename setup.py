#/usr/bin/env python2

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(name='query-bot',
      version='0.1.0',
      description='IRC Bot that likes to reply',
      packages=find_packages(),
      install_requires=[
        'httplib2',
        'simplejson',
        'xmltodict',
      ],
      )
