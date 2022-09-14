import os
from selenium import webdriver


class Base:
    @staticmethod
    def current_path():
        return os.path.dirname(__file__)

    @staticmethod
    def gen_options(headless):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        if headless:
            options.add_argument("--headless")
        return options

    @staticmethod
    def captcha_print(content):
        print(f"CaptchaPass - {content}")

    @staticmethod
    def get_stealth_js():
        with open(os.path.dirname(__file__) + "/../template/stealth.min.js", 'r') as f:
            stealth_js = f.read()
        return stealth_js

    @staticmethod
    def tx_gen_html(captcha_app_id):
        with open(os.path.dirname(__file__) + "/../template/tx_captcha.html", 'r', encoding='utf-8') as fp:
            html = str(fp.read()).replace('#CaptchaAppId#', str(captcha_app_id))

        with open(os.path.dirname(__file__) + "/../temp/tx_captcha.html", 'w', encoding='utf-8') as f:
            f.write(html)