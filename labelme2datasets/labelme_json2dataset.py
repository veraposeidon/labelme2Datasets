"""
brief: covert single json file to single image dataset.

usage：python labelme_json2dataset.py json_file -o output_directory

reference: https://github.com/wkentaro/labelme/blob/main/labelme/cli/json_to_dataset.py
"""

# coding=utf-8

import argparse
import base64
import json
import os
import os.path as osp

import PIL.Image
import imgviz
from labelme import utils
from labelme.logger import logger


def get_data_and_image(json_file):
    """
    get data and image from json file
    :param json_file: json file
    :return: data and image
    """
    with open(json_file, 'rb') as json_f:
        data = json.load(json_f)
        image_data = data.get('imageData')
        if not image_data:
            image_path = os.path.join(os.path.dirname(json_file), data['imagePath'])
            with open(image_path, 'rb') as image_f:
                image_data = image_f.read()
                image_data = base64.b64encode(image_data).decode('utf-8')
        img = utils.img_b64_to_arr(image_data)

        return data, img


def get_label_names(data, image):
    """
    get label names from data and image
    :param data: data
    :param image: image
    :return: label names and lbl
    """
    label_name_to_value = {'_background_': 0}
    for shape in sorted(data['shapes'], key=lambda x: x['label']):
        label_name = shape['label']
        if label_name in label_name_to_value:
            pass
        else:
            label_value = len(label_name_to_value)
            label_name_to_value[label_name] = label_value
    lbl, _ = utils.shapes_to_label(image.shape, data['shapes'], label_name_to_value)

    label_names = [None] * (max(label_name_to_value.values()) + 1)
    for name, value in label_name_to_value.items():
        label_names[value] = name

    return label_names, lbl


def save_image_and_label(image, lbl, output_dir, label_names):
    """
    save image and label to output_dir
    :param image: image
    :param lbl: label
    :param output_dir: output directory
    :param label_names: label names
    :return:
    """
    PIL.Image.fromarray(image).save(osp.join(output_dir, 'img.png'))
    utils.lblsave(osp.join(output_dir, 'label.png'), lbl)
    lbl_viz = imgviz.label2rgb(lbl, imgviz.asgray(image), label_names=label_names, loc="rb")
    PIL.Image.fromarray(lbl_viz).save(osp.join(output_dir, 'label_viz.png'))

    with open(osp.join(output_dir, 'label_names.txt'), 'w', encoding="utf8") as label_f:
        for lbl_name in label_names:
            label_f.write(lbl_name + '\n')

    print(f"Saved to: {output_dir}")


def main():
    """ main """
    logger.warning(
        'This script is aimed to demonstrate how to convert the'
        'JSON file to a single image dataset, and not to handle'
        'multiple JSON files to generate a real-use dataset.'
    )
    logger.warning(
        "It won't handle multiple JSON files to generate a "
        "real-use dataset."
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_file')
    parser.add_argument('--output_dir', default=None)
    args = parser.parse_args()

    json_file = args.json_file

    if args.output_dir is None:
        out_dir = osp.basename(json_file).replace('.', '_')
        out_dir = osp.join(osp.dirname(json_file), out_dir)
    else:
        out_dir = args.output_dir
    if not osp.exists(out_dir):
        os.mkdir(out_dir)

    (data, img) = get_data_and_image(json_file)

    (label_names, lbl) = get_label_names(data, img)

    save_image_and_label(img, lbl, out_dir, label_names)


if __name__ == '__main__':
    main()
