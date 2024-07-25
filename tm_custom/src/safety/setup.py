from setuptools import find_packages, setup

package_name = 'safety'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']), 
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'dataclass_package'],
    zip_safe=True,
    maintainer='rslomron',
    maintainer_email='mkiyama@scu.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['safety = safety.safety_node:main',
                            'demo = safety.safety_demo:main',
                            'stow_safety = safety.safety_demo_stow:main',
                            'stow_controller = safety.controller_demo_stow:main',
        ],
    },
)

