"""setup.py for install this package"""
from setuptools import setup, find_packages

setup(
    name='labelme_to_datasets',
    version='0.1',
    description='python scripts to convert labelme-generated-jsons to voc/coco style datasets.',
    author='veraposeidon',
    packages=find_packages(include=['labelme_to_datasets', 'labelme_to_datasets.*']),
    install_requires=[
        'imgviz~=1.4.1',
        'pillow~=8.4.0',
        'labelme~=4.5.13',
        'lxml~=4.6.4',
        'progressbar~=2.5'
    ],
    entry_points={
        'console_scripts': [
            'labelme_json2dataset = labelme_to_datasets.labelme_json2dataset:main',
            'labelme_bbox_json2voc = labelme_to_datasets.labelme_bbox_json2voc:main'
        ]
    },
)
