from flask import Flask
import requests
import base64
import http.client
import hashlib
import urllib
import random
import json
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def say():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=EqCrf9uiA6NXRFGr1KEBsb58&client_secret=2Qesi6mhGnTofyCs9sGzmMGYDHboKkgh'
    response = requests.get(host)
    # print(response)
    ai_response = ""
    if response:
        access_token = response.json()['access_token']
        # print(access_token)
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
        # 二进制方式打开图片文件
        # f = open('[本地文件]', 'rb')
        # img = base64.b64encode(f.read())
        img_src = "https://cbu01.alicdn.com/img/ibank/2020/341/009/20518900143_171621457.360x360.jpg"
        iresponse = requests.get(img_src)
        img = base64.b64encode(iresponse.content)
        params = {"image":img}
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        ai_response = requests.post(request_url, data=params, headers=headers)
        words_result = ai_response.json()['words_result']
        for target_list in words_result:
            translation = baidu_translate(target_list['words'])
            print(translation)
            pass
    return ai_response.json()

def baidu_translate(word):
    appid = '20200526000470908'  # 填写你的appid
    secretKey = 'KcKZn2yFt001N2PEVx5R'  # 填写你的密钥

    httpClient = None
    myurl = '/api/trans/vip/translate'

    fromLang = 'zh'   #原文语种
    toLang = 'en'   #译文语种
    salt = random.randint(32768, 65536)
    q= word
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
    salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        print (result)
        return result.trans_result[0].dst

    except Exception as e:
        print (e)
    finally:
        if httpClient:
            httpClient.close()
    pass

def replaceZeroes(data):
    min_nonzero = min(data[np.nonzero(data)])
    data[data == 0] = min_nonzero
    return data


def SSR(src_img, size):
    L_blur = cv2.GaussianBlur(src_img, (size, size), 0)
    img = replaceZeroes(src_img)
    L_blur = replaceZeroes(L_blur)

    dst_Img = cv2.log(img / 255.0)
    dst_Lblur = cv2.log(L_blur / 255.0)
    dst_IxL = cv2.multiply(dst_Img, dst_Lblur)
    log_R = cv2.subtract(dst_Img, dst_IxL)

    dst_R = cv2.normalize(log_R, None, 0, 255, cv2.NORM_MINMAX)
    log_uint8 = cv2.convertScaleAbs(dst_R)
    return log_uint8

def removeCH(img):
    size = 3
    src_img = cv2.imread(img)
    b_gray, g_gray, r_gray = cv2.split(src_img)
    b_gray = SSR(b_gray, size)
    g_gray = SSR(g_gray, size)
    r_gray = SSR(r_gray, size)
    result = cv2.merge([b_gray, g_gray, r_gray])

    cv2.imshow('img', src_img)
    cv2.imshow('aaa', result)
    cv2.imwrite('cavity1.png', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 对增强后图像进行Canny：
    img = cv2.imread('cavity1.png', cv2.IMREAD_GRAYSCALE)
    canny_img = cv2.Canny(img, 200, 150)
    cv2.imwrite('cavity2.png', canny_img)

    # 对边缘图像进行闭运算得到掩码图：
    img = cv2.imread('cavity2.png', 1)
    k = np.ones((3, 3), np.uint8)
    img2 = cv2.morphologyEx(img, cv2.MORPH_CLOSE, k)  # 闭运算
    cv2.imwrite('cavity3.png', img2)
    return 0

# 对图像进行修复：
def repair(path):
    img = cv2.imread(path)

    b = cv2.imread('cavity3.png',0)
    dst = cv2.inpaint(img, b, 5, cv2.INPAINT_TELEA)
    cv2.imshow('dst', dst)
    cv2.imwrite(f'repair_{path}', dst)
    cv2.waitKey()
    cv2.destroyAllWindows()    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")