# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    install_requires=required,
    name='connect_youtube_uploader',
    version='0.1.0',
    description='This python package handles the uploading of a Connect resources video to Youtube with video metadata added via the SchedDataInterface module.',
    long_description=readme,
    author='Kyle Kirkby',
    author_email='kyle.kirkby@linaro.org',
    url='https://github.com/linaro-marketing/connect_youtube_uploader',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
