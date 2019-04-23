#!/usr/bin/env python
# 参考来源：labelme examples
# 简介：labelme 标注完一份图像之后得到Json文件，收集该Json文件至一个文件夹，使用本程序转换为VOC格式的数据集。
from __future__ import print_function

import argparse
import glob
import json
import os
import os.path as osp
import re

import lxml.builder
import lxml.etree
import PIL.Image

import labelme
from labelme import utils
from labels_cn_en import en_cn_dict_build  # convert chinese label to english label


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # labels file
    parser.add_argument('labels_file')
    # directory where contains labelme annotated json files
    parser.add_argument('in_dir', help='input dir with annotated files')
    # output directory for dataset
    parser.add_argument('out_dir', help='output dataset directory')
    args = parser.parse_args()

    # 1. Create Directories
    # remove output dir manually when exists
    if osp.exists(args.out_dir):
        print('Output directory already exists:', args.out_dir)
        quit(1)
    # make voc format directories
    os.makedirs(args.out_dir)
    os.makedirs(osp.join(args.out_dir, 'JPEGImages'))
    os.makedirs(osp.join(args.out_dir, 'Annotations'))
    os.makedirs(osp.join(args.out_dir, 'AnnotationsVisualization'))
    print('dataset dir is:', args.out_dir)

    # 2. Get Label Information
    # get labels and save it to dataset dir
    class_names = []
    for i, line in enumerate(open(args.labels_file, 'r', encoding='UTF-8').readlines()):
        class_id = i - 1  # starts with -1
        class_name = line.strip()
        if class_id == -1:
            assert class_name == '__ignore__'
            continue
        elif class_id == 0:
            assert class_name == '_background_'
            class_names.append(class_name)
        else:
            class_names.append(cn2ens[class_name])
    class_names = tuple(class_names)
    print('class_names:', class_names)
    out_class_names_file = osp.join(args.out_dir, 'class_names.txt')  # save labels in txt for information
    with open(out_class_names_file, 'w', encoding='UTF-8') as f:
        f.writelines('\n'.join(class_names))
    print('Saved class_names:', out_class_names_file)

    # 3. Process Every Json File
    for label_file in glob.glob(osp.join(args.in_dir, '*.json')):
        # load json
        print('Generating dataset from:', label_file)
        with open(label_file, 'r', encoding='UTF-8') as f:
            data = json.load(f)

        # regex get img name
        filename = osp.splitext(osp.basename(label_file))[0]
        base = pattern.findall(filename)[0]

        # src image file
        out_img_file = osp.join(
            args.out_dir, 'JPEGImages', base + '.jpg')
        # annotation xml file
        out_xml_file = osp.join(
            args.out_dir, 'Annotations', base + '.xml')
        # visualize image file
        out_viz_file = osp.join(
            args.out_dir, 'AnnotationsVisualization', base + '_Viz.jpg')
        # color annotated image file
        out_colorize_file = osp.join(
            args.out_dir, 'AnnotationsVisualization', base + '_ColorViz.jpg')

        # labelme annotated file contains source image data(serialized)
        # get img data as numpy array
        imgdata = data['imageData']
        img = utils.img_b64_to_arr(imgdata)

        # also you can read image from img path too
        # img_file = osp.join(osp.dirname(label_file), data['imagePath'])
        # img = np.asarray(PIL.Image.open(img_file))

        # save the origin image file
        PIL.Image.fromarray(img).save(out_img_file)

        # lxml is a wonderful xml tool
        # generate voc format annotation file
        maker = lxml.builder.ElementMaker()
        xml = maker.annotation(
            maker.folder(""),   # folder name
            maker.filename(base + '.jpg'),  # img path
            maker.source(  # img source, doesn't matter
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
            class_name = shape['label']     # object name in json file
            class_id = class_names.index(cn2ens[class_name])    # convert to class id

            # box info from annotated points
            xmin = shape['points'][0][0]
            ymin = shape['points'][0][1]
            xmax = shape['points'][2][0]
            ymax = shape['points'][2][1]

            bboxes.append([xmin, ymin, xmax, ymax])
            labels.append(class_id)

            #
            xml.append(
                maker.object(   # object info
                    maker.name(cn2ens[shape['label']]),  # label name(in english)
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
        # save it
        PIL.Image.fromarray(viz).save(out_viz_file)

        # another visualize format (colored mask in bbox)
        # convert label to id
        label_name_to_value = {'背景': 0}
        for shape in sorted(data['shapes'], key=lambda x: x['label']):
            label_name = shape['label']
            if label_name in label_name_to_value:
                label_value = label_name_to_value[label_name]
            else:
                label_value = len(label_name_to_value)
                label_name_to_value[label_name] = label_value
        # labelme's function
        lbl = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value)
        label_names = [None] * (max(label_name_to_value.values()) + 1)
        for name, value in label_name_to_value.items():
            label_names[value] = cn2ens[name]  # annotated in english
        # labelme's function
        lbl_viz = utils.draw_label(lbl, img, label_names)
        # save img
        PIL.Image.fromarray(lbl_viz).save(out_colorize_file)

        # save voc annotation to xml file
        with open(out_xml_file, 'wb') as f:
            f.write(lxml.etree.tostring(xml, pretty_print=True))


if __name__ == '__main__':
    # build a chinese-english label convert dict
    (cn2ens, en2cns) = en_cn_dict_build('瑕疵中英文名.txt')

    # regex pattern(used in get image name)
    pattern = re.compile(r"\d+")  # e.g. use time as file name

    # begin
    main()
