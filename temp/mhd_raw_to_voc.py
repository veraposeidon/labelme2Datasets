import os
import sys
import numpy as np
import pandas as pd
import SimpleITK as sitk
import matplotlib.pyplot as plt
import lxml.builder
import lxml.etree
from PIL import Image
import labelme
from pathlib import Path
from tqdm import tqdm

# 标签
label_dict = {}
label_dict[1] = 'nodule'
label_dict[5] = 'stripe'
label_dict[31] = 'artery'
label_dict[32] = 'lymph'

anns_path = os.path.abspath('E:/Documents/Datasets/2019CT/chestCT_round1_annotation.csv')
anns_all = pd.read_csv(anns_path, engine='python')

train_dir = Path('E:/Documents/Datasets/2019CT/chestCT_round1_train')
mhds = list(train_dir.glob("*.mhd"))
ids = [o.stem for o in mhds]

JPGS = train_dir / "VOC" / "JPGS"
ANNOS = train_dir / "VOC" / "ANNOS"
VIZ = train_dir / "VOC" / "VIZ"


def load_itk(file_name, file_path):
    '''
    modified from https://stackoverflow.com/questions/37290631/reading-mhd-raw-format-in-python
    '''

    # Reads the image using SimpleITK
    file = os.path.join(file_path, file_name + '.mhd')
    itkimage = sitk.ReadImage(file)

    # Convert the image to a  numpy array first and then shuffle the dimensions to get axis in the order z,y,x
    ct_scan = sitk.GetArrayFromImage(itkimage)

    # Read the origin of the ct_scan, will be used to convert the coordinates from world to voxel and vice versa.
    origin = np.array(list(reversed(itkimage.GetOrigin())))

    # Read the spacing along each dimension
    spacing = np.array(list(reversed(itkimage.GetSpacing())))

    return ct_scan, origin, spacing


def plot_scan(seriesuid, anns_all, file_path, plot_path='./visualization/',
              clipmin=-1000, clipmax=600, only_df=False, return_ct=False):
    '''
    input:
    seriesuid: specify the scan plotted.
    anns_all:  the annotation provided (Dataframe).
    file_path: the path of the data.
    plot_path: the path of the visualization, default: make a subdirectory under the current dir.
    clip_min:  the lower boundary which is used for clipping the CT valued for the lung window.
    clip_max:  the upper boundary which is used for clipping the CT valued for the lung window.
    only_df:   if True, only return the dataframe , and do not plot.
    return_ct: if True, return the dataframe with the ct array.

    return:
    ann_df:    return the annotation dataframe according to the seriesuid

    Mediastinum window: clipmin=-150, clipmax=250
    '''
    seriesuid = str(seriesuid)
    ann_df = anns_all.query('seriesuid == "%s"' % seriesuid).copy()
    ct, origin, spacing = load_itk(file_name=seriesuid, file_path=file_path)
    ct_clip = ct.clip(min=clipmin, max=clipmax)

    # coordinate transform: world to voxel
    ann_df.coordX = (ann_df.coordX - origin[2]) / spacing[2]
    ann_df.coordY = (ann_df.coordY - origin[1]) / spacing[1]
    ann_df.coordZ = (ann_df.coordZ - origin[0]) / spacing[0]

    ann_df.diameterX = ann_df.diameterX / spacing[2]
    ann_df.diameterY = ann_df.diameterY / spacing[1]
    ann_df.diameterZ = ann_df.diameterZ / spacing[0]

    ann_df['labelstr'] = ann_df.label.apply(lambda x: label_dict[x])

    # 没有标注就保存图像
    if ann_df.shape[0] == 0:
        print('no annoatation')
        # for num in tqdm(range(ct_clip.shape[0])):
        #     # 图像名称
        #     base = str(seriesuid) + "_" + str(num)
        #
        #     # 图像数据和保存
        #     data = ct_clip[num]
        #     out_img_file = base + ".npy"
        #     imgdata.save(out_img_file)
        del ct
        return

    for num in tqdm(range(ct_clip.shape[0])):
        # 图像名称
        base = str(seriesuid) + "_" + str(num)
        out_npy_file = JPGS / (base + ".npy")
        out_npy_file = str(out_npy_file)
        out_img_file = JPGS / (base + ".png")
        out_img_file = str(out_img_file)
        out_xml_file = ANNOS / (base + ".xml")
        out_xml_file = str(out_xml_file)
        out_viz_file = VIZ / (base + ".jpg")
        out_viz_file = str(out_viz_file)

        # 图像数据和保存
        data = ct_clip[num]
        np.save(out_npy_file, data)

        img_data = (data - data.min()) / (data.max() - data.min()) * 255
        img_data = img_data.astype(np.uint8)
        Image.fromarray(img_data).save(out_img_file)

        # 标注XML
        maker = lxml.builder.ElementMaker()
        xml = maker.annotation(
            maker.folder(""),  # folder name
            maker.filename(base + '.npy'),  # img path
            maker.source(  # img source, doesn't matter
                maker.database(""),
                maker.annotation(""),
                maker.image(""),
            ),
            maker.size(  # image size(height, width and channel)
                maker.height(str(img_data.shape[0])),
                maker.width(str(img_data.shape[1])),
                maker.depth(str(1)),
            ),
            maker.segmented("0"),  # if for segmentation
        )

        bboxes = []
        labels = []
        for _, ann in ann_df.iterrows():
            x, y, z, w, h, d = ann.coordX, ann.coordY, ann.coordZ, ann.diameterX, ann.diameterY, ann.diameterZ

            if num > z - d / 2 and num < z + d / 2:
                # box info from annotated points
                xmin = int(x - w / 2)
                ymin = int(y - h / 2)
                xmax = int(x + w / 2)
                ymax = int(y + h / 2)

                bboxes.append([xmin, ymin, xmax, ymax])
                labels.append(ann.label)

                xml.append(
                    maker.object(  # object info
                        maker.name(label_dict[ann.label]),  # label name(in english)
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
        # save voc annotation to xml file
        with open(out_xml_file, 'wb') as f:
            f.write(lxml.etree.tostring(xml, pretty_print=True))

        # caption for visualize drawing
        # 受彩色影响，需要三维图
        rgb = np.repeat(img_data[:,:, np.newaxis], 3, axis=2)

        if bboxes is not None:
            captions = [label_dict[l] for l in labels]
            viz = labelme.utils.draw_instances(
                rgb, bboxes, labels, captions=captions
            )
            # save it
            Image.fromarray(viz).save(out_viz_file)

    del ct


for seriesuid in ids:
    plot_scan(seriesuid, anns_all, train_dir)
