from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name='benchmarks-runner',
    version='0.1.0',
    author="Max Wang",
    author_email="max@covar.com",
    url="https://github.com/TranslatorSRI/Benchmarks",
    description="Translator Benchmarks Runner",
    long_description_content_type="text/markdown",
    long_description=readme,
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'httpx',
        'matplotlib',
        'numpy',
        'requests',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'benchmarks_eval = '
            'benchmarks_runner.cli.eval:main',
            'benchmarks_fetch = '
            'benchmarks_runner.cli.fetch:main',
            'benchmarks_score = '
            'benchmarks_runner.cli.score:main',
        ]
    }
)
