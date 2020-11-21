import json
import os
import sys
from PIL import Image


class Icon:

    def __init__(self, level, property, id, bounds):
        self.level = level
        self.property = property
        self.id = id
        self.bounds = bounds
        self.tag = ""

    def set_tag(self, tag):
        self.tag = tag


# tag 有优先级
keywords = {'NavigationBar': 0, 'Header': 1, 'Button': 2, 'Picker': 2, 'StatusBar': 3, 'Video': 3, 'Image': 4,
            'Text': 5, 'Bar': 5, 'View': 6, 'Seperator': 6}
icons = []

square = 1440 * 2560


def search(node, lv):
    # child层数
    level = 'L' + str(lv)
    for li in node:
        if 'resource-id' in li:
            id = li['resource-id']
            index = id.find('id/')
            id = id[index:]
            icon_child = Icon(level, li['class'], id, li['bounds'])
            icon_child.set_tag("View")
        else:
            icon_child = Icon(level, li['class'], "NULL", li['bounds'])
        if not filter_bounds(icon_child.bounds):
            flag = filter_redundancy(icon_child)
            if flag == 0:
                icons.append(icon_child)
        if 'children' in li:
            search(li['children'], lv + 1)


# 剔除不能截图的控件
def filter_bounds(bounds):
    return bounds[0] == bounds[2] or bounds[1] == bounds[3] \
           or bounds[0] < 0 or bounds[0] > 1440 or bounds[1] < 0 or bounds[1] > 2560 \
           or bounds[2] < 0 or bounds[2] > 1440 or bounds[3] < 0 or bounds[3] > 2560


# 删除冗余控件
def filter_redundancy(child):
    flag = 0
    for icon in icons:
        if icon.bounds == child.bounds and icon.property == child.property:
            # s1 = icon.property
            # s2 = child.property
            # 取两个字符串的最大子串
            flag = 1
            break
    return flag


def get_icons(path):
    f = open(path, encoding='utf-8')
    data = json.load(f)

    # 找到root，把root控件信息存储到icons中
    node = data['activity']['root']
    root = Icon("L0", node['class'], "NULL", node['bounds'])
    if not filter_bounds(root.bounds):
        icons.append(root)

    if 'children' in node:
        search(node['children'], 1)
    f.close()


def write_file(path):
    f = open(path, 'w')
    for icon in icons:
        f.write(icon.level + '\n')
        f.write("class: ")
        f.write(icon.property + '\n')
        f.write("bounds: ")
        f.write(str(icon.bounds) + '\n')
        f.write("resource-id: ")
        f.write(icon.id + '\n')
        f.write("tag: ")
        f.write(icon.tag + '\n\n')


# 剔除resource-id为NULL的控件
def filter_id():
    li = [x for x in icons if x.id != 'NULL']
    return li


def tag_judge_class(tags, property):
    if "Layout" in property:
        tags.append("View")
    if "View" in property:
        tags.append("View")
    if "Button" in property:
        tags.append("Button")
    if "Text" in property:
        tags.append("Text")
    if "Image" in property:
        tags.append("Image")
    if "Video" in property:
        tags.append("Video")
    if "ActionBar" in property:
        tags.append("NavigationBar")
    if "Progress" in property:
        tags.append("Bar")
    if "Bar" in property:
        tags.append("Bar")
    tags.append("View")
    return tags


def tag_judge_id(tags, id):
    if "navigationBar" in id:
        tags.append("NavigationBar")
    if "action_bar" in id:
        tags.append("NavigationBar")
    if "header" in id:
        tags.append("Header")
    if "statusBar" in id:
        tags.append("StatusBar")
    if "content" in id:
        tags.append("View")
    if "button" in id:
        tags.append("Button")
    if "Panel" in id:
        tags.append("View")
    if "picker" in id:
        tags.append("Picker")
    if "video" in id:
        tags.append("Video")
    if "ads" in id:
        tags.append("Button")
    if "progress" in id:
        tags.append("Bar")
    if "bar" in id:
        tags.append("Bar")
    if "TXT" in id:
        tags.append("Text")
    if "Seperator" in id:
        tags.append("Seperator")
    tags.append("View")
    return tags


# 给控件打上标记
def setTag():
    for icon in icons:
        id = icon.id
        property = icon.property
        tags = []
        tags = tag_judge_id(tags, id)
        tags = tag_judge_class(tags, property)
        tag = ""
        priority = sys.maxsize
        for item in tags:
            if keywords[item] < priority:
                tag = item
                priority = keywords[item]
        if keywords[tag] < keywords[icon.tag]:
            icon.set_tag(tag)
        if "Seperator" in tags:
            icon.set_tag("View")


def filter_same_icon():
    res = []
    flag = 1
    for item in icons:
        if len(res) == 0:
            res.append(item)
        else:
            for icon in res:
                if icon.bounds == item.bounds:
                    tag_item = item.tag
                    flag = 0
                    if keywords[tag_item] <= keywords[icon.tag]:
                        icon.tag = tag_item
                else:
                    flag = 1
            if flag == 1:
                res.append(item)

    return res


