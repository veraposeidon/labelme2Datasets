# 过采样：对训练的数据集进行判断，遍历得到
from collections import OrderedDict
from pathlib import Path
import xmltodict
from numpy.random import randint
import random

# 1. 读取训练集
train_txt = Path("E:/Documents/Datasets/AluminumVOC/ImageSets/Main/train.txt")
trainList = []
with train_txt.open() as f:
    for item in f.readlines():
        trainList.append(item)

print(len(trainList))

# 2. 类别字典
clsDict = {}
clsDict['BuDaoDian'] = []
clsDict['CaHua'] = []
clsDict['JiaoWeiLouDi'] = []
clsDict['JuPi'] = []
clsDict['LouDi'] = []
clsDict['PengLiu'] = []
clsDict['QiPao'] = []
clsDict['QiKeng'] = []
clsDict['ZaSe'] = []
clsDict['ZangDian'] = []

xmlPath = Path("E:/Documents/Datasets/AluminumVOC/MultiLabelAnnotations")
for item in trainList:
    name = item.strip()
    xmlName = xmlPath / (name + ".xml")
    # read xml
    doc = xmltodict.parse(open(xmlName).read())
    # obj_list
    if 'object' in doc['annotation']:
        objects = doc['annotation']['object']
        if isinstance(objects, OrderedDict):
            obj = objects
            objects = list()
            objects.append(obj)
    else:
        continue

    for obj in objects:
        cls = obj['name']
        clsDict[cls].append(name)

# get max num
maxClsNum = 0
for key in clsDict.keys():
    print(key, len(clsDict[key]))
    if len(clsDict[key]) > maxClsNum:
        maxClsNum = len(clsDict[key])

# oversampling every class
for key in clsDict.keys():
    lower = 0
    upper = len(clsDict[key])
    print(key, maxClsNum-len(clsDict[key]))
    remain =  maxClsNum-len(clsDict[key])

    indexList = randint(lower, upper, size=remain)
    for index in indexList:
        clsDict[key].append(clsDict[key][index])

# check
for key in clsDict.keys():
    print(key, len(clsDict[key]))

# cat and write to file
totalList = []
for item in clsDict.values():
    totalList.extend(item)
random.shuffle(totalList)

#
new_path = Path("E:/Documents/Datasets/AluminumVOC/ImageSets/Main/train_oversample.txt")
with new_path.open('w') as f:
    for item in totalList:
        f.write(item + "\n")