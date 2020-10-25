from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="pmg_influx",
    version="0.1",
    description="Feed data from ProxMox Mail Gateway into an InfluxDB",
    license='GPL',
    packages=['pmg_influx'],
    author='Tim Rightnour',
    author_email='the@garbled.one',
    url='https://github.com/garbled1/pmg_influx',
    project_urls={
        'Gitub Repo': 'https://github.com/garbled1/pmg_influx',
    },
    install_requires=[
        'influxdb',
        'proxmoxer'
    ],
    python_requires='>3.5',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'pmg_influx=pmg_influx.__main__:main'
        ]
    }
)
