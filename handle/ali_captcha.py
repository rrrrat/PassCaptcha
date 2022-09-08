from selenium.webdriver.common.action_chains import ActionChains
import random
import time
import os
from selenium import webdriver

current_path = os.path.dirname(__file__)


def slide_captcha(browser):
    slide_width = browser.execute_script("return (document.querySelector(\".nc_scale\").clientWidth - "
                                         "document.querySelector(\".nc_iconfont\").clientWidth);")
    click_btn = browser.find_element_by_css_selector(".btn_slide")
    ActionChains(browser).click_and_hold(click_btn).perform()
    ActionChains(browser).move_by_offset(xoffset=slide_width, yoffset=0).perform()
    ActionChains(browser).release().perform()
    return browser


class ALI:
    def __init__(self, headless=True):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36")
        with open(current_path + "/../template/stealth.min.js", 'r') as f:
            self.stealth = f.read()
        if headless:
            self.options.add_argument("--headless")

    def slide_captcha_callback(self, captcha_app_id, captcha_scene):
        with open(current_path + "/../template/ali_slide_captcha.html", 'r', encoding='utf-8') as fp:
            html = str(fp.read()).replace('#captcha_app_id#',
                                          str(captcha_app_id)).replace('#captcha_scene#', str(captcha_scene))

        with open(current_path + "/../temp/ali_slide_captcha.html", 'w', encoding='utf-8') as f:
            f.write(html)

        browser = webdriver.Chrome(options=self.options)
        browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': self.stealth})
        browser.get("file://" + current_path + "/../temp/ali_slide_captcha.html")
        browser = slide_captcha(browser)
        time.sleep(1)
        try:
            pass_code = {"session_id": browser.find_element_by_xpath('//*[@id="session_id"]').text,
                         "sig": browser.find_element_by_xpath('//*[@id="sig"]').text,
                         "token": browser.find_element_by_xpath('//*[@id="token"]').text}
            browser.close()
            return pass_code
        except:
            browser.close()
            return '验证失败!'

    @classmethod
    def slide_captcha_injection(cls, browser):
        return slide_captcha(browser)
