"""setup.py for install this package"""
from setuptools import setup, find_packages
from labelme2datasets.version import __version__


def get_long_description():
    with open('README.md', encoding='utf-8') as readme_f:
        return readme_f.read()


def get_install_requires():
    with open('requirements.txt', encoding='utf-8') as req_f:
        return req_f.read().splitlines()


def get_version():
    return __version__


setup(
    name='labelme2datasets',
    version=get_version(),
    description='python scripts to convert labelme-generated-jsons to voc/coco style datasets.',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/veraposeidon/labelme2Datasets",
    author='veraposeidon',
    packages=find_packages(include=['labelme2datasets', 'labelme2datasets.*']),
    install_requires=get_install_requires(),
    entry_points={
        'console_scripts': [
            'labelme_json2dataset = labelme2datasets.labelme_json2dataset:main',
            'labelme_bbox_json2voc = labelme2datasets.labelme_bbox_json2voc:main',
            'split_voc_datasets = labelme2datasets.split_voc_datasets:main',
            'voc2coco = labelme2datasets.voc2coco:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
