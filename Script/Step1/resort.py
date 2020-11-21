# 图片和json文件重命名排序
import os


def rename(n):
    s = str(n+1)
    s = '0'*(8-len(s)) + s
    return s


if __name__ == '__main__':
    path = '../../Data/ATMobile2020-1'
    files = os.listdir(path)
    index1 = 0
    index2 = 0
    for file in files:
        if file.endswith('.json'):
            src = os.path.join(os.path.abspath(path), file)
            dst = os.path.join(os.path.abspath('../../Data/JSON'), rename(index1) + '.json')
            os.rename(src, dst)
            index1 += 1
        else:
            src = os.path.join(os.path.abspath(path), file)
            dst = os.path.join(os.path.abspath('../../Data/Img'), rename(index2) + '.jpg')
            os.rename(src, dst)
            index2 += 1
        print(file)