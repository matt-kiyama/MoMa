from setuptools import find_packages
from setuptools import setup

setup(
    name='tm_msgs',
    version='1.1.2',
    packages=find_packages(
        include=('tm_msgs', 'tm_msgs.*')),
)
