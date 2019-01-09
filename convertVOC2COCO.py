import os
import xml.etree.ElementTree as ET
import xmltodict
import json
from xml.dom import minidom
from collections import OrderedDict

def generateVOC2Json(rootDir, xmlFiles, jsonFile):
    attrDict = dict()
    attrDict["categories"] = [{"supercategory": "defect", "id": 1, "name": "BuDaoDian"},
                              {"supercategory": "defect", "id": 2, "name": "CaHua"},
                              {"supercategory": "defect", "id": 3, "name": "JiaoWeiLouDi"},
                              {"supercategory": "defect", "id": 4, "name": "JuPi"},
                              {"supercategory": "defect", "id": 5, "name": "LouDi"},
                              {"supercategory": "defect", "id": 6, "name": "PengLiu"},
                              {"supercategory": "defect", "id": 7, "name": "QiPao"},
                              {"supercategory": "defect", "id": 8, "name": "QiKeng"},
                              {"supercategory": "defect", "id": 9, "name": "ZaSe"},
                              {"supercategory": "defect", "id": 10, "name": "ZangDian"}
                              ]

    images = list()
    annotations = list()
    for root, dirs, files in os.walk(rootDir):
        image_id = 0
        for file in xmlFiles:
            image_id = image_id + 1
            if file in files:
                # image_id = image_id + 1
                annotation_path = os.path.abspath(os.path.join(root, file))

                # tree = ET.parse(annotation_path)#.getroot()
                image = dict()
                doc = xmltodict.parse(open(annotation_path).read())
                image['file_name'] = str(doc['annotation']['filename'])
                image['height'] = int(doc['annotation']['size']['height'])
                image['width'] = int(doc['annotation']['size']['width'])
                image['id'] = image_id
                images.append(image)

                print("File Name: {} and image_id {}".format(file, image_id))

                id1 = 1
                if 'object' in doc['annotation']:
                    objects = doc['annotation']['object']
                    if isinstance(objects, OrderedDict):
                        obj = objects
                        objects = list()
                        objects.append(obj)

                    for obj in objects:
                        for value in attrDict["categories"]:
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
                                annotation["segmentation"] = [[x, y, x, (y + h - 1), (x + w - 1), (y + h - 1), (x + w - 1), y]]
                                annotation["id"] = id1
                                id1 += 1

                                annotations.append(annotation)
                else:
                    print("File: {} doesn't have any object".format(file))
            else:
                print("File: {} not found".format(file))
    attrDict["images"] = images
    attrDict["annotations"] = annotations
    attrDict["type"] = "instances"
    jsonString = json.dumps(attrDict)

    with open(jsonFile, "w") as f:
        f.write(jsonString)

    print("Completed. ")


File = "E:/Documents/Datasets/AluminiumData/AluminiumVOC/ImageSets/Main/test.txt"
# File = "E:/Documents/Datasets/AluminiumData/AluminiumVOC/ImageSets/Main/train.txt"
XMLFiles = list()
with open(File, "r", encoding='UTF-8') as f:
    for line in f:
        fileName = line.strip()
        print(fileName)
        XMLFiles.append(fileName + ".xml")

rootDir = "E:/Documents/Datasets/AluminiumData/AluminiumVOC/Annotations"
jsonFile = "E:/Documents/Datasets/AluminiumData/AluminiumVOC/Annotations/data_test2018.json"
if os.path.exists(jsonFile):
    os.remove(jsonFile)

generateVOC2Json(rootDir, XMLFiles, jsonFile)