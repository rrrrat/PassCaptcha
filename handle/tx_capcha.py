import re
import time
import os

import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

if os.path.dirname(__file__) != (os.getcwd() + "\\handle"):
    from ..utils import click_image_ocr
else:
    from utils import click_image_ocr

current_path = os.path.dirname(__file__)


def captcha_print(content):
    print(f"CaptchaPass - {content}")


def click_captcha(browser):
    locator = (By.XPATH, '//*[@id="tcaptcha_transform_dy"]')
    WebDriverWait(browser, 10).until(EC.presence_of_element_located(locator))
    time.sleep(1)
    frame_x = browser.execute_script(
        "return document.getElementById('tcaptcha_transform_dy').getBoundingClientRect()['x']")
    frame_y = browser.execute_script(
        "return document.getElementById('tcaptcha_transform_dy').getBoundingClientRect()['y']")
    browser.switch_to.frame('tcaptcha_iframe_dy')
    image_x = browser.find_element_by_id('slideBg').location['x']
    image_y = browser.find_element_by_id('slideBg').location['y']
    while True:
        code = browser.find_element_by_id('guideText').text
        code = str(re.compile('. . .').findall(code)[0]).replace(' ', '')
        captcha_print(code)
        image = browser.find_element_by_id('slideBg').get_attribute("style")
        image = re.compile('url\("(.+)"\);').findall(image)
        image_url = 'https://t.captcha.qq.com' + image[0]
        image_ocr = click_image_ocr.Ddddocr().get_img_xy(requests.get(image_url).content)
        r = True
        for hans_code in code:
            if hans_code not in image_ocr:
                captcha_print("无正确结果, 正在重试")
                browser.find_element_by_id('reload').click()
                time.sleep(1)
                r = False
                break
            code_x, code_y = image_ocr[hans_code]
            time.sleep(1)
            ActionChains(browser).move_by_offset(frame_x + image_x + code_x,
                                                 frame_y + image_y + code_y).click().perform()
            ActionChains(browser).reset_actions()
        if r:
            browser.find_element_by_xpath('//*[@id="tcStatus"]/div[2]/div[2]/div/div').click()
            browser.switch_to.parent_frame()
            return browser


class TX:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
        if headless:
            self.options.add_argument("--headless")

    def click_captcha_callback(self, captcha_app_id):
        """
        获取randstr和ticket，适用于前后端分离项目
        :param captcha_app_id: 网站验证码ID(可通过查看数据获取)
        :return: randstr, ticket
        """
        with open(current_path + "/../html/tx_click_captcha.html", 'r', encoding='utf-8') as fp:
            html = str(fp.read()).replace('#CaptchaAppId#', str(captcha_app_id))

        with open(current_path + "/../temp/tx_click_captcha.html", 'w', encoding='utf-8') as f:
            f.write(html)

        browser = webdriver.Chrome(options=self.options)
        browser.get("file://" + current_path + "/../temp/tx_click_captcha.html")
        browser = click_captcha(browser)
        time.sleep(1)
        pass_code = {"randstr": browser.find_element_by_id("randstr").text,
                     "ticket": browser.find_element_by_id("ticket").text}
        browser.close()
        return pass_code

    @classmethod
    def click_captcha_injection(cls, browser):
        """
        注入方式验证
        :param browser: 浏览器对象
        :return: 浏览器对象
        """
        click_captcha(browser)
        return browser
