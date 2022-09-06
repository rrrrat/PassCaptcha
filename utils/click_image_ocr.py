from io import BytesIO
import ddddocr
from PIL import Image, ImageDraw, ImageFont


class Ddddocr:
    def __init__(self):
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        self.xy_ocr = ddddocr.DdddOcr(det=True, show_ad=False)

    def get_img_xy(self, img):
        click_identify_result = self.ddddocr_click_identify(img, (0, 0, 340, 243))
        img_xy = {}
        for key, xy in click_identify_result.items():
            img_xy[key] = (int((xy[0] + xy[2]) / 2), int((xy[1] + xy[3]) / 2))
        return img_xy

    def ddddocr_identify(self, captcha_bytes):
        return self.ocr.classification(captcha_bytes)

    def draw_img(self, content, xy_list):
        font_type = "./msyhl.ttc"
        font_size = 20
        font = ImageFont.truetype(font_type, font_size)
        # 识别
        img = Image.open(BytesIO(content))
        draw = ImageDraw.Draw(img)
        words = []
        for row in xy_list:
            # 框字
            x1, y1, x2, y2 = row
            draw.line(([(x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)]), width=1, fill="red")
            # 裁剪出单个字
            corp = img.crop(row)
            img_byte = BytesIO()
            corp.save(img_byte, 'png')
            # 识别出单个字
            word = self.ocr.classification(img_byte.getvalue())
            words.append(word)
            # 填字
            y = y1 - 30 if y2 > 300 else y2
            draw.text((int((x1 + x2) / 2), y), word, font=font, fill="red")
        return words

    def ddddocr_click_identify(self, content, crop_size=None):
        img = Image.open(BytesIO(content))
        img = img.resize((340, 243), Image.ANTIALIAS)
        if crop_size:
            img = img.crop(crop_size)
            img_byte = BytesIO()
            img.save(img_byte, 'png')
            content = img_byte.getvalue()
        xy_list = self.xy_ocr.detection(content)
        words = self.draw_img(content, xy_list)
        return dict(zip(words, xy_list))


