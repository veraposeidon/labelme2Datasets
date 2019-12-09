# coding=utf-8

import argparse
import os
import os.path as osp
import glob
from sklearn.model_selection import train_test_split
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('voc_dir', help='input annotated directory')
    parser.add_argument('test_ratio', help='test set ratio', default=0.3)
    parser.add_argument('--random_state', help='random seed ', default=42)
    args = parser.parse_args()

    if not osp.exists(args.voc_dir):
        print('directory not exists:', args.voc_dir)
        sys.exit(1)

    annotationDir = osp.join(args.voc_dir, 'Annotations')
    if not osp.exists(annotationDir):
        print('annotation directory not exists:', annotationDir)
        sys.exit(1)

    outputDir = osp.join(args.voc_dir, 'ImageSets', 'Main')
    if not osp.exists(outputDir):
        os.makedirs(outputDir)

    train_file = osp.join(outputDir, 'train.txt')
    test_file = osp.join(outputDir, 'test.txt')
    if osp.exists(train_file) or osp.exists(test_file):
        print('train.txt: {} exists or \ntest.txt: {} exists,\nplease check!'.format(train_file, test_file))
        sys.exit(1)

    total_files = glob.glob(osp.join(annotationDir, '*.xml'))
    total_files = [Path(o).stem for o in total_files]
    train_set, test_set = train_test_split(total_files, test_size=float(args.test_ratio),
                                           random_state=int(args.random_state))

    f_train = open(train_file, 'w')
    for file in train_set:
        f_train.write(file + "\n")
    f_train.close()

    f_test = open(test_file, 'w')
    for file in test_set:
        f_test.write(file + "\n")
    f_test.close()

    print("split Completed. Number of Train Samples: {}. Number of Test Samples: {}".format(len(train_set),
                                                                                            len(test_set)))


if __name__ == '__main__':
    main()
