"""
some common functions.
"""

# coding=utf-8


def get_label_conversion_dict(dict_file):
    """
    自定义标签转换，例如将中文标签转换为英文标签
    custom label conversion, for example, convert chinese label to english label, vice versa.
    """
    with open(dict_file, "r", encoding='UTF-8') as dict_f:
        label_dict = {}
        for line in dict_f:
            line = line.strip()
            if line == "":
                continue
            words = line.split(":")
            label_dict[words[0].strip()] = words[1].strip()
    return label_dict


# 生成标签字典，用于生成COCO数据集时供查询
def get_coco_category(labels_file):
    print("build attr dict.")
    attr_dict = dict()
    attr_dict["categories"] = []
    lbl_count = 0
    with open(labels_file, "r", encoding='UTF-8') as f:
        for line in f:
            label = line.strip()
            print(lbl_count, label)
            attr_dict["categories"].append({"supercategory": "defect", "id": lbl_count, "name": label})
            lbl_count += 1
    return attr_dict
