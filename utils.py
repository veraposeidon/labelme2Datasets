# coding=utf-8


# 自定义标签转换，例如将中文便签转换为英文标签。
def label_name_convert_dict_build(dict_file):
    f = open(dict_file, 'r', encoding='UTF-8')

    fst2snd = []
    for line in f:
        fst2snd.append(line.split(','))

    fst2snd_dict = {o[0]: o[1][:-1] for o in fst2snd}
    # snd2fst_dict = {fst2snd_dict[o]: o for o in fst2snd_dict}

    print("dict build complete!")
    return fst2snd_dict


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