# 返回 x, y, width, length
def rec_trans(a):
    return [(a[0] + a[2]) / 2, (a[1] + a[3]) / 2, a[2] - a[0], a[3] - a[1]]


# 相邻在同一级别的控件如果tag相同可以合并
# 现在还有问题，要给一定的宽泛
def combine_neighbour():
    save = []
    res = []
    for icon in icons:
        flag = 0
        for el in save:
            if icon.tag == el.tag and icon.level == el.level and icon.tag != "Button":
                bounds1 = icon.bounds
                bounds2 = el.bounds
                rec1 = rec_trans(bounds1)
                rec2 = rec_trans(bounds2)
                x_dis = abs(rec1[0] - rec2[0]) - (rec1[2] + rec2[2]) / 2
                y_dis = abs(rec1[1] - rec2[1]) - (rec1[3] + rec2[3]) / 2
                # 搭到1/3的边
                if abs(x_dis) <= 35 and y_dis + (rec1[3] + rec2[3]) / 6 <= 0 or abs(y_dis) <= 35 and x_dis + (
                        rec1[2] + rec2[2]) / 6 <= 0:
                    flag = 1
                    bounds = [min(bounds1[0], bounds2[0]), min(bounds1[1], bounds2[1]),
                              max(bounds1[2], bounds2[2]), max(bounds1[3], bounds2[3])]
                    icon.bounds = bounds
                    res.append(icon)
                    save.remove(el)
                    break
        if flag == 0:
            save.append(icon)
    for item in save:
        res.append(item)
    return res


# 删除button包含的其他子项目
def filter_button_contain():
    buttons = []
    for item in icons:
        if item.tag == "Button":
            buttons.append(item)
    for icon in icons:
        if keywords[icon.tag] >= 5 and icon.tag != 'Text':
            for btn in buttons:
                bounds1 = btn.bounds
                bounds2 = icon.bounds
                if bounds1[0] <= bounds2[0] and bounds1[1] <= bounds2[1] \
                        and bounds1[2] >= bounds2[2] and bounds1[3] >= bounds2[3]:
                    icons.remove(icon)
                    break


# 删除只有一种颜色的控件
def filter_1clr(img_path):
    img = Image.open(img_path)
    img = img.resize((1440, 2560))
    res = []
    for icon in icons:
        bounds = icon.bounds
        cropped = img.crop((bounds[0], bounds[1], bounds[2], bounds[3]))
        extrema = cropped.convert("L").getextrema()
        if extrema is not None:
            if extrema[0] != extrema[1]:
                res.append(icon)
    return res


# 错误标注bar的情况
def correct_bar():
    for icon in icons:
        if "Bar" in icon.tag:
            width = icon.bounds[2] - icon.bounds[0]
            height = icon.bounds[3] - icon.bounds[1]
            if width * height / square > 0.75:
                icon.set_tag("View")


# view控件删除
def filter_view():
    res = []
    for icon in icons:
        if icon.tag != "View":
            res.append(icon)
    return res


if __name__ == '__main__':
    # 文件夹路径
    # dir_path = '../../Data/JSON'
    # files = os.listdir(dir_path)
    # for file in files:
    #     name = file
    #     icons = []
    #     iPath = '../../Data/JSON/' + name
    #     # oPath = '../Demo/' + str(i) + '_.TXT'
    #     oPath = '../../Demo/TXT/' + name.replace('.json','.txt')
    #     img_path = '../../Data/Img/' + name.replace('.json', '.jpg')
    #     get_icons(iPath)
    #     icons = filter_id()
    #     setTag()
    #     correct_bar()
    #     icons = filter_same_icon()
    #     length1 = len(icons)
    #     # 合并
    #     while 1:
    #         icons = combine_neighbour()
    #         length2 = len(icons)
    #         if length1 == length2:
    #             break
    #         else:
    #             length1 = length2
    #
    #     filter_button_contain()
    #     icons = filter_1clr(img_path)
    #     icons = filter_view()
    #     write_file(oPath)
    #     print("文件" + name + " 控件数量： ", len(icons))

    i = 1
    icons = []
    iPath = '../../Data/JSON/00000001.json'
    # oPath = '../Demo/' + str(i) + '_.TXT'
    oPath = '../../Demo/00000001.TXT'
    img_path = '../../Data/Img/00000001.jpg'
    get_icons(iPath)
    icons = filter_id()
    setTag()
    correct_bar()
    icons = filter_same_icon()
    length1 = len(icons)
    # 合并
    while 1:
        icons = combine_neighbour()
        length2 = len(icons)
        if length1 == length2:
            break
        else:
            length1 = length2

    filter_button_contain()
    icons = filter_1clr(img_path)
    icons = filter_view()
    write_file(oPath)
    print("文件" + str(i) + " 控件数量： ", len(icons))
