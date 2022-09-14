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
    from ..base import base
    from ..operation import tx
else:
    from base import base
    from operation import tx


class TX(base.Base):
    def __init__(self, headless=True):
        super(base.Base)
        self.options = self.gen_options(headless)

    def click_captcha_callback(self, captcha_app_id):
        """
        获取randstr和ticket，适用于前后端分离项目
        :param captcha_app_id: 网站验证码ID(可通过查看数据获取)
        :return: randstr, ticket
        """
        self.tx_gen_html(captcha_app_id)

        browser = webdriver.Chrome(options=self.options)
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': self.get_stealth_js()})
        browser.get("file://" + self.current_path() + "/../temp/tx_captcha.html")
        browser = tx.TxOperation(browser).click_captcha()
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
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': cls.get_stealth_js})
        return tx.TxOperation(browser).click_captcha()

    def slide_captcha_callback(self, captcha_app_id):
        self.tx_gen_html(captcha_app_id)
        browser = webdriver.Chrome(options=self.options)
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': self.get_stealth_js()})
        # browser.get('https://bot.sannysoft.com/')
        browser.get("file://" + self.current_path() + "/../temp/tx_captcha.html")
        tx.TxOperation(browser).slide_captcha()
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
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': cls.get_stealth_js()})
        return tx.TxOperation(browser).slide_captcha()
