from setuptools import setup
from glob import glob
import os

package_name = 'factory_robot'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Factory Robot Team',
    maintainer_email='maintainer@example.com',
    description='ROS 2 factory material handling robot starter',
    license='MIT',
    entry_points={
        'console_scripts': [
            'mission_manager = factory_robot.mission_manager:main',
            'ultrasonic_guard = factory_robot.ultrasonic_guard:main',
            'camera_perception = factory_robot.camera_perception:main',
        ],
    },
)
