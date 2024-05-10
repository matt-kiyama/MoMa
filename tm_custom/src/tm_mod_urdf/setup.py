from setuptools import find_packages, setup

package_name = 'tm_mod_urdf'

setup(
    name=package_name,
    version='1.1.2',
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
    description='tm_mod_urdf',
    license='BSD',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'modify_urdf = tm_mod_urdf.modify_urdf:main',
            'modify_xacro = tm_mod_urdf.modify_xacro:main'
        ],
    },
)
