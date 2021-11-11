# coding=utf-8
from __future__ import print_function

import argparse
import os.path as osp
import xmltodict
from collections import OrderedDict
import sys
import PIL
from PIL import Image
from pathlib import Path

try:
    import lxml.builder
    import lxml.etree
except ImportError:
    print('Please install lxml:\n\n    pip install lxml\n')
    sys.exit(1)

import numpy as np
import progressbar
import labelme
from labelme.utils import shape_to_mask
import logging

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(filename='my.log', level=logging.DEBUG, format=LOG_FORMAT)

class_names = []


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('voc_dir', help='INPUT: voc style dataset root directory')
    parser.add_argument('voc_split', help='INPUT: image set text file name, like train.txt')
    parser.add_argument('width', help='New region size width')
    parser.add_argument('height', help='New region size height')
    parser.add_argument('overlay_ratio', help='overlay ration both in x dimension and y dimension')
    args = parser.parse_args()

    if not osp.exists(args.voc_dir):
        print('directory not exists:', args.voc_dir)
        sys.exit(1)

    if not osp.exists(osp.join(args.voc_dir, 'class_names.txt')):
        print('need class_names.txt in voc_dir')
        sys.exit(1)
    # build class name list
    for i, line in enumerate(open(osp.join(args.voc_dir, 'class_names.txt'), 'r', encoding='UTF-8').readlines()):
        class_id = i  # starts with -1
        class_name = line.strip()
        if class_id == 0:
            assert class_name == '_background_'
        class_names.append(class_name)

    if osp.exists(osp.join(args.voc_dir, 'SegmentationClassPNG')):
        SEGMENTATION_ON = True
    else:
        SEGMENTATION_ON = False
    if osp.exists(osp.join(args.voc_dir, 'JPEGImages')):
        IMAGE_ON = True
    else:
        IMAGE_ON = False

    set_file = osp.join(args.voc_dir, 'ImageSets', 'Main', args.voc_split + ".txt")
    if not osp.exists(set_file):
        print('directory not exists:', set_file)
        sys.exit(1)
    new_set_file = osp.join(args.voc_dir, 'ImageSets', 'Main',
                            args.voc_split + '_' + args.width + '_' + args.height + '.txt')

    # read origin set
    anno_list = list()
    with open(set_file, "r", encoding='UTF-8') as f_open:
        for Line in f_open:
            base = Line.strip()
            # check image file exist
            image_from = osp.join(args.voc_dir, "JPEGImages", base + ".jpg")  # jpg or png or other pic suffix
            if not osp.exists(image_from):
                print("some thing wrong, file not exists: {}".format(image_from))
                continue
            # print(base)
            anno_list.append(osp.join(args.voc_dir, 'Annotations', base + ".xml"))  # absolute path of file
    print("build anno_list completed. total samples:", len(anno_list))

    # split refer
    width = int(args.width)
    height = int(args.height)
    overlap = 1 - float(args.overlay_ratio)  # transform

    new_set_list = []
    # process every annotation xml
    for i in progressbar.progressbar(range(len(anno_list))):
        file = anno_list[i]
        if not osp.exists(file):
            print("file not exists", file)
            continue
        # get image info
        image = dict()
        doc = xmltodict.parse(open(file).read())
        image['file_name'] = str(doc['annotation']['filename'])
        image['height'] = int(doc['annotation']['size']['height'])
        image['width'] = int(doc['annotation']['size']['width'])
        base = Path(file).stem  # base

        # read image
        if IMAGE_ON:
            data = Image.open(osp.join(args.voc_dir, 'JPEGImages', image['file_name']))
        else:
            data = None
        if SEGMENTATION_ON:
            seg_data = Image.open(
                osp.join(args.voc_dir, 'SegmentationClassPNG', base + '.png'))  # FIXME：change suffix when needed.
        else:
            seg_data = None

        # split region
        regions = list()
        ID = 0
        for x in range(0, image['width'], int(width * overlap)):
            for y in range(0, image['height'], int(height * overlap)):
                if x + width > image['width']:
                    x = image['width'] - width
                if y + height > image['height']:
                    y = image['height'] - height
                region = dict()
                region['base'] = base + '_' + str(width) + '_' + str(height) + '_' + str(ID)
                region['file_name'] = region['base'] + '.jpg'  # with part id
                region['width'] = width
                region['height'] = height
                region['image_from'] = image['file_name']
                region['region_x'] = x
                region['region_y'] = y
                region['objects'] = list()  # store objects inside region

                # 裁剪原图和保存
                if data is not None:
                    region_img = data.crop((x, y, x + width - 1, y + height - 1))
                    region['img_data'] = region_img  # PIL image
                    # region_img.save(osp.join(args.voc_dir, 'JPEGImages', region['file_name']))

                # 裁剪分割图和保存
                if seg_data is not None:
                    region['seg_file'] = region['base'] + '.png'  # with part id
                    region_seg = seg_data.crop((x, y, x + width - 1, y + height - 1))
                    region['seg_data'] = region_seg
                    # region_seg.save(osp.join(args.voc_dir, 'SegmentationClassPNG', region['seg_file']))

                regions.append(region)
                ID += 1  # next part

        # get object info
        if 'object' in doc['annotation']:
            objects = doc['annotation']['object']
            if isinstance(objects, OrderedDict):
                obj = objects
                objects = list()
                objects.append(obj)

            for obj in objects:
                name = obj['name']  # class
                obj_xmin = int(obj["bndbox"]["xmin"])
                obj_ymin = int(obj["bndbox"]["ymin"])
                obj_xmax = int(obj["bndbox"]["xmax"])
                obj_ymax = int(obj["bndbox"]["ymax"])
                # correct wrong box
                obj_xmax = min(obj_xmax, image['width'] - 1)
                obj_ymax = min(obj_ymax, image['height'] - 1)

                # check valid
                if not check_size(obj_xmin, obj_ymin, obj_xmax, obj_ymax, image['width'], image['height']):
                    logging.error("ERROR SOURCE", file)
                    continue

                # iterate every anno
                for region in regions:
                    img_xmin = region['region_x']
                    img_ymin = region['region_y']
                    img_xmax = img_xmin + region['width'] - 1
                    img_ymax = img_ymin + region['height'] - 1

                    # intersection
                    anno_xmin = max(obj_xmin, img_xmin)
                    anno_ymin = max(obj_ymin, img_ymin)
                    anno_xmax = min(obj_xmax, img_xmax)
                    anno_ymax = min(obj_ymax, img_ymax)

                    # check intersect
                    if abs(max(anno_xmax - anno_xmin, 0) * max(anno_ymax - anno_ymin, 0)) == 0:
                        continue  # not intersect

                    # relative object coordinate for region
                    anno_xmin -= region['region_x']
                    anno_ymin -= region['region_y']
                    anno_xmax -= region['region_x']
                    anno_ymax -= region['region_y']

                    # check valid
                    if not check_size(anno_xmin, anno_ymin, anno_xmax, anno_ymax, region['width'], region['height']):
                        logging.error("ERROR REGION", file, img_xmin, img_ymin, img_xmax, img_ymax, obj_xmin, obj_ymin,
                                      obj_xmax, obj_ymax)
                        continue

                    # append to region objects
                    region['objects'].append({'name': name, 'bndbox': (anno_xmin, anno_ymin, anno_xmax, anno_ymax)})

            # save region information to xml after process all objects in origin image
            for region in regions:
                save_voc_annotation(args.voc_dir, region)
                new_set_list.append(region['base'])
    with open(new_set_file, 'w', encoding='UTF-8') as f:
        f.writelines('\n'.join(tuple(new_set_list)))


