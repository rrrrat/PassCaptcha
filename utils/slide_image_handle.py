from PIL import Image
import os

current_path = os.path.dirname(__file__)


def del_background(img_addr):
    pic = Image.open(img_addr)
    pic = pic.convert('RGBA')
    width, height = pic.size
    array = pic.load()
    for i in range(width):
        for j in range(height):
            pos = array[i, j]
            isEdit = (sum([1 for x in pos[0:3] if x > 240]) == 3)
            if isEdit:
                array[i, j] = (255, 255, 255, 0)
    pic.save(img_addr)
