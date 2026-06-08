from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'arena_battle'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'html'), glob('html/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='keepitupp',
    maintainer_email='you@example.com',
    description='Arena Battle Robot Game with URDF',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'keyboard_controller = arena_battle.keyboard_controller:main',
            'game_logic = arena_battle.game_logic:main',
            'robot_pose_tf = arena_battle.robot_pose_tf:main',
        ],
    },
)
