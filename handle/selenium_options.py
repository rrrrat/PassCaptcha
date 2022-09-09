from selenium import webdriver


def gen_options(headless):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    if headless:
        options.add_argument("--headless")
    return options
