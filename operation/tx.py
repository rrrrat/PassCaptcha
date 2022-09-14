import re
import time
import os

import ddddocr
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

if os.path.dirname(__file__) != (os.getcwd() + "\\operation"):
    from ..utils import click_image_ocr, slide_image_handle
    from ..handle import selenium_options
    from ..base import base
else:
    from utils import click_image_ocr, slide_image_handle
    from handle import selenium_options
    from base import base


class TxOperation(base.Base):
    def __init__(self, browser):
        self.browser = browser

    def click_captcha(self):
        locator = (By.XPATH, '//*[@id="tcaptcha_transform_dy"]')
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(locator))
        time.sleep(1)
        frame_x = self.browser.execute_script(
            "return document.getElementById('tcaptcha_transform_dy').getBoundingClientRect()['x']")
        frame_y = self.browser.execute_script(
            "return document.getElementById('tcaptcha_transform_dy').getBoundingClientRect()['y']")
        self.browser.switch_to.frame('tcaptcha_iframe_dy')
        image_x = self.browser.find_element_by_id('slideBg').location['x']
        image_y = self.browser.find_element_by_id('slideBg').location['y']
        while True:
            code = self.browser.find_element_by_id('instructionText').text
            code = str(re.compile('. . .').findall(code)[0]).replace(' ', '')
            self.captcha_print(code)
            image = self.browser.find_element_by_id('slideBg').get_attribute("style")
            image = re.compile('url\("(.+)"\);').findall(image)
            image_url = 'https://t.captcha.qq.com' + image[0]
            image_ocr = click_image_ocr.Ddddocr().get_img_xy(requests.get(image_url).content)
            r = True
            for hans_code in code:
                if hans_code not in image_ocr:
                    self.captcha_print("无正确结果, 正在重试")
                    self.browser.find_element_by_id('reload').click()
                    time.sleep(1)
                    r = False
                    break
                code_x, code_y = image_ocr[hans_code]
                time.sleep(1)
                ActionChains(self.browser).move_by_offset(frame_x + image_x + code_x,
                                                     frame_y + image_y + code_y).click().perform()
                ActionChains(self.browser).reset_actions()
            if r:
                self.browser.find_element_by_xpath('//*[@id="tcStatus"]/div[2]/div[2]/div/div').click()
                self.browser.switch_to.parent_frame()
                return self.browser

    def slide_captcha(self):
        try:
            locator = (By.XPATH, '//*[@id="tcaptcha_iframe_dy"]')
            WebDriverWait(self.browser, 3).until(EC.presence_of_element_located(locator))
            self.browser.switch_to.frame('tcaptcha_iframe_dy')
            slide_version = 1
        except Exception:
            self.browser.switch_to.frame('tcaptcha_iframe')
            slide_version = 2

        if slide_version == 1:
            self.browser.find_element_by_id('reload').click()
            background_image = re.compile('url\("(.+)"\);').findall(
                self.browser.find_element_by_id('slideBg').get_attribute("style"))
            background_url = 'https://t.captcha.qq.com' + background_image[0]
        elif slide_version == 2:
            self.browser.find_element_by_xpath('//*[@id="tcStatus"]/div[5]/div[2]').click()
            background_url = self.browser.find_element_by_id('slideBg').get_attribute("src")
        else:
            raise 'Error'
        background_bytes = requests.get(background_url).content

        target_image_path = self.current_path() + '/../temp/tx_slide_target.png'
        if slide_version == 1:
            target_image = re.compile('url\("(.+)"\);').findall(
                self.browser.find_element_by_xpath('//*[@id="tcOperation"]/div[7]').
                    get_attribute("style"))
            target_url = 'https://t.captcha.qq.com' + target_image[0]
            with open(self.current_path() + "/../template/tx_slide_target.html", 'r', encoding='utf-8') as fp:
                html = str(fp.read()).replace('#target_url#', str(target_url))
            with open(self.current_path() + "/../temp/tx_slide_target.html", 'w', encoding='utf-8') as f:
                f.write(html)
            options = selenium_options.gen_options(True)
            target_browser = webdriver.Chrome(options=options)
            target_browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': self.get_stealth_js()})
            target_browser.get("file://" + self.current_path() + "/../temp/tx_slide_target.html")
            target_browser.execute_script('document.body.style.zoom="0.8"')
            target_xpath = target_browser.find_element_by_xpath('/html/body/div')
            target_xpath.screenshot(target_image_path)
        elif slide_version == 2:
            target_url = self.browser.find_element_by_id('slideBlock').get_attribute("src")
            target_src = requests.get(target_url).content
            with open(target_image_path, 'wb') as f:
                f.write(target_src)
        slide_image_handle.del_background(target_image_path)
        with open(target_image_path, 'rb') as f:
            target_bytes = f.read()
        det = ddddocr.DdddOcr(det=False, ocr=False)
        res = det.slide_match(target_bytes, background_bytes)

        slide_width = 0
        if slide_version == 1:
            slide_width = self.browser.execute_script("return (document.querySelector(\"#tcOperation > div:nth-child("
                                                      "7)\").clientWidth - "
                                                      "document.querySelector(\"#tcOperation > "
                                                      "div.tc-fg-item.tc-slider-normal\").clientWidth);")
            if slide_width < 50:
                slide_width = self.browser.execute_script("return (document.querySelector(\"#tcOperation > "
                                                          "div:nth-child( "
                                                          "8)\").clientWidth - "
                                                          "document.querySelector(\"#tcOperation > "
                                                          "div.tc-fg-item.tc-slider-normal\").clientWidth);")
        elif slide_version == 2:
            slide_width = self.browser.execute_script('return (document.querySelector("#slide > '
                                                      'div.tc-drag-track").clientWidth - document.querySelector('
                                                      '"#tcaptcha_drag_thumb").clientWidth);')

        self.captcha_print(res)
        slide_width *= 0.93
        target_xy = slide_width * ((res['target'][0] + res['target'][2]) / 2 / 672)
        slide_btn = ''
        if slide_version == 1:
            slide_btn = self.browser.find_element_by_xpath('//*[@id="tcOperation"]/div[6]')
        elif slide_version == 2:
            slide_btn = self.browser.find_element_by_id('tcaptcha_drag_thumb')
        ActionChains(self.browser).click_and_hold(slide_btn).perform()
        ActionChains(self.browser).move_by_offset(xoffset=target_xy, yoffset=0).perform()
        slide_btn.click()
        time.sleep(1)
        self.browser.switch_to.parent_frame()
        try:
            _pep8 = self.browser.find_element_by_id("randstr").text
            return self.browser
        except Exception as _pep8:
            self.captcha_print("未成功滑动，正在重试")
            return self.slide_captcha()