from setuptools import find_packages
from setuptools import setup

setup(
    name='arena_battle_interfaces',
    version='0.0.0',
    packages=find_packages(
        include=('arena_battle_interfaces', 'arena_battle_interfaces.*')),
)
