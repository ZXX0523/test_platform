import base64
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
from Crypto.PublicKey import RSA
from conf.readconfig import *
import random
import requests
import jsonpath
import json



class wandou_unbindWechat():
    # 加密手机号
    def get_wandow_encrypt(self,phone):
        WANDOU_PUBLIC_KEY = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCw1znRd8ck4JujUxBvQKBYGykn1kLafsyNVw4hN+LN93PiFwLiQgfzDZewTuqhWhjegVbcKgAf8MCsYHSZ9FdKRueVZwqM4nRQ+HuL9tolp7JIv7S9CLt7zvkxZW7xIN92JPs+rppBIVIwLNkwBxy1M5KgQClwhGK5eHAsB4AfhwIDAQAB"
        # 获取豌豆侧用户中心，手机号或密码加密后的密文
        wpk_public_key = '-----BEGIN PUBLIC KEY-----\n' + WANDOU_PUBLIC_KEY + '\n-----END PUBLIC KEY-----'
        rsa_key = RSA.importKey(wpk_public_key)
        cipher = Cipher_pksc1_v1_5.new(rsa_key)
        encrypt_text = cipher.encrypt(phone.encode())
        cipher_text_tmp = base64.b64encode(encrypt_text)
        return cipher_text_tmp.decode()

    #获取豌豆authorization
    def get_wandou_authorization(self,choose_url,phoneCipher,passwordCipher):
        order_url = getConfig("gw-url", choose_url)
        url_path = "/api/memberaggr/unau/user/passwordLogin"
        payload = json.dumps({
            "passwordCipher":passwordCipher,
            "areaCode": '86',
            "phoneCipher":phoneCipher,
            "cipherVersion": "v1",
            "source": 12305,
            "appTypeCode": "MASTER_WECHAT"
        })
        headers = {
             "Content-Type": "application/json",
             "appid": "46620432"
        }
        response = requests.request("POST",headers=headers,url=order_url+url_path,data=payload)
        re = json.loads(response.text)
        # print("获取authorization：", re)
        try:
             return re['data']['authorization']
        except KeyError as e:
             # 异常时，执行该块
             return False, e

    #微信解绑
    def unbindWechat(self,choose_url,openid,authorization):
        member_url = getConfig("member-url",choose_url)
        url_path = "/member/v1/front/unbindWechat"
        payload = json.dumps({
            "appTypeCode": "MASTER_WECHAT",
            "openid": openid
        })
        headers = {
             "Content-Type": "application/json",
             "appid":"wxa1daf9c5db49d7c8",
             "x-auth-type":"user",
             "authorization":authorization
        }
        response = requests.request("POST",headers=headers,url=member_url+url_path,data=payload)
        re = json.loads(response.text)
        # print("微信解绑结果返回：", re)
        try:
            return re
        except KeyError as e:
            # 异常时，执行该块
            return False, e


    #生产环境微信解绑流程
    def run(self,choose_url,openid):
        #先登录获取authorization
        phoneCipher = self.get_wandow_encrypt('15915886236')
        passwordCipher = self.get_wandow_encrypt('123456')
        authorization = self.get_wandou_authorization(choose_url,phoneCipher,passwordCipher)
        if authorization is False: return False, "登录失败"
        #微信解绑
        try:
           re = self.unbindWechat(choose_url,openid,authorization)
           return re
        except KeyError as e:
           # 异常时，执行该块
           return False, "False"
           pass
        except IndexError as e:
           # 异常时，执行该块
           return False, "False"
           pass
        finally:
           # 无论异常与否，最终执行该块
           pass





# if __name__ == '__main__':
#     choose_url = 'pro'
#     openid = 'o555nwaEjAHegTBVj5YCkZ2aCpXE'
#     re = wandou_unbindWechat().run(choose_url,openid)
#     print("打印解绑接口返回：",re)

