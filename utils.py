# coding=utf-8

# 自定义标签转换，例如将中文便签转换为英文标签。
def label_name_convert_dict_build(dict_file):
    f = open(dict_file, 'r', encoding='UTF-8')

    fst2snd = []
    for line in f:
        fst2snd.append(line.split(','))

    fst2snd_dict = {o[0]: o[1][:-1] for o in fst2snd}
    # snd2fst_dict = {fst2snd_dict[o]: o for o in fst2snd_dict}

    print("dict build complete!")
    return fst2snd_dict

