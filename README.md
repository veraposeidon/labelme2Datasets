<img src="logo.png" width="200" >

# 数据集转换脚本（工具向）

**News:** 最近开始论文实验，需要重新整理一下数据集，顺便整理一下这个代码仓库。

## 简介

仓库中的脚本用于将Labelme标注的数据转换为PASCAL VOC格式或MS COCO格式的标准数据集，便于直接利用现有的训练框架进行训练。

## 标注工具和常见的两种数据集格式

Labelme是我用的标注工具，对图像进行多种类型的标注，可以直接得到`json`文件。GitHub地址如下：

[labelme: Image Polygonal Annotation with Python](https://github.com/wkentaro/labelme)

PASCAL-VOC和MS-COCO是两个大型的开源数据集，其数据集的标注形式成为了通用的标注方式，常见的视觉模型的训练框架都支持这两种格式的读取，将自己的数据集转换为这两种标注方式，可以避免修改读取数据的代码。

两种数据集和标注格式的介绍：

[目标检测数据集PASCAL VOC简介](https://arleyzhang.github.io/articles/1dc20586/)

[目标检测数据集MSCOCO简介](https://arleyzhang.github.io/articles/e5b86f16/)


## 仓库中的代码文件

- `labelme_json_to_dataset.py`: 演示如何将单个labelme标注的json文件转换为单张图像的数据集。

  **usage:**  `python labelme_json_to_dataset.py test/test_single.json -o test/test_single`
- labels_cn_en.py: build dictionary for label's chinese name and english name.  (for people use english name in datasets while annotating other language in labelme)
- labelme2voc.py: convert a batch of labelme json files to voc format dataset.
- split_dataset.py：split voc annotation files into train set and test set.
- voc_xml2coco_json.py：convert voc format dataset to coco format dataset, which is a json file.
- label_names.txt：label names annotated with Labelme tool. important file for later convert.
- 瑕疵中英文名.txt：label name comparison in chinese and english. you can change this file for your task.

## 安装

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

## 拓展

仓库中的脚本只针对目前本人已有数据的转换，如果有实例分割、语义分割或视频标注等数据，可以参考labelme提供的示例代码进行修改，示例代码演示了这类标注文件如何转换成VOC格式数据集：

https://github.com/wkentaro/labelme/tree/master/examples

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
