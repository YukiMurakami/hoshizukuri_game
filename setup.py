import os
from setuptools import setup, find_packages


def read_requirements():
    """Parse requirements from requirements.txt."""
    reqs_path = os.path.join('.', 'requirements.txt')
    with open(reqs_path, 'r') as f:
        requirements = [line.rstrip() for line in f]
    return requirements


with open("Readme.md") as f:
    readme = f.read()


setup(
    name='hoshizukuri_game',
    version='1.0',
    description='This module can play the Hoshizukuri game.',
    long_description=readme,
    author='Haruki',
    author_email='muru31415926@gmail.com',
    install_requires=read_requirements(),
    url='',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
