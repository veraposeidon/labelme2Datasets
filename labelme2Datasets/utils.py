"""
some common functions.
"""

# coding=utf-8


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
