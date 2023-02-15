from setuptools import find_packages, setup

setup(
    name='benchmarks',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'httpx',
        'matplotlib',
        'numpy',
        'requests',
        'tqdm',
        'xmltodict'
    ],
    entry_points={
        'console_scripts': [
            'benchmarks_eval = '
            'benchmarks.cli.eval:main',
            'benchmarks_fetch = '
            'benchmarks.cli.fetch:main',
            'benchmarks_score = '
            'benchmarks.cli.score:main',
        ]
    }
)
