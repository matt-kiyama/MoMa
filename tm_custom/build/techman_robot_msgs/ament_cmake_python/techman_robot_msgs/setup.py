from setuptools import find_packages
from setuptools import setup

setup(
    name='techman_robot_msgs',
    version='1.0.0',
    packages=find_packages(
        include=('techman_robot_msgs', 'techman_robot_msgs.*')),
)
