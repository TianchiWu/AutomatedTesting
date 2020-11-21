from lxml.etree import Element, SubElement, tostring, ElementTree
from lxml import etree
import cv2
import os
if __name__ == '__main__':
    txt_dir = '../../Demo/TXT'
    template_file = '../../Demo/template.xml'
    target_dir = '../../Demo/XML/'
    img_dir = '../../Demo/Img'
    files = os.listdir(txt_dir)

    for file in files:
        img_path = img_dir + '/' + file.replace('.txt','.jpg')
        file_name = file.replace('.txt','')
        f = open(txt_dir + '/' + file)
        line = f.readline()
        # 标注存在data列表里
        datas = []
        while line:
            if line[0] == 'L':
                data = []
                f.readline()
                bounds = f.readline()
                f.readline()
                label = f.readline()
                bounds = bounds[8:-1]
                label = label[5:-1]
                xmin, ymin, xmax, ymax = bounds.replace('[', '').replace(']', '').split(',')
                data.append(label)
                data.append(xmin)
                data.append(ymin)
                data.append(xmax)
                data.append(ymax)
                datas.append(data)
            line = f.readline()

        tree = ElementTree()

        parser = etree.XMLParser(remove_blank_text=True)
        tree.parse(template_file, parser)
        root = tree.getroot()
        root.find('filename').text = file_name

        # size
        sz = root.find('size')
        im = cv2.imread(img_path)

        sz.find('height').text = str(im.shape[0])
        sz.find('width').text = str(im.shape[1])
        sz.find('depth').text = str(im.shape[2])

        flag = 0
        for data in datas:
            label = data[0]
            xmin, ymin, xmax, ymax = data[1], data[2], data[3], data[4]

            # object，首次填充
            if flag == 0:
                obj = root.find('object')
                obj.find('name').text = label
                bb = obj.find('bndbox')
                bb.find('xmin').text = xmin
                bb.find('ymin').text = ymin
                bb.find('xmax').text = xmax
                bb.find('ymax').text = ymax
                flag = 1
            else:
                obj = Element('object')
                name = Element('name')
                name.text = label
                obj.append(name)
                pose = Element('pose')
                pose.text = 'Unspecified'
                obj.append(pose)
                truncated = Element('truncated')
                truncated.text = '0'
                obj.append(truncated)
                difficult = Element('difficult')
                difficult.text = '0'
                obj.append(difficult)

                bb = Element('bndbox')
                xmi = Element('xmin')
                xmi.text = xmin
                ymi = Element('ymin')
                ymi.text = ymin
                xma = Element('xmax')
                xma.text = xmax
                yma = Element('ymax')
                yma.text = ymax
                bb.append(xmi)
                bb.append(ymi)
                bb.append(xma)
                bb.append(yma)
                obj.append(bb)
                root.append(obj)

        xml_file = file_name + '.xml'
        tree.write(target_dir + xml_file, pretty_print=True, encoding='utf-8')
        print(file_name)
    # file_name = str(i) + '.jpg'
    # f = open(txt_dir)
    # line = f.readline()
    # # 标注存在data列表里
    # datas = []
    # while line:
    #     if line[0] == 'L':
    #         data = []
    #         f.readline()
    #         bounds = f.readline()
    #         f.readline()
    #         label = f.readline()
    #         bounds = bounds[8:-1]
    #         label = label[5:-1]
    #         xmin, ymin, xmax, ymax = bounds.replace('[', '').replace(']', '').split(',')
    #         data.append(label)
    #         data.append(xmin)
    #         data.append(ymin)
    #         data.append(xmax)
    #         data.append(ymax)
    #         datas.append(data)
    #     line = f.readline()
    #
    # tree = ElementTree()
    #
    # parser = etree.XMLParser(remove_blank_text=True)
    # tree.parse(template_file, parser)
    # root = tree.getroot()
    # root.find('filename').text = file_name
    #
    # # size
    # sz = root.find('size')
    # im = cv2.imread(img_path)
    #
    # sz.find('height').text = str(im.shape[0])
    # sz.find('width').text = str(im.shape[1])
    # sz.find('depth').text = str(im.shape[2])
    #
    # flag = 0
    # for data in datas:
    #     print(data)
    #     label = data[0]
    #     xmin, ymin, xmax, ymax = data[1], data[2], data[3], data[4]
    #
    #     # object，首次填充
    #     if flag == 0:
    #         obj = root.find('object')
    #         obj.find('name').text = label
    #         bb = obj.find('bndbox')
    #         bb.find('xmin').text = xmin
    #         bb.find('ymin').text = ymin
    #         bb.find('xmax').text = xmax
    #         bb.find('ymax').text = ymax
    #         flag = 1
    #     else:
    #         obj = Element('object')
    #         name = Element('name')
    #         name.text = label
    #         obj.append(name)
    #         pose = Element('pose')
    #         pose.text = 'Unspecified'
    #         obj.append(pose)
    #         truncated = Element('truncated')
    #         truncated.text = '0'
    #         obj.append(truncated)
    #         difficult = Element('difficult')
    #         difficult.text = '0'
    #         obj.append(difficult)
    #
    #         bb = Element('bndbox')
    #         xmi = Element('xmin')
    #         xmi.text = xmin
    #         ymi = Element('ymin')
    #         ymi.text =ymin
    #         xma = Element('xmax')
    #         xma.text = xmax
    #         yma = Element('ymax')
    #         yma.text = ymax
    #         bb.append(xmi)
    #         bb.append(ymi)
    #         bb.append(xma)
    #         bb.append(yma)
    #         obj.append(bb)
    #         root.append(obj)
    #
    # xml_file = file_name.replace('.jpg', '.xml')
    # tree.write(target_dir + xml_file, pretty_print=True, encoding='utf-8')
    # print(i)