import json

import requests

from conf.readconfig import getConfig


class getSignApi():
    #获取签名sign接口
    def getSign(self,data,choose_url):
        sign_url = getConfig("sign-url",choose_url)
        url_path = '/assets/v1/signature/get'
        payload = json.dumps(data)
        headers = {
            'content-type': 'application/json',
            'appid': '46620464',
            'Authorization': 'EFXfxsRDN9EwQXvqrMDWkboJT9E9btZl',
            'key': '40g3ndAr2a9mHrTdJbNEapT5sjLmr1uX'
        }
        response = requests.request("POST", sign_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        print("sign-url:",sign_url + url_path)
        print("请求头：",headers)
        print("请求体：",payload)
        print("获取到的sign接口响应:", re)
        print ("打印sign:",re)
        # sign = re['data']['v1']
        return re


    def getSign_api(self,data,url,sign):
        api_url = url
        payload = json.dumps(data)
        headers = {
            'content-Type': 'application/json',
            'appid': '46620464',
            'sign': sign,
            'x-auth-type': 'sign'
        }
        response = requests.post(url=url,headers=headers,data=payload)
        re = json.loads(response.text)
        return re

    def run(self,choose_url,url,data):
        try:
            data = eval(data)
            sign_response = getSignApi().getSign(data,choose_url)
            if sign_response['message'] == '操作成功':
                  sign = sign_response['data']['v1']
                  print("run函数获取的sign:",sign)
                  result = getSignApi().getSign_api(data,url,sign)
                  print("run函数的result：",result)
                  return result
            else:
                return sign_response

            pass
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
#     choose_url = 'test'
#     url = 'http://uat-gw.vipthink.cn/api/order/v1/collection-refund/internal/submitRefundApply'
#     data = {"createAdminUser": 666954, "detainmentResult": "refund33", "orderNumber": "20220614101612608202163", "refundFileUrl": "https://cc-vipthink-pub.oss-cn-beijing.aliyuncs.com/invoice_order1574481642127.jpg", "refundPrice": 10.01, "refundReason": "refundtest", "refundType": 1, "sysRefundPrice": 10.01}
#     method = 'POST'
#     re = getSignApi().run(choose_url,url,data,method)
#     # sign = getSign_api().getSign(data,choose_url)
#     # print("打印sign:")
#     # result = getSign_api().getSig_api(data,url,method,sign)
#     print ("接口响应结果：",re)
#
#
