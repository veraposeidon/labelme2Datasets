# coding=utf-8

from __future__ import print_function

import argparse
import glob
import json
import os
import os.path as osp
import re
import sys

try:
    import lxml.builder
    import lxml.etree
except ImportError:
    print('Please install lxml:\n\n    pip install lxml\n')
    sys.exit(1)

import numpy as np
import PIL.Image
import progressbar
import labelme
from labelme import utils
from utils import label_name_convert_dict_build

# regex for get base name
pattern = re.compile(r"\d+")  # e.g. '擦花20180830172530对照样本.jpg' -> '20180830172530'


# labelme 标注完一份图像之后得到Json文件，收集该Json文件至一个文件夹，使用本程序转换为VOC格式的数据集。
# reference: https://github.com/wkentaro/labelme/blob/master/examples/bbox_detection/labelme2voc.py
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_dir', help='input annotated directory')
    parser.add_argument('output_dir', help='output dataset directory')
    parser.add_argument('--labels', help='labels file', required=True)
    parser.add_argument('--label_dict', help='convert label with dict')
    args = parser.parse_args()

    # make voc format directories
    if osp.exists(args.output_dir):
        print('Output directory already exists:', args.output_dir)
        sys.exit(1)
    os.makedirs(args.output_dir)
    os.makedirs(osp.join(args.output_dir, 'JPEGImages'))
    os.makedirs(osp.join(args.output_dir, 'Annotations'))
    os.makedirs(osp.join(args.output_dir, 'AnnotationsVisualization'))
    print('Creating dataset:', args.output_dir)

    # build convert dict
    if args.label_dict is not None:
        fst2snd_dict = label_name_convert_dict_build(args.label_dict)

    # get labels and save it to dataset dir
    class_names = []
    for i, line in enumerate(open(args.labels, 'r', encoding='UTF-8').readlines()):
        class_id = i - 1  # starts with -1
        class_name = line.strip()
        if class_id == -1:
            assert class_name == '__ignore__'
            continue
        elif class_id == 0:
            assert class_name == '_background_'

        if args.label_dict is not None:
            class_name = fst2snd_dict[class_name]
        class_names.append(class_name)
    class_names = tuple(class_names)
    print('class_names:', class_names)
    out_class_names_file = osp.join(args.output_dir, 'class_names.txt')  # save labels in txt for information
    with open(out_class_names_file, 'w', encoding='UTF-8') as f:
        f.writelines('\n'.join(class_names))
    print('Saved class_names:', out_class_names_file)

    label_file_list = glob.glob(osp.join(args.input_dir, '*.json'))
    for i in progressbar.progressbar(range(len(label_file_list))):
        label_file = label_file_list[i]
        # print('Generating dataset from:', label_file)
        with open(label_file, 'r', encoding='UTF-8') as f:
            data = json.load(f)

        # regex: get image name
        filename = osp.splitext(osp.basename(label_file))[0]
        base = pattern.findall(filename)[0]  # TODO: you can change it here: design a method for sample name,
        # TODO: or just use file name.
        # base = osp.splitext(osp.basename(label_file))[0]

        # src image file
        out_img_file = osp.join(
            args.output_dir, 'JPEGImages', base + '.jpg')
        # annotation xml file
        out_xml_file = osp.join(
            args.output_dir, 'Annotations', base + '.xml')
        # visualize image file
        out_viz_file = osp.join(
            args.output_dir, 'AnnotationsVisualization', base + '.jpg')
        # color annotated image file
        out_colorize_file = osp.join(
            args.output_dir, 'AnnotationsVisualization', base + '_viz.jpg')

        # save source image
        imageData = data.get('imageData')  # labelme annotated file contains source image data(serialized)
        if imageData:
            img = utils.img_b64_to_arr(imageData)
        else:
            img_file = osp.join(osp.dirname(label_file), data['imagePath'])
            img = np.asarray(PIL.Image.open(img_file))
        PIL.Image.fromarray(img).save(out_img_file)

        # generate voc format annotation file
        maker = lxml.builder.ElementMaker()
        xml = maker.annotation(
            # folder name
            maker.folder(""),
            # img path
            maker.filename(base + '.jpg'),
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
        for shape in data['shapes']:
            # TODO: change it for annotation shape type, some use points, some use rectangle. Here shows the points one.
            class_name = shape['label']  # object name in json file
            if args.label_dict is not None:
                class_name = fst2snd_dict[class_name]

            class_id = class_names.index(class_name)  # convert to class id

            # box info from annotated points
            # 注意⚠️：大家确认下自己使用的数据中 获取BBOX的方式正不正确。是否需要调整下标。
            xmin = shape['points'][0][0]
            ymin = shape['points'][0][1]
            xmax = shape['points'][2][0]
            ymax = shape['points'][2][1]

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
        for shape in sorted(data['shapes'], key=lambda x: x['label']):
            label_name = shape['label']

            if label_name in label_name_to_value:
                label_value = label_name_to_value[label_name]
            else:
                label_value = len(label_name_to_value)
                label_name_to_value[label_name] = label_value

        lbl = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value)
        label_names = [None] * (max(label_name_to_value.values()) + 1)
        for name, value in label_name_to_value.items():
            if args.label_dict is not None:
                name = fst2snd_dict[name]
            label_names[value] = name

        lbl_viz = utils.draw_label(lbl, img, label_names)
        PIL.Image.fromarray(lbl_viz).save(out_colorize_file)

        # save voc annotation to xml file
        with open(out_xml_file, 'wb') as f:
            f.write(lxml.etree.tostring(xml, pretty_print=True))


if __name__ == '__main__':
    main()
