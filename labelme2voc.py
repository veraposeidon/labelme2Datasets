#!/usr/bin/env python
# 参考来源：labelme examples
from __future__ import print_function

import argparse
import glob
import json
import os
import os.path as osp

import lxml.builder
import lxml.etree
import numpy as np
import PIL.Image

import labelme
from labelme import utils
from buildNameDict import en_cn_dict_build  # 处理中英文转换
import re  # 处理字符串数字提取


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('labels_file')
    parser.add_argument('in_dir', help='input dir with annotated files')
    parser.add_argument('out_dir', help='output dataset directory')
    args = parser.parse_args()


    # 创建PASCAL格式数据集文件夹
    if osp.exists(args.out_dir):
        print('Output directory already exists:', args.out_dir)
        quit(1)
    os.makedirs(args.out_dir)
    os.makedirs(osp.join(args.out_dir, 'JPEGImages'))
    os.makedirs(osp.join(args.out_dir, 'Annotations'))
    os.makedirs(osp.join(args.out_dir, 'AnnotationsVisualization'))
    print('Creating dataset:', args.out_dir)

    # 整理类型名称,就保存成英文吧
    class_names = []
    class_name_to_id = {}
    for i, line in enumerate(open(args.labels_file, 'r', encoding='UTF-8').readlines()):
        class_id = i - 1  # starts with -1
        class_name = line.strip()
        class_name_to_id[class_name] = class_id
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
    out_class_names_file = osp.join(args.out_dir, 'class_names.txt')
    with open(out_class_names_file, 'w', encoding='UTF-8') as f:
        f.writelines('\n'.join(class_names))
    print('Saved class_names:', out_class_names_file)


    # 开始整理每个Json
    for label_file in glob.glob(osp.join(args.in_dir, '*.json')):
        print('Generating dataset from:', label_file)
        with open(label_file, 'r', encoding='UTF-8') as f:
            data = json.load(f)
        filename = osp.splitext(osp.basename(label_file))[0]
        base = pattern.findall(filename)[0]
        out_img_file = osp.join(
            args.out_dir, 'JPEGImages', base + '.jpg')
        out_xml_file = osp.join(
            args.out_dir, 'Annotations', base + '.xml')
        out_viz_file = osp.join(
            args.out_dir, 'AnnotationsVisualization', base + '_Viz.jpg')
        out_Colorviz_file = osp.join(
            args.out_dir, 'AnnotationsVisualization', base + '_ColorViz.jpg')

        # 此处用json自带的图像数据来保存图像
        imageData = data['imageData']
        img = utils.img_b64_to_arr(imageData)

        # img_file = osp.join(osp.dirname(label_file), data['imagePath'])
        # img = np.asarray(PIL.Image.open(img_file))

        # 保存原始图片
        PIL.Image.fromarray(img).save(out_img_file)

        maker = lxml.builder.ElementMaker()
        xml = maker.annotation(
            maker.folder(""),                   # 文件夹
            maker.filename(base + '.jpg'),      # 文件名
            maker.source(                       # 图像来源
                maker.database(""),
                maker.annotation(""),
                maker.image(""),
            ),
            maker.size(                         # 图像尺寸（长宽以及通道数）
                maker.height(str(img.shape[0])),
                maker.width(str(img.shape[1])),
                maker.depth(str(img.shape[2])),
            ),
            maker.segmented("0"),               # 是否用于分割
        )

        bboxes = []
        labels = []
        for shape in data['shapes']:
            # # 原有标记中并不存在shape_type方式，都是rectangle形式
            # if shape['shape_type'] != 'rectangle':
            #     print('Skipping shape: label={label}, shape_type={shape_type}'
            #           .format(**shape))
            #     continue

            class_name = shape['label']
            class_id = class_names.index(cn2ens[class_name])

            xmin = shape['points'][0][0]
            ymin = shape['points'][0][1]
            xmax = shape['points'][2][0]
            ymax = shape['points'][2][1]

            bboxes.append([xmin, ymin, xmax, ymax])
            labels.append(class_id)

            xml.append(
                maker.object(                               # 目标对象
                    maker.name(cn2ens[shape['label']]),     # 分类
                    maker.pose(""),                         # 拍摄角度
                    maker.truncated("0"),                   # 是否截断
                    maker.difficult("0"),                   # 识别难度
                    maker.bndbox(                           # bbox左上角和右下角xy坐标
                        maker.xmin(str(xmin)),
                        maker.ymin(str(ymin)),
                        maker.xmax(str(xmax)),
                        maker.ymax(str(ymax)),
                    ),
                )
            )

        captions = [class_names[l] for l in labels]
        viz = labelme.utils.draw_instances(
            img, bboxes, labels, captions=captions
        )
        PIL.Image.fromarray(viz).save(out_viz_file)

        # 另一种可视化方式，每种缺陷一种颜色
        label_name_to_value = {'背景': 0}
        for shape in sorted(data['shapes'], key=lambda x: x['label']):
            label_name =shape['label']
            if label_name in label_name_to_value:
                label_value = label_name_to_value[label_name]
            else:
                label_value = len(label_name_to_value)
                label_name_to_value[label_name] = label_value
        lbl = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value)
        label_names = [None] * (max(label_name_to_value.values()) + 1)
        for name, value in label_name_to_value.items():
            label_names[value] = cn2ens[name]  # 图注用英文
        lbl_viz = utils.draw_label(lbl, img, label_names)
        PIL.Image.fromarray(lbl_viz).save(out_Colorviz_file)

        # 保存标注文件XML
        with open(out_xml_file, 'wb') as f:
            f.write(lxml.etree.tostring(xml, pretty_print=True))


if __name__ == '__main__':
    (cn2ens, en2cns) = en_cn_dict_build('瑕疵中英文名.txt')

    # 正则表达式处理json的文件名，结果作为图像和标注文件名
    pattern = re.compile(r"\d+")    # e.g. 用时间作为文件名

    main()