def check_size(xmin, ymin, xmax, ymax, width, height):
    if xmin >= xmax:
        return False
    if ymin >= ymax:
        return False
    if xmin < 0 or xmin >= width:
        return False
    if ymin < 0 or ymax >= height:
        return False
    return True


def save_voc_annotation(voc_dir, region):
    """
    save region part to xml, reference: labelme_bbox_json2voc.py
    :param voc_dir:
    :param region:
    :return:
    """
    # src image file
    out_img_file = osp.join(voc_dir, 'JPEGImages', region['base'] + '.jpg')
    # annotation xml file
    out_xml_file = osp.join(voc_dir, 'Annotations', region['base'] + '.xml')
    # visualize image file
    out_viz_file = osp.join(voc_dir, 'AnnotationsVisualization', region['base'] + '.jpg')
    # color annotated image file
    out_colorize_file = osp.join(voc_dir, 'AnnotationsVisualization', region['base'] + '_viz.jpg')

    # image data
    img = np.asarray(region['img_data'])
    # save image
    region['img_data'].save(out_img_file)

    # generate voc format annotation file
    maker = lxml.builder.ElementMaker()
    xml = maker.annotation(
        # folder name
        maker.folder(""),
        # img path
        maker.filename(region['base'] + '.jpg'),
        # img source, ignore it
        maker.source(
            maker.database(""),
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

    # two list for visualization
    bboxes = []
    labels = []
    for shape in region['objects']:
        class_name = shape['name']
        class_id = class_names.index(class_name)

        # box info from annotated
        xmin = shape['bndbox'][0]
        ymin = shape['bndbox'][1]
        xmax = shape['bndbox'][2]
        ymax = shape['bndbox'][3]

        # swap if min is larger than max.
        xmin, xmax = sorted([xmin, xmax])
        ymin, ymax = sorted([ymin, ymax])

        bboxes.append([xmin, ymin, xmax, ymax])
        labels.append(class_id)

        xml.append(
            maker.object(  # object info
                maker.name(class_name),  # label name
                maker.pose(""),  # pose info, doesn't matter
                maker.truncated("0"),  # truncated info, doesn't matter
                maker.difficult("0"),  # diificulty, doesn't matter
                maker.bndbox(  # bbox(up-left corner and bottom-right corner points)
                    maker.xmin(str(xmin)),
                    maker.ymin(str(ymin)),
                    maker.xmax(str(xmax)),
                    maker.ymax(str(ymax)),
                ),
            )
        )

    # caption for visualize drawing
    captions = [class_names[l] for l in labels]
    viz = labelme.utils.draw_instances(
        img, bboxes, labels, captions=captions
    )

    PIL.Image.fromarray(viz).save(out_viz_file)

    # another visualize format (colored mask in bbox)
    label_name_to_value = {'_background_': 0}
    for shape in sorted(region['objects'], key=lambda x: x['name']):
        label_name = shape['name']

        if label_name in label_name_to_value:
            label_value = label_name_to_value[label_name]
        else:
            label_value = len(label_name_to_value)
            label_name_to_value[label_name] = label_value

    lbl = shapes_to_label(img.shape, region['objects'], label_name_to_value)
    label_names = [None] * (max(label_name_to_value.values()) + 1)
    for name, value in label_name_to_value.items():
        label_names[value] = name

    lbl_viz = labelme.utils.draw_label(lbl, img, label_names)
    PIL.Image.fromarray(lbl_viz).save(out_colorize_file)

    # save voc annotation to xml file
    with open(out_xml_file, 'wb') as f:
        f.write(lxml.etree.tostring(xml, pretty_print=True))

    if region['seg_data'] is not None:
        out_png_file = osp.join(voc_dir, 'SegmentationClassPNG', region['base'] + '.png')
        region['seg_data'].save(out_png_file)


def shapes_to_label(img_shape, shapes, label_name_to_value):
    """
    override for this region split fuc
    :param img_shape:
    :param shapes:
    :param label_name_to_value:
    :return:
    """
    cls = np.zeros(img_shape[:2], dtype=np.int32)
    for shape in shapes:
        xmin = shape['bndbox'][0]
        ymin = shape['bndbox'][1]
        xmax = shape['bndbox'][2]
        ymax = shape['bndbox'][3]
        points = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]
        label = shape['name']
        shape_type = shape.get('shape_type', None)
        cls_name = label
        cls_id = label_name_to_value[cls_name]
        mask = shape_to_mask(img_shape[:2], points, shape_type)
        cls[mask] = cls_id
    return cls


if __name__ == '__main__':
    main()
