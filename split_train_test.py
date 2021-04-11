import glob
import time
import math
import random
import cv2
import json
import os

root = './coco_rabbit/'


def split_train_test(img_list,
                     ratio=.1):
    stamp = str(time.strftime("%Y-%m-%d", time.localtime()))
    test_size = math.floor(len(img_list) * ratio)
    test = []
    for i in range(test_size):
        select = random.randint(0, len(img_list) - 1)
        select_img = img_list[select]
        img_list.remove(select_img)
        test.append(select_img)

    train_dir = root + 'train' + stamp
    test_dir = root + 'test' + stamp
    os.mkdir(train_dir)
    os.mkdir(test_dir)
    print('train dir:', train_dir, '\ntest dir:', test_dir)

    dump(img_list, train_dir)
    dump(test, test_dir)


def dump(paths, dir):
    for path in paths:
        img_path = path
        write_img_path = dir + '/' + img_path.split('/')[-1]
        json_path = path[: -3] + 'json'
        write_json_path = dir + '/' + json_path.split('/')[-1]
        print(img_path, '->', write_img_path)
        print(json_path, '->', write_json_path)
        img_file = cv2.imread(img_path)
        json_file = json.load(open(json_path, 'r'))
        cv2.imwrite(write_img_path, img_file)
        json.dump(json_file, open(write_json_path, 'w+'))


if __name__ == '__main__':
    origin_img_list = glob.glob(root + 'rabbitdata/*.png')
    split_train_test(origin_img_list)
