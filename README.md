# Datasets Conversion：Labelme -> PascalVOC format -> MS COCO format

## Annotation Tool and Two Common Dataset Format

Labelme is a common annotation tool.

It generate a json file for annotated image.

This repo is aim to convert these json files to image dataset for CV deep learning.
  
For your information: 

[labelme: Image Polygonal Annotation with Python](https://github.com/wkentaro/labelme)

PASCAL-VOC and MS-COCO are two common open source image datasets.

And are supported by most open source object detection algorithm or architecture. 

For your information:

[目标检测数据集PASCAL VOC简介](https://arleyzhang.github.io/articles/1dc20586/)

[目标检测数据集MSCOCO简介](https://arleyzhang.github.io/articles/e5b86f16/)


## Python Tools in this Repo:

- json_to_dataset.py: demonstrate how to convert a single labelme json file to a single image dataset.
- labels_cn_en.py: build dictionary for label's chinese name and english name.  (for people use english name in datasets while annotating other language in labelme)
- labelme2voc.py: convert a batch of labelme json files to voc format dataset.
- split_dataset.py：split voc annotation files into train set and test set.
- voc_xml2coco_json.py：convert voc format dataset to coco format dataset, which is a json file.
- label_names.txt：label names annotated with Labelme tool. important file for later convert.
- 瑕疵中英文名.txt：label name comparison in chinese and english. you can change this file for your task.

## Required Packages and Installation Guide

labelme environment:  [from labelme repo](https://github.com/wkentaro/labelme#anaconda) 
```bash
# python3
conda create --name=labelme python=3.6
source activate labelme
# conda install -c conda-forge pyside2
# conda install pyqt
pip install pyqt5  # pyqt5 can be installed via pip on python3
pip install labelme
```

other tools:
```bash
conda install scikit-learn  # used to split train set and test set 
pip install xmltodict
pip install progressbar2    # for progress visualize
```

## USAGE

### step1: prepare label_names.txt and cn-to-en.txt(e.g. 瑕疵中英文名.txt)

cn-to-en.txt(e.g. 瑕疵中英文名.txt) is required. 
for english name in labelme annotation, fill english name both in first column and second column.

### step2：convert labelme jsons to voc style datasets

`python labelme2voc.py labels_file en_cn_file in_dir out_dir `

- labels_file: label_names.txt
- en_cn_file: cn-en table file
- in_dir: directory contains labelme's json files
- out_dir：output dir for voc format dataset

### step3: split datasets to train set and test set

`python split_dataset.py voc_dir test_ratio`

- voc_dir: VOC format dataset directory
- test_ratio: test set ratio in whole dataset

this automatically generate train.txt and test.txt

### step4: convert voc style datasets to coco style datasets

`python voc_xml2coco_json.py imgset_file anno_dir json_file `

- imgset_file: image set file path. (Use train.txt or test.txt generated last step)
- anno_dir: directory contains voc dataset xml format annotations. (usually in VOC/Annotations)
- json_file: output file path. COCO style json file.

change the parameters to get coco format train set and test set.
