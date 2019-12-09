# coding = utf-8

import argparse
import os
import os.path as osp
import xmltodict
import json
from collections import OrderedDict
import sys
from utils import get_coco_category
import shutil

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('voc_dir', help='INPUT: voc style dataset root directory')
    parser.add_argument('voc_split', help='INPUT: image set text file name, like train.txt')
    parser.add_argument('coco_dir', help='OUTPUT: coco style dataset root directory')
    parser.add_argument('anno_file', help='OUTPUT: coco annotations json file')
    args = parser.parse_args()

    if not osp.exists(args.voc_dir):
        print('directory not exists:', args.voc_dir)
        sys.exit(1)

    # FIXME: here strictly follow the voc style, you can change the path format here.
    set_file = osp.join(args.voc_dir, 'ImageSets', 'Main', args.voc_split + ".txt")
    if not osp.exists(set_file):
        print('directory not exists:', set_file)
        sys.exit(1)

    if not osp.exists(args.coco_dir):
        os.makedirs(args.coco_dir)
        os.makedirs(osp.join(args.coco_dir, 'annotations'))

    if osp.exists(osp.join(args.coco_dir, args.voc_split)):
        print("directory not supposed to exist: ", osp.join(args.coco_dir, args.voc_split))
        sys.exit(1)
    os.makedirs(osp.join(args.coco_dir, args.voc_split))

    anno_path = osp.join(args.coco_dir, 'annotations', args.anno_file)
    if osp.exists(anno_path):
        print('anno file exists:', anno_path)
        sys.exit(1)

    # check class_names.txt in voc dataset
    label_file = osp.join(args.voc_dir, 'class_names.txt')
    if not osp.exists(set_file):
        print('file not exists:', label_file)
        sys.exit(1)

    attr_dict = get_coco_category(label_file)

    anno_list = list()
    with open(set_file, "r", encoding='UTF-8') as f_open:
        for Line in f_open:
            base = Line.strip()
            # print(base)
            anno_list.append(osp.join(args.voc_dir, 'Annotations', base + ".xml"))  # absolute path of file
            # TODO: copy image to COCO dataset
            image_from = osp.join(args.voc_dir,  "JPEGImages", base+".jpg")   # jpg or png or other pic suffix
            if not osp.exists(image_from):
                print("some thing wrong, file not exists: {}".format(image_from))
            image_dest = osp.join(args.coco_dir,  args.voc_split)
            shutil.copy(image_from, image_dest)
            # print("copy image {} to {}".format(base, image_dest))

    print("build anno_list. total samples:", len(anno_list))

    images = list()
    annotations = list()

    image_id = 0
    for file in anno_list:
        if not osp.exists(file):
            print("file not exists", file)
            continue

        image_id += 1
        # print("{}/{}".format(image_id, len(anno_list)))

        # get image info
        image = dict()
        doc = xmltodict.parse(open(file).read())
        image['file_name'] = str(doc['annotation']['filename'])
        image['height'] = int(doc['annotation']['size']['height'])
        image['width'] = int(doc['annotation']['size']['width'])
        image['id'] = image_id
        images.append(image)

        # get annotation info
        anno_id = 1
        if 'object' in doc['annotation']:
            objects = doc['annotation']['object']
            if isinstance(objects, OrderedDict):
                obj = objects
                objects = list()
                objects.append(obj)

            for obj in objects:
                for value in attr_dict["categories"]:
                    annotation = dict()
                    if str(obj['name']) == value["name"]:
                        # annotation["segmentation"] = []
                        annotation["iscrowd"] = 0
                        annotation["image_id"] = image_id
                        x = int(obj["bndbox"]["xmin"])
                        y = int(obj["bndbox"]["ymin"])
                        w = int(obj["bndbox"]["xmax"]) - x + 1
                        h = int(obj["bndbox"]["ymax"]) - y + 1
                        annotation["bbox"] = [x, y, w, h]
                        annotation["area"] = float(w * h)
                        annotation["category_id"] = value["id"]
                        annotation["ignore"] = 0
                        annotation["segmentation"] = [
                            [x, y, x, (y + h - 1), (x + w - 1), (y + h - 1), (x + w - 1), y]]
                        annotation["id"] = anno_id
                        anno_id += 1
                        annotations.append(annotation)
        else:
            print("File: {} doesn't have any object".format(file))

    attr_dict["images"] = images
    attr_dict["annotations"] = annotations
    attr_dict["type"] = "instances"

    # save file
    json_string = json.dumps(attr_dict)
    with open(osp.join(args.coco_dir, 'annotations', args.anno_file), "w") as f:
        f.write(json_string)


if __name__ == '__main__':
    main()
