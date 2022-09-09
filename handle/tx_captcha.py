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

if os.path.dirname(__file__) != (os.getcwd() + "\\handle"):
    from ..utils import click_image_ocr, slide_image_handle
    from ..handle import selenium_options
else:
    from utils import click_image_ocr, slide_image_handle
    from handle import selenium_options

current_path = os.path.dirname(__file__)

with open(current_path + "/../template/stealth.min.js", 'r') as f:
    stealth = f.read()


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
        code = browser.find_element_by_id('instructionText').text
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


def slide_captcha(browser):
    locator = (By.XPATH, '//*[@id="tcaptcha_transform_dy"]')
    WebDriverWait(browser, 10).until(EC.presence_of_element_located(locator))
    time.sleep(1)
    browser.switch_to.frame('tcaptcha_iframe_dy')
    browser.find_element_by_id('reload').click()
    time.sleep(1)
    background_image = re.compile('url\("(.+)"\);').findall(
        browser.find_element_by_id('slideBg').get_attribute("style"))
    background_url = 'https://t.captcha.qq.com' + background_image[0]
    background_bytes = requests.get(background_url).content

    target_image = re.compile('url\("(.+)"\);').findall(browser.find_element_by_xpath('//*[@id="tcOperation"]/div[7]').
                                                        get_attribute("style"))
    target_url = 'https://t.captcha.qq.com' + target_image[0]
    with open(current_path + "/../template/tx_slide_target.html", 'r', encoding='utf-8') as fp:
        html = str(fp.read()).replace('#target_url#', str(target_url))
    with open(current_path + "/../temp/tx_slide_target.html", 'w', encoding='utf-8') as f:
        f.write(html)
    options = selenium_options.gen_options(True)
    target_browser = webdriver.Chrome(options=options)
    target_browser.get("file://" + current_path + "/../temp/tx_slide_target.html")
    target_browser.execute_script('document.body.style.zoom="0.8"')
    target_xpath = target_browser.find_element_by_xpath('/html/body/div')
    target_image = current_path + '/../temp/tx_slide_target.png'
    target_xpath.screenshot(target_image)
    slide_image_handle.del_background(target_image)
    with open(target_image, 'rb') as f:
        target_bytes = f.read()
    with open(current_path + '/../temp/tx_slide_background.png', 'wb') as f:
        f.write(background_bytes)
    det = ddddocr.DdddOcr(det=False, ocr=False)
    res = det.slide_match(target_bytes, background_bytes)
    slide_width = browser.execute_script("return (document.querySelector(\"#tcOperation > div:nth-child("
                                         "7)\").clientWidth - "
                                         "document.querySelector(\"#tcOperation > "
                                         "div.tc-fg-item.tc-slider-normal\").clientWidth);")
    if slide_width < 50:
        slide_width = browser.execute_script("return (document.querySelector(\"#tcOperation > div:nth-child("
                                             "8)\").clientWidth - "
                                             "document.querySelector(\"#tcOperation > "
                                             "div.tc-fg-item.tc-slider-normal\").clientWidth);")
    captcha_print(res)
    slide_width *= 0.93
    target_xy = slide_width * ((res['target'][0] + res['target'][2]) / 2 / 672)
    slide_btn = browser.find_element_by_xpath('//*[@id="tcOperation"]/div[6]')
    ActionChains(browser).click_and_hold(slide_btn).perform()
    ActionChains(browser).move_by_offset(xoffset=target_xy, yoffset=0).perform()
    ActionChains(browser).release().perform()
    time.sleep(1)
    browser.switch_to.parent_frame()
    try:
        _pep8 = browser.find_element_by_id("randstr").text
        return browser
    except Exception as _pep8:
        captcha_print("未成功滑动，正在重试")
        return slide_captcha(browser)


def tx_gen_html(captcha_app_id):
    with open(current_path + "/../template/tx_captcha.html", 'r', encoding='utf-8') as fp:
        html = str(fp.read()).replace('#CaptchaAppId#', str(captcha_app_id))

    with open(current_path + "/../temp/tx_captcha.html", 'w', encoding='utf-8') as f:
        f.write(html)


class TX:
    def __init__(self, headless=True):
        self.options = selenium_options.gen_options(headless)

    def click_captcha_callback(self, captcha_app_id):
        """
        获取randstr和ticket，适用于前后端分离项目
        :param captcha_app_id: 网站验证码ID(可通过查看数据获取)
        :return: randstr, ticket
        """
        tx_gen_html(captcha_app_id)

        browser = webdriver.Chrome(options=self.options)
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth})
        browser.get("file://" + current_path + "/../temp/tx_captcha.html")
        browser = click_captcha(browser)
        time.sleep(1)
        try:
            pass_code = {"randstr": browser.find_element_by_id("randstr").text,
                         "ticket": browser.find_element_by_id("ticket").text}
            browser.close()
            return pass_code
        except:
            return '验证失败!'

    @classmethod
    def click_captcha_injection(cls, browser):
        """
        注入方式验证
        :param browser: 浏览器对象
        :return: 浏览器对象
        """
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth})
        return click_captcha(browser)

    def slide_captcha_callback(self, captcha_app_id):
        tx_gen_html(captcha_app_id)
        browser = webdriver.Chrome(options=self.options)
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth})
        # browser.get('https://bot.sannysoft.com/')
        browser.get("file://" + current_path + "/../temp/tx_captcha.html")
        slide_captcha(browser)
        try:
            pass_code = {"randstr": browser.find_element_by_id("randstr").text,
                         "ticket": browser.find_element_by_id("ticket").text}
            browser.close()
            return pass_code
        except Exception as _pep8:
            return '验证失败!'

    @classmethod
    def slide_captcha_injection(cls, browser):
        """
        注入方式验证
        :param browser: 浏览器对象
        :return: 浏览器对象
        """
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth})
        return slide_captcha(browser)
