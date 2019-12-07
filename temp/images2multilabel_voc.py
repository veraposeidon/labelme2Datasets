# coding=utf-8
# 转换多标签图像分类数据至VOC格式数据集
# For personal use.

from __future__ import print_function
import re

from pathlib import Path
from PIL import Image
import lxml.builder
import lxml.etree
import numpy as np
import progressbar

from temp.labels_cn_en import en_cn_dict_build  # convert chinese label to english label

# configuration for big image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


# build a chinese-english label convert dict
(cn2ens, en2cns) = en_cn_dict_build("瑕疵中英文名.txt")

# 多标签缺陷图像
src_dir = Path("E:/Documents/Datasets/AluminiumClassification/select_defect")

# 输出文件夹
output_dir = Path("E:/Documents/Datasets/AluminiumClassification/multilabeldataset")

# regex：中文标签
cn_pattern = re.compile(r"^([^a-zA-Z0-9]+)")
# regex：数字时间作为ID
date_pattern = re.compile(r"\d+")

file_names = list(src_dir.glob("*.jpg"))

# using progress bar
for i in progressbar.progressbar(range(len(file_names))):
    filepath = file_names[i]
    label_text = cn_pattern.findall(filepath.name)[0]  # 获取中文标签名字
    labels = label_text.split(",")  # 获取多个标签
    labels = [cn2ens[o] for o in labels]  # 转换为英文标签
    base = re.findall(date_pattern, filepath.name)[0]  # 保留时间作为图像ID
    # annotation xml file
    out_xml_file = output_dir / (str(base) + ".xml")
    # src image file
    out_img_file = output_dir / (str(base) + '.jpg')

    # 读取图像
    img = np.asarray(Image.open(filepath))
    # 保存原图
    Image.fromarray(img).save(out_img_file)

    # 制作VOC 格式标注文件（忽略bndbox信息）
    maker = lxml.builder.ElementMaker()
    xml = maker.annotation(
        maker.folder(""),  # folder name
        maker.filename(base + '.jpg'),  # img path
        maker.source(  # img source, doesn't matter
            maker.database("multiple label defect"),
            maker.annotation(""),
            maker.image(""),
        ),
        maker.size(  # image size(height, width and channel)
            maker.height(str(img.shape[0])),
            maker.width(str(img.shape[1])),
            maker.depth(str(img.shape[2])),
        ),
        maker.segmented("0"),  # if for segmentation
    )

    # 因为没有BBOX, 只能以标签为实例
    for label in labels:
        xml.append(
            maker.object(  # object info
                maker.name(label),  # label name(in english)
                maker.pose(""),  # pose info, doesn't matter
                maker.truncated("0"),  # truncated info, doesn't matter
                maker.difficult("0"),  # diificulty, doesn't matter
                # maker.bndbox(  # bbox(up-left corner and bottom-right corner points)
                #     maker.xmin(0),
                #     maker.ymin(0),
                #     maker.xmax(0),
                #     maker.ymax(0),
                # ),
            )
        )
    # save voc annotation to xml file
    with open(out_xml_file, 'wb') as f:
        f.write(lxml.etree.tostring(xml, pretty_print=True))
