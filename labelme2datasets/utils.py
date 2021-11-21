"""
some common functions.
"""

# coding=utf-8

import os.path as osp

def get_label_conversion_dict(dict_file):
    """
    自定义标签转换，例如将中文标签转换为英文标签
    custom label conversion, for example, convert chinese label to english label, vice versa.
    """
    if dict_file is None:
        return {}
    with open(dict_file, "r", encoding='UTF-8') as dict_f:
        label_dict = {}
        for line in dict_f:
            line = line.strip()
            if line == "":
                continue
            words = line.split(":")
            label_dict[words[0].strip()] = words[1].strip()
    return label_dict


def get_coco_category(labels_file):
    """生成标签字典，用于生成COCO数据集时供查询"""
    if not osp.exists(labels_file):
        print('file not exists:', labels_file)
        return None
    attr_dict = {"categories": []}
    label_id = 0
    with open(labels_file, "r", encoding='UTF-8') as label_f:
        for line in label_f:
            label = line.strip()
            label_item = {"supercategory": "defect", "id": label_id, "name": label}
            attr_dict["categories"].append(label_item)
            label_id += 1
    return attr_dict
