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

  **用法**  `python labelme_json_to_dataset.py [-h] [-o OUT] json_file`

  **举例**  `python labelme_json_to_dataset.py test/test_single.json -o test/test_single`

- `bbox_labelme2voc.py`: 批量处理labelme标注的json文件，转换成VOC格式的数据集。

  **用法** `python bbox_labelme2voc.py [-h] --labels LABELS [--label_dict LABEL_DICT] input_dir output_dir `

  **举例** `python bbox_labelme2voc.py --labels test/label_names.txt --label_dict test/瑕疵中英文-Dict.txt test/test_jsons test/test_voc`

- `split_dataset.py`：将VOC数据集中的样本按照比例，分割成训练集和测试集，并保存在`ImageSets/Main`文件夹下。
  
  **用法** `python split_dataset.py [-h] [--random_state RANDOM_STATE] voc_dir test_ratio`
  
  **举例** `python split_dataset.py test/test_voc 0.35`

- `utils.py`: 内置一些简单的转换函数。

- voc_xml2coco_json.py：convert voc format dataset to coco format dataset, which is a json file.

## 安装

[labelme](https://github.com/wkentaro/labelme): 

```bash
# python3
conda create --name=labelme python=3.6
conda activate labelme
conda install labelme
```

其他工具：
```bash
conda install progressbar2    # 进度条
conda install scikit-learn  # 用于分割数据集 
conda install xmltodict	
conda install lxml
```

## 拓展

仓库中的脚本只针对目前本人已有数据的转换，如果有实例分割、语义分割或视频标注等数据，可以参考labelme提供的示例代码进行修改，示例代码演示了这类标注文件如何转换成VOC格式数据集：

https://github.com/wkentaro/labelme/tree/master/examples

## 使用流程

### 步骤一：使用Labelme标注数据集

- 标注得到一批json文件
- 准备好`label_names.txt`，包含数据集的目标标签，可参考`test/label_names.txt`
- 如果有需要进行标签名称转换的，准备好`label_dict.txt `，可参考`test/label_dict.txt`

### 步骤二：转换为VOC风格的数据集

`python bbox_labelme2voc.py --labels LABELS [--label_dict LABEL_DICT] input_dir output_dir `

- `LABELS`：`label_names.txt`
- `LABEL_DICT`：`label_dict.txt`
- `input_dir `：json标注文件所在文件夹
- `output_dir`：VOC数据集文件夹

### 步骤三：分割训练集和测试集

`python split_dataset.py [--random_state RANDOM_STATE] voc_dir test_ratio`

- `voc_dir`：VOC数据集文件夹
- `test_ratio`：测试集比例
- `RANDOM_STATE`：随机数种子

训练集和测试集文件在`ImageSets/Main`文件夹下。