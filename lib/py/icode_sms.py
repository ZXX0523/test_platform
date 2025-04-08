import json

import requests

from conf.readconfig import getConfig
from lib.py.order_V2_script import *
import requests
import json
import pandas as pd
import os, time

import oss2
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from conf.readconfig import *

class Get_sms():
    def get_sms(self,choose_url,phone,Authorization):
     message_url = getConfig("message-url",choose_url)
     url_path = '/message-web/console/message/list'
     payload = json.dumps(
        {"messageType": 2, "mobile": phone, "nowPage": 1, "pageSize": 50}
     )
     headers = {
        'content-type': 'application/json',
        'authorization': Authorization
     }

     response = requests.request("POST",message_url+url_path,headers=headers,data=payload)
     re = json.loads(response.text)
     # print("请求url：",message_url+url_path)
     # print("请求头：",headers)
     # print("请求体：",payload)
     # print("返回结果：",response.text)
     templatedata = re['data'][0]['templateData']
     pushstatus = re['data'][0]['pushStatus']
     mobile = re['data'][0]['mobile']
     # print("获取成功:",templatedata,pushstatus,mobile)
     # print("templatedata:",templatedata)
     return templatedata,pushstatus,mobile

    def getCrmToken(self,choose_url):
        auth_url = getConfig("auth-url",choose_url)
        url_path = "/v1/auth/admin/token"
        payload = json.dumps({
            "username": getConfig("crm-login",choose_url+"_phone"),
            "password": getConfig("crm-login",choose_url+"_pwd"),
            "__fields": "token,uid"
        })
        headers = {
            'content-type': 'application/json'
        }
        response = requests.request("POST", auth_url+url_path, headers=headers, data=payload)
        re=json.loads(response.text)
        try:
            return re['data']['token'],re['data']['uid']
        except KeyError as e:
            # 异常时，执行该块
            return False, e
            pass




    def run(self,choose_url, phone,Authorization):
      if choose_url != 'test':choose_url = 'pro'
      # Authorization = 'Bearer '+self.getCrmToken(choose_url)[0]
      if Authorization == "": Authorization = 'Bearer '+self.getCrmToken(choose_url)[0]
      # print("authorization:",Authorization)

      if Authorization is False: return False, "登录失败"
      try:
        # 主代码块
         templatedata = Get_sms().get_sms(choose_url,phone,Authorization)
         print("验证吗：",templatedata)
         return templatedata     #True, "Success"
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



if __name__ == '__main__':
    print("开始查询...")
    choose_url = 'pro' #'test' 'pro'
    phone = '15915886236'
    Authorization = ''
    # Authorization = 'Bear eyJhbGciOiJzaGEyNTYiLCJ0eXAiOiJKV1QifQ.W3sibmJmIjoxNjQwNTg5ODk2LCJpc3MiOiJkb2YiLCJ0emEiOiJDU1QiLCJleHAiOjE2NDA2NzYyOTYsImlhdCI6MTY0MDU4OTg5Niwic2lkIjoxfSx7InJhbmQiOiIxOTMxNjM2MDczNTQzNTU3Mjc5NTc4MzIxMDg2MTM3MTYxMjAxMzE2MzkzOTQxMDAzMzk5ODQwNzQ1NTY2MDUzIiwidWlkIjo2NTkwNTMsInR5cCI6ImEiLCJ0aW1lIjoxNjQwNTg5ODk2fV0.MTk0ZTVlMTliMWMzZDQwYmJiZGIxMzIzZmM3ZDMwODYxNTNlYzU0YzZjYjhmMjBhZmRjMGE4NDk2YzdlMGZmMQ'
    Get_sms().run(choose_url,phone,Authorization)

    print("执行结束：")


