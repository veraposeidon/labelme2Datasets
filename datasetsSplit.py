import os
from glob import glob

from sklearn.model_selection import train_test_split

def split_to_train_test(XmlDir, outputDir):

    train_file = outputDir + 'train.txt'
    test_file = outputDir + 'test.txt'

    if os.path.exists(train_file):
        os.remove(train_file)
    if os.path.exists(test_file):
        os.remove(test_file)

    ftrain = open(train_file, 'w')
    ftest = open(test_file, 'w')

    total_files = glob(XmlDir + "*.xml")
    total_files = [file.replace('\\','/') for file in total_files]
    total_files = [i.split("/")[-1].split(".xml")[0] for i in total_files]

    train_files, test_files = train_test_split(total_files, test_size=0.3, random_state=42)

    # train
    for file in train_files:
        ftrain.write(file + "\n")

    # test
    for file in test_files:
        ftest.write(file + "\n")

    ftrain.close()
    ftest.close()

    print("split Completed. Number of Train Samples: {}. Number of Test Samples: {}".format(len(train_files), len(test_files)))


if __name__ == '__main__':
    annotationXmlDir = "E:/Documents/Datasets/AluminiumData/AluminiumVOC/Annotations/"
    outputDir = "E:/Documents/Datasets/AluminiumData/AluminiumVOC/ImageSets/Main/"

    split_to_train_test(annotationXmlDir, outputDir)