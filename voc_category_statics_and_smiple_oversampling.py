# coding=utf-8

import argparse
import os.path as osp
import sys
from collections import OrderedDict
import xmltodict
from numpy.random import randint
import random


# 对VOC数据集进行简单的标注统计及过采样处理
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('voc_dir', help='input annotated directory')
    parser.add_argument('set', help='set split, e.g. train')
    parser.add_argument('--save_name', help='over sampling result. ignore it if only for statics')
    args = parser.parse_args()

    if not osp.exists(args.voc_dir):
        print('directory not exists:', args.voc_dir)
        sys.exit(1)

    set_file = osp.join(args.voc_dir, "ImageSets", "Main", args.set + ".txt")
    if not osp.exists(set_file):
        print('file not exists:', set_file)
        sys.exit(1)

    annotations_dir = osp.join(args.voc_dir, "Annotations")
    if not osp.exists(annotations_dir):
        print('directory not exists:', annotations_dir)
        sys.exit(1)

    # read label file for labels dict
    labels_dict = {}

    # read set file for samples
    samples = []

    with open(set_file, 'r', encoding='UTF-8') as f_open:
        for base in f_open.readlines():
            base = base.strip()
            anno_file = osp.join(annotations_dir, base + ".xml")
            if not osp.exists(anno_file):
                print("anno_file not exists:", anno_file)
                continue

            samples.append(base)
            # read xml and process
            doc = xmltodict.parse(open(anno_file).read())

            # obj_list
            if 'object' in doc['annotation']:
                objects = doc['annotation']['object']
                if isinstance(objects, OrderedDict):
                    obj = objects
                    objects = list()
                    objects.append(obj)
                for obj in objects:
                    label = obj['name']

                    if label in labels_dict.keys():
                        labels_dict[label].append(base) # add sample base name
                    else:
                        labels_dict[label] = [base]
            else:
                print("sample {} don't have object.".format(base))

    # print statics
    print('------------------------------------------')
    print("total samples: ", len(samples))
    anno_count = 0
    for KEY in labels_dict.keys():
        anno_count += len(labels_dict[KEY])
        print(KEY, len(labels_dict[KEY]))
    print("total annos: ", anno_count)
    print('------------------------------------------')

    if args.save_name is None:
        print("no need to save new set, task complete!")
        sys.exit(1)

    # simple oversampling
    upper_bound = max([len(labels_dict[key]) for key in labels_dict.keys()])
    upper_bound = int(upper_bound * 1.2)

    for key in labels_dict.keys():
        bias = upper_bound - len(labels_dict[key])

        idxs = randint(0, len(labels_dict[key])-1, size=bias)
        for idx in idxs:
            labels_dict[key].append(labels_dict[key][idx])

    # concat and shuffle
    save_list = []
    for key in labels_dict.keys():
        save_list = save_list + labels_dict[key]

    random.shuffle(save_list)

    # print statics
    print('------------------------------------------')
    print('after total samples: ', len(save_list))
    anno_count = 0
    for KEY in labels_dict.keys():
        anno_count += len(labels_dict[KEY])
        print(KEY, len(labels_dict[KEY]))
    print("after total annotations: ", anno_count)
    print('------------------------------------------')

    # save
    save_file = osp.join(args.voc_dir, "ImageSets", "Main", args.save_name + ".txt")
    with open(save_file, 'w', encoding='UTF-8') as f_open:
        for base in save_list:
            f_open.write(base + '\n')

    print("task completed!")


if __name__ == '__main__':
    main()
