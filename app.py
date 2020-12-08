from flask import Flask
import requests
import base64
import http.client
import hashlib
import urllib
import random
import json

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")