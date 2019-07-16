#!/usr/bin/env python

import imp
from setuptools import setup, find_packages

setup(
    name='arcade-voice',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['scipy','numpy','flask', 'dialogflow','google-cloud-speech','google-cloud-texttospeech','pydub'],
)
