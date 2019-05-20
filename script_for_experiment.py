# 脚本 备忘
from pathlib import Path
clsdir = Path("E:/Documents/Datasets/AluminumVOC/Backup/multilabelclassification")
allclsfiles = clsdir.glob("*.xml")
allclsfiles=list(allclsfiles)
len(allclsfiles)

train_obj_file = Path("E:/Documents/Datasets/AluminumVOC/ImageSets/Main/train_obj_1000.txt")
obj_list = []
with train_obj_file.open() as f:
    for line in f.readlines():
        obj_list.append(line)
len(obj_list)

test_list =[]
test_file = Path("E:/Documents/Datasets/AluminumVOC/ImageSets/Main/test.txt")
with test_file.open() as f:
    for line in f.readlines():
        test_list.append(line)
len(test_list)


obj_list = [o.strip() for o in obj_list]
test_list = [o.strip() for o in test_list]
cls_list = []
for item in allclsfiles:
    name = item.stem
    if name in obj_list or name in test_list:
        continue
    else:
        cls_list.append(name)

len(cls_list)

cls_file = Path("E:/Documents/Datasets/AluminumVOC/ImageSets/Main/train_cls_1670.txt")
with cls_file.open('w') as f:
    for item in cls_list:
        f.write(item + "\n")

# 也可以进行查重。