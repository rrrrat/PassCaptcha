# PassCaptcha
## 推荐使用导入包的形式调用此项目
## 使用DDDDOCR识别文字坐标(这玩意真牛逼)
```angular2html
支持注入方式及返回callback方式通过验证码
当前支持腾讯点选验证, 阿里滑块验证, 腾讯滑动拼图(实验性功能)
```
## 更新
| 版本号   | 更新时间       | 更新内容            |
|-------|------------|-----------------|
| 0.0.1 | 2022.09.07 | 项目创建，初始支持腾讯点选   |
| 0.0.2 | 2022.09.08 | 新增阿里滑块验证        |
| 0.0.3 | 2022.09.09 | 新增腾讯滑动拼图(实验性功能) |

## 部署
### 0x01 准备 | 难度 1-5
```angular2html
Chrome浏览器(Linux也可正常部署，有疑问联系) | Windows难度: 1 Linux难度: 2
Chrome driver(百度一下，你就知道。注！需对应版本) | 难度: 1
将下载的chromedriver放在你项目的根路径
```
### 0x02 安装
```shell
git clone https://github.com/rrrrat/PassCaptcha.git
pip3 install -r requirements.txt
```

### 0x03 使用
```python
from PassCaptcha import AllPassCaptcha 

# 1.注入方式通过验证
# browser为你的webdriver.Chrome对象, 函数将返回你的浏览器对象
browser = AllPassCaptcha.TX().click_captcha_injection(browser)
browser = AllPassCaptcha.TX().slide_captcha_injection(browser)
browser = AllPassCaptcha.ALI().slide_captcha_callback(browser)
# return <object browser>

# 2.callback方式通过验证
# 此处captcha_app_id为对方网站腾讯验证码的APPID(访问网站查看网络内https://t.captcha.qq.com/cap_union_prehandle的aid值)下面会详细说明
randstr, ticket = AllPassCaptcha.TX().click_captcha_callback(captcha_app_id)
randstr, ticket = AllPassCaptcha.TX().slide_captcha_callback(captcha_app_id)
# 此处captcha_app_id, captcha_scene为对方网站阿里滑块验证的captcha_app_id和captcha_scene(访问网站查看网络内https://cf.aliyun.com/nocaptcha/initialize.jsonp的a和scene值)
# 与腾讯查看方式一样
session_id, sig, token = AllPassCaptcha.ALI().slide_captcha_callback(captcha_app_id, captcha_scene)
# return randstr, ticket
```



## 演示
### 1.注入方式
![](temp/injection_1.jpg)

### 2.callback方式
![](temp/callback_1.jpg)
#### 返回randstr, ticket
![](temp/callback_2.jpg)

## 获取captcha_app_id
![](temp/callback_3.jpg)
```angular2html
aid: 191805058
此处191805058为网站captcha_app_id
```

## 关于操作过于频繁
![](temp/err_1.jpg)
```angular2html
若网站风控等级过高会出现此类错误，可以尝试自己训练模型提高识别率解决此类问题。
这里大量征集训练数据。
```

![](temp/err_2.jpg)


## 关于后期更新
```angular2html
当前阿里滑块使用一镜到底方式，后期将优化此步骤，提高验证成功率。
当前无优化思路，欢迎大家给出意见。
```

## 须知
### 不要用191805058测试！！！不要用191805058测试！！！不要用191805058测试！！！
### 该程序仅用于学习用途，禁止用作非法用途！
### 个人维护，不定期更新
### 该程序造成的任何法律责任，财产损失或者人身伤害等问题，本人概不负责！
### 企鹅: 321878646
