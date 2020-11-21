import os
from PIL import Image

if __name__ == '__main__':
    path = '../../Data/Img'
    files = os.listdir(path)
    for file in files:
        img = Image.open(path + '/' + file)
        re = img.resize((1440, 2560))
        re.save(('../Demo/Img/0000') + file)
        print(file)