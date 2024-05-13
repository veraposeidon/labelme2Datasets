# coding=utf-8
"""splitting voc format datasets into training set and test set"""


import argparse
import sys
import os
import os.path as osp
import glob
from pathlib import Path
from sklearn.model_selection import train_test_split


def main():
    """splitting voc format datasets into training set and test set"""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--voc_dir', help='input annotated directory')
    parser.add_argument('--test_ratio', help='test set ratio', default=0.3)
    parser.add_argument('--random_seed', help='random seed ', default=42)
    args = parser.parse_args()

    if not osp.exists(args.voc_dir):
        print('directory not exists:', args.voc_dir)
        sys.exit(1)

    annotation_dir = osp.join(args.voc_dir, 'Annotations')
    if not osp.exists(annotation_dir):
        print('annotation directory not exists:', annotation_dir)
        sys.exit(1)

    output_dir = osp.join(args.voc_dir, 'ImageSets', 'Main')
    if not osp.exists(output_dir):
        os.makedirs(output_dir)

    train_file = osp.join(output_dir, 'train.txt')
    test_file = osp.join(output_dir, 'test.txt')
    if osp.exists(train_file) or osp.exists(test_file):
        print(f'train.txt: {train_file} exists or test.txt: {train_file} exists,please check!')
        sys.exit(1)

    total_files = glob.glob(osp.join(annotation_dir, '*.xml'))
    total_files = [Path(o).stem for o in total_files]
    train_set, test_set = train_test_split(total_files,
                                           test_size=float(args.test_ratio),
                                           random_state=int(args.random_seed))

    with open(train_file, 'w', encoding='utf8') as train_f:
        for file in train_set:
            train_f.write(file + "\n")

    with open(test_file, 'w', encoding='utf8') as test_f:
        for file in test_set:
            test_f.write(file + "\n")

    print(f"split Completed. Number of Train Samples: {len(train_set)}."
          f" Number of Test Samples: {len(test_set)}")


if __name__ == '__main__':
    main()
