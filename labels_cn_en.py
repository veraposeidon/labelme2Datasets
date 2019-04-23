def en_cn_dict_build(file_name):
    f = open(file_name, 'r', encoding='UTF-8')

    en_cn = []
    for line in f:
        en_cn.append(line.split(','))

    cn_ens = {o[0]: o[1][:-1] for o in en_cn}
    en_cns = {cn_ens[o]: o for o in cn_ens}

    print("构建瑕疵中文名字典完成...")

    return cn_ens, en_cns


if __name__ == '__main__':
    en_cn_dict_build('瑕疵中英文名.txt')
