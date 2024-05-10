from setuptools import find_packages, setup
from setuptools import setup

package_name = 'techman_robot_get_status'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rslomron',
    maintainer_email='mkiyama@scu.edu',
    description='techman robot get status python scripts',
    license='BSD',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'image_talker = tm_get_status.image_pub:main',
            'status_talker = tm_get_status.get_status:main'
        ],
    },
)
