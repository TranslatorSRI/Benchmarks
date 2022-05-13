# Copyright (c) 2022, CoVar, LLC. All rights reserved.
# Terms of ownership and licensing of this software are governed by the
# associated LICENSE.TXT.

import os

from setuptools import find_packages, setup

setup(
    name='benchmarks',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'benchmarks_eval = '
            'benchmarks.cli.eval:main',
            'benchmarks_get = '
            'benchmarks.cli.get:main',
            'benchmarks_score = '
            'benchmarks.cli.score:main',
        ]
    }
)
