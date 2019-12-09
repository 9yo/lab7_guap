# -*- coding: utf-8 -*-

import os
import os.path

from setuptools import find_packages
from setuptools import setup


NAME = 'super_resolver'
VERSION = '0.0.1'


def find_requires():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    requirements = []
    with open(os.path.join(dir_path, 'requirements'), 'r') as rq:
        requirements = rq.readlines()
        return requirements


def main():
    setup(
        name=NAME,
        version=VERSION,
        description='Краткое описание',
        long_description='''Подробное описание''',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Programming Language :: Python'
        ],
        packages=find_packages(), install_requires=find_requires(),
        data_files=[],
        include_package_data=True,
        entry_points={
            'console_scripts': ['asyncdig=super_resolver.asyncres: main'],
        },
    )


if __name__ == '__main__':
    main()
