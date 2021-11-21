"""setup.py for install this package"""
from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_f:
    long_description = readme_f.read()

setup(
    name='labelme2datasets',
    version='0.0.2',
    description='python scripts to convert labelme-generated-jsons to voc/coco style datasets.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/veraposeidon/labelme2Datasets",
    author='veraposeidon',
    packages=find_packages(include=['labelme2datasets', 'labelme2datasets.*']),
    install_requires=[
        'imgviz~=1.4.1',
        'pillow~=8.4.0',
        'labelme~=4.5.13',
        'lxml~=4.6.4',
        'progressbar~=2.5',
        'xmltodict~=0.12.0',
        'sklearn~=0.0',
        'scikit-learn~=0.24.2',
    ],
    entry_points={
        'console_scripts': [
            'labelme_json2dataset = labelme2datasets.labelme_json2dataset:main',
            'labelme_bbox_json2voc = labelme2datasets.labelme_bbox_json2voc:main',
            'split_voc_datasets = labelme2datasets.split_voc_datasets:main',
            'voc2coco = labelme2datasets.voc2coco:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
