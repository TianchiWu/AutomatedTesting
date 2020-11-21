from PIL import Image
import os


def getName(line):
    # name = line[13:-1].replace('.','_').replace(':','_').replace('/','_')
    name = line[5:-1]
    return name


def getBounds(line):
    line = line[8:-1]
    s = line.replace('[', '').replace(']', '')
    bounds = list(map(int, s.split(',')))
    return bounds


def imgCrop(img, path, name, bounds):
    path += "/" + name + ".jpg"
    cropped = img.crop((bounds[0], bounds[1], bounds[2], bounds[3]))
    cropped.save(path)


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


# 根据控件裁剪
def crop_all(txt_path, img_path, output_path, NO):
    # output_path ../Data/ImgCropped/NO
    f = open(txt_path)
    line = f.readline()

    img = Image.open(img_path)
    img_re = img.resize((1440, 2560))
    #######################
    # 测试专用
    #######################
    # dir_path = output_path + '/_' + str(NO)
    dir_path = output_path + '/' + str(NO)
    mkdir(dir_path)
    img_re.save(dir_path + '/' + str(NO) + '.jpg')

    i = 1
    while line:
        if (line[0] == 'L'):
            line1 = f.readline()  # class
            line2 = f.readline()  # bounds
            line3 = f.readline()  # resource-id
            line4 = f.readline()  # tag
            name = getName(line4)
            bounds = getBounds(line2)
            imgCrop(img_re, dir_path, 'Pic' + str(i) + '_' + line[0:-1] + '_' + name, bounds)
            i += 1
        line = f.readline()

    f.close()


if __name__ == '__main__':
    # txt_path = "../Demo/"
    # img_path = "../Data/ATMobile2020-1/"
    # output_path = "../Data/ImgCropped"
    # for i in range(1, 10):
    # i = 1
    # txt_path = "../Demo/" + str(i) + "_.TXT"
    # txt_path = "../../Demo/" + str(i) + ".TXT"
    # img_path = "../../Data/ATMobile2020-1/" + str(i) + ".jpg"
    # crop_all(txt_path, img_path, output_path, i)

    img_path = '../Demo/Img/00000001.jpg'
    name = '00000001'
    bounds = [114, 2385, 1328, 2519]
    img = Image.open(img_path)
    path = '../Demo'
    imgCrop(img, path, name, bounds)
