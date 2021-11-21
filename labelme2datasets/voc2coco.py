"""turn voc format datasets into coco format datasets"""
# coding = utf-8

import argparse
import sys
import os
import os.path as osp
from pathlib import Path
import json
import glob
from collections import OrderedDict
import shutil
import xmltodict
from labelme2datasets.utils import get_coco_category


def get_xml_anno_list(set_file, voc_dir, coco_dir):
    """get_xml_anno_list and copy source image to coco dir."""
    voc_split = Path(set_file).stem  # e.g. train.txt -> train
    anno_list = []
    with open(set_file, "r", encoding='UTF-8') as f_open:
        for line in f_open:
            base = line.strip()
            # absolute path of file
            anno_list.append(osp.join(voc_dir, 'Annotations', base + ".xml"))
            # copy image to COCO dataset
            # MARK: jpg or png or other pic suffix
            image_from = osp.join(voc_dir, "JPEGImages", base + ".jpg")
            if not osp.exists(image_from):
                print(f"some thing wrong, file not exists: {image_from}")
            image_dest = osp.join(coco_dir, voc_split)
            shutil.copy(image_from, image_dest)
            # print("copy image {} to {}".format(base, image_dest))
    print("build anno_list. total samples:", len(anno_list))
    return anno_list


def get_image_with_anno(anno_file):
    """get image with annotation"""
    image = {}
    with open(anno_file, 'r', encoding='utf8') as f_open:
        doc = xmltodict.parse(f_open.read())
        image['file_name'] = str(doc['annotation']['filename'])
        image['height'] = int(doc['annotation']['size']['height'])
        image['width'] = int(doc['annotation']['size']['width'])
    return image


def get_coco_anno_with_file(anno_file, image_id, attr_dict):
    """get coco annotation with file"""
    annotations = []
    with open(anno_file, 'r', encoding='utf8') as f_open:
        doc = xmltodict.parse(f_open.read())
        anno_id = 1
        if 'object' in doc['annotation']:
            objects = doc['annotation']['object']
            if isinstance(objects, OrderedDict):
                obj = objects
                objects = [obj]

            for obj in objects:
                for value in attr_dict["categories"]:
                    if str(obj['name']) != value["name"]:
                        continue
                    annotation = {"iscrowd": 0, "image_id": image_id}
                    # annotation["segmentation"] = []
                    box_x = int(float(obj["bndbox"]["xmin"]))
                    box_y = int(float(obj["bndbox"]["ymin"]))
                    box_w = int(float(obj["bndbox"]["xmax"])) - box_x + 1
                    box_h = int(float(obj["bndbox"]["ymax"])) - box_y + 1
                    annotation["bbox"] = [box_x, box_y, box_w, box_h]
                    annotation["area"] = float(box_w * box_h)
                    annotation["category_id"] = value["id"]
                    annotation["ignore"] = 0
                    annotation["segmentation"] = [[box_x, box_y, box_x, (box_y + box_h - 1),
                                                   (box_x + box_w - 1), (box_y + box_h - 1),
                                                   (box_x + box_w - 1), box_y]]
                    annotation["id"] = anno_id
                    anno_id += 1
                    annotations.append(annotation)
        else:
            print(f"File: {anno_file} doesn't have any object")

    return annotations


def save_coco_json(attr_dict, anno_path):
    """save coco json file"""
    json_string = json.dumps(attr_dict)
    with open(anno_path, "w", encoding="utf8") as anno_f:
        anno_f.write(json_string)


def generate_coco_annotation(set_file, voc_dir, coco_dir):
    """
    generate coco annotation from voc annotation
    """
    voc_split = Path(set_file).stem  # e.g. train.txt -> train
    anno_file = voc_split + '.json'

    if osp.exists(osp.join(coco_dir, voc_split)):
        print("directory not supposed to exist: ", osp.join(coco_dir, voc_split))
        sys.exit(1)
    os.makedirs(osp.join(coco_dir, voc_split))

    anno_path = osp.join(coco_dir, 'annotations', anno_file)
    if osp.exists(anno_path):
        print('anno file exists:', anno_path)
        sys.exit(1)

    # check class_names.txt in voc dataset
    attr_dict = get_coco_category(osp.join(voc_dir, 'class_names.txt'))
    if attr_dict is None:
        print('class_names.txt not found')
        sys.exit(1)

    anno_list = get_xml_anno_list(set_file, voc_dir, coco_dir)

    image_id = 0
    images = []
    annotations = []

    for file in anno_list:
        if not osp.exists(file):
            print("file not exists", file)
            continue

        image_id += 1

        # get image info
        image = get_image_with_anno(file)
        image['id'] = image_id
        images.append(image)

        # get annotation info
        current_annotations = get_coco_anno_with_file(file, image_id, attr_dict)
        for item in current_annotations:
            annotations.append(item)

    attr_dict["images"] = images
    attr_dict["annotations"] = annotations
    attr_dict["type"] = "instances"

    # save file
    save_coco_json(attr_dict, anno_path)


def main():
    """turn voc format datasets into coco format datasets."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--voc_dir', help='INPUT: voc style dataset root directory')
    parser.add_argument('--coco_dir', help='OUTPUT: coco style dataset root directory')
    args = parser.parse_args()

    if not osp.exists(args.voc_dir):
        print('directory not exists:', args.voc_dir)
        sys.exit(1)

    set_files = glob.glob(osp.join(args.voc_dir, 'ImageSets', 'Main', '*.txt'))
    if len(set_files) == 0:
        print(f"set file not exists: {osp.join(args.voc_dir, 'ImageSets', 'Main')}")
        sys.exit(1)

    if not osp.exists(args.coco_dir):
        os.makedirs(args.coco_dir)
        os.makedirs(osp.join(args.coco_dir, 'annotations'))

    # iterate every set file(eg. train.txt、test.txt)
    for set_file in set_files:
        generate_coco_annotation(set_file, args.voc_dir, args.coco_dir)


if __name__ == '__main__':
    main()
