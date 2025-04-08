import random
from datetime import date

import numpy as np

from conf.readconfig import getConfig
from lib.py.order_V2_script import *
import requests
import json
import pandas as pd
import os, time

# import oss2
# from qcloud_cos import CosConfig
# from qcloud_cos import CosS3Client

from lib.py.hualala_applystandardcourser import ApplyStandardCourserRun
from lib.py.wandou_coming_user import WanDouUserComingRun
from conf.readconfig import *

class UserComingRun():
    def get_datemobile(self):
        # 获取当前日期
        now = time.time()
        new_phone = '1' + str(int(now))
        return new_phone
    # 根据转介绍上级画啦啦id获取平台用户id
    # def getBizId(self,TransferId,choose_url,queryType):
    #     Authorization = ApplyStandardCourserRun().getLiuyiToken(choose_url)
    #     sign_url = getConfig("liuyi-gw-mg-url",choose_url)
    #     url_path = '/bizcenter-usercenter/p/v1/user/query'
    #     headers = {
    #         'content-type': 'application/json',
    #         'authorization': Authorization
    #     }
    #     payload = json.dumps({
    #           "keyword": TransferId,
    #           "queryType": queryType
    #     })
    #     response = requests.request("POST", sign_url + url_path, headers=headers, data=payload)
    #     re = json.loads(response.text)
    #     if re['code']==0:
    #         return re['data'][0]['id']
    #     else:
    #         return 0

    #获取签名sign接口
    def GetBizUserid(self,orderNum,choose_url,choose_type,mobile,areaCode):
        global payload
        sign_url = getConfig("liuyi-url-1",choose_url)
        print(sign_url)
        url_path = '/bizcenter-usercenter/o/login/mobileCaptcha'
        headers = {
            'content-type': 'application/json'
        }

        if choose_type == 'appoint':
            usermobile = mobile
        else:
            usermobile = orderNum

        if choose_url =='test':
            payload = json.dumps({
              "pageLink": "https://pay-test.61info.cn/maliang-test/popularize-31904.html?business_Type=checkIn&courseBelong=HLL&courseSubjectType=1&fissionInviteConfigId=&invite_userID=3010462558&popularizeId=31904&posterId=31904",
              "channel": "PLATFORM",
              "terminal": "WEB",
              "telCode": 86,
              "countryCode": "CN",
              "mobile": usermobile,
              "captcha": "111111",
              "limitRegister": 'false'
            })
        elif choose_url =='pre':
            payload = json.dumps({
                "terminal": "WEB",
                # "pageLink": "https://market-h5-pre.61info.cn/maliang-pre/382-7690686776.html?popularizeId=23",
                "pageLink": "https://pay-test.61info.cn/maliang-pre/popularize-33896.html?business_Type=checkIn&courseBelong=HLL&courseSubjectType=1&fissionInviteConfigId=&invite_userID=3001548500&popularizeId=33896",
                "telCode": int(areaCode),
                "countryCode": "",
                "mobile": usermobile,
                "captcha": "111111",
                "channel": "PLATFORM"
            })
        response = requests.request("POST", sign_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        return re

    #第一步-提交学员进线
    def submitUserComing(self,accessToken,biz_user_id,choose_url,TransferId):
        # TransferId = 226397061
        global payload
        gw_url = getConfig("liuyi-url-1",choose_url)
        url_path = '/bizcenter-order-backend/o/v1/order/placeOrder'

        if choose_url =='test':
            payload = json.dumps({
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 84,
                  "num": 1,
                  "popularizeId": 31843,
                  "returnUrl": "https://market-h5-test.61info.cn/maliang-test/popularize-31843.html?",
                  "channelId": "291",
                  "formData": {
                    "age": 6
                  },
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id,
                    }
                  }
                })
        elif choose_url =='pre':
            payload = json.dumps({
                "activityId": 'null',
                "activityType": 1,
                "addPurchaseActivityReq": {
                    "addGoods": []
                },
                "channelCode": "PLATFORM",
                "displayActualAmount": 0,
                "goodsId": 2,
                "num": 1,
                "popularizeId": "23",
                "returnUrl": "https://market-h5-pre.61info.cn/maliang-pre/382-7690686776.html?popularizeId=23",
                "channelId": "18",
                "formData": {
                    "age": 12
                },
                "price": 0,
                "extraInfo": {
                    "bizUserIdMap": {
                        "PLATFORM": biz_user_id
                    }
                }
            })
        if TransferId == "0":
            print("TransferId:" + TransferId)
            headers = {
                'content-Type': 'application/json',
                'Auth': accessToken,
            }
        else:
            # transfer_id = self.getBizId(TransferId,choose_url,4)
            transfer_id = WanDouUserComingRun().GetPlatformUserid(choose_url,TransferId,str("HLL"))
            print("transfer_id:",transfer_id)
            if transfer_id != int(0):
                if choose_url == 'test':
                    cookie="_ga=GA1.2.1849005566.1709897342; _ga_D1FM8TW3RM=GS1.1.1722936724.3.1.1722936929.44.0.0; _ga_PKC3YZCYQ0=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_S200MHJ9H3=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_9NT8CGDND8=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_VMYC3SS2SE=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_0C9G9JD0YT=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_25C04NL7R4=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_LBJJYH0K3G=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_B5BTT07LP1=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_2N593TT8CR=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_HYLVLTP58J=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_Y4K746K2LW=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_YHS3JESL36=GS1.1.1722936724.3.1.1722936929.45.0.0; _ga_9LCSSXV2KP=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_WJKV9R3RVW=GS1.1.1722936724.3.1.1722936929.0.0.0; _gcl_au=1.1.119426728.1732782500; _fbp=fb.1.1732786394243.55125292262667820; popularUrl=https%253A%252F%252Fpay-test.61info.cn%252Fmaliang-test%252Fpopularize-31904.html%253Fbusiness_Type%253DcheckIn%2526courseBelong%253DHLL%2526courseSubjectType%253D1%2526fissionInviteConfigId%253D%2526invite_userID%253D"+str(transfer_id)+"%2526popularizeId%253D31904%2526posterId%253D31904; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%223028512505%22%2C%22first_id%22%3A%2218deec60abfc8f-062353c9c7ac484-26001851-2073600-18deec60ac0822%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThkZWVjNjBhYmZjOGYtMDYyMzUzYzljN2FjNDg0LTI2MDAxODUxLTIwNzM2MDAtMThkZWVjNjBhYzA4MjIiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIzMDI4NTEyNTA1In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%223028512505%22%7D%2C%22%24device_id%22%3A%2218deec60abfc8f-062353c9c7ac484-26001851-2073600-18deec60ac0822%22%7D"
                    payload = json.dumps({
                        "activityId": 'null',
                        "activityType": 1,
                        "addPurchaseActivityReq": {
                            "addGoods": []
                        },
                        "channelCode": "PLATFORM",
                        "displayActualAmount": 0,
                        "goodsId": 84,
                        "num": 1,
                        "popularizeId": "31904",
                        "returnUrl": "https://pay-test.61info.cn/maliang-test/popularize-31904.html?business_Type=checkIn&courseBelong=HLL&courseSubjectType=1&fissionInviteConfigId=&invite_userID="+str(transfer_id)+"&popularizeId=31904&posterId=31904&bizToken=" + accessToken + "&bizChannel=PLATFORM&interactiveConfig={\"action\":\"comp:purchaseEvent\",\"content\":\"purchaseEvent\",\"customPopup\":\"\",\"customPopupEvent\":\"\",\"params\":[],\"conditionsForSuccess\":\"\",\"orderSuccess\":{\"action\":\"\",\"content\":\"\",\"customPopup\":\"\",\"customPopupEvent\":\"\",\"params\":[]}}",
                        "price": 0,
                        "extraInfo": {
                            "bizUserIdMap": {
                                "PLATFORM": biz_user_id
                            }
                        }
                    })
                else:
                    cookie="_ga=GA1.2.1849005566.1709897342; _ga_D1FM8TW3RM=GS1.1.1722936724.3.1.1722936929.44.0.0; _ga_PKC3YZCYQ0=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_S200MHJ9H3=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_9NT8CGDND8=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_VMYC3SS2SE=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_0C9G9JD0YT=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_25C04NL7R4=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_LBJJYH0K3G=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_B5BTT07LP1=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_2N593TT8CR=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_HYLVLTP58J=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_Y4K746K2LW=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_YHS3JESL36=GS1.1.1722936724.3.1.1722936929.45.0.0; _ga_9LCSSXV2KP=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_WJKV9R3RVW=GS1.1.1722936724.3.1.1722936929.0.0.0; _gcl_au=1.1.119426728.1732782500; _fbp=fb.1.1732786394243.55125292262667820; LtpaToken=AAECAzY3NjI3NDA2Njc2MzFDQzYxNTU0Njc5NjY4MB6Ew9kDrJbNQxjFxLW2OijAmfQv; popularUrl=https%253A%252F%252Fpay-test.61info.cn%252Fmaliang-pre%252Fpopularize-33896.html%253Fbusiness_Type%253DcheckIn%2526courseBelong%253DHLL%2526courseSubjectType%253D1%2526fissionInviteConfigId%253D%2526invite_userID%253D"+str(transfer_id)+"%2526popularizeId%253D33896; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%223003579344%22%2C%22first_id%22%3A%2218deec60abfc8f-062353c9c7ac484-26001851-2073600-18deec60ac0822%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThkZWVjNjBhYmZjOGYtMDYyMzUzYzljN2FjNDg0LTI2MDAxODUxLTIwNzM2MDAtMThkZWVjNjBhYzA4MjIiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIzMDAzNTc5MzQ0In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%223003579344%22%7D%2C%22%24device_id%22%3A%2218deec60abfc8f-062353c9c7ac484-26001851-2073600-18deec60ac0822%22%7D"
                    payload = json.dumps({
                      "activityId": 'null',
                      "activityType": 1,
                      "addPurchaseActivityReq": {
                        "addGoods": []
                      },
                      "channelCode": "PLATFORM",
                      "displayActualAmount": 0,
                      "goodsId": 2,
                      "num": 1,
                      "popularizeId": "33896",
                      "returnUrl": "https://pay-test.61info.cn/maliang-pre/popularize-33896.html?business_Type=checkIn&courseBelong=HLL&courseSubjectType=1&fissionInviteConfigId=&invite_userID="+str(transfer_id)+"&popularizeId=33896",
                      "channelId": "195",
                      "formData": {
                        "age": 5
                      },
                      "price": 0,
                      "extraInfo": {
                        "bizUserIdMap": {
                          "PLATFORM": biz_user_id
                        }
                      }
                    })
            else:
                return "查询不到转介绍上级学员的平台id，进线失败"
            headers = {
                'content-Type': 'application/json',
                'Auth': accessToken,
                'Cookie':cookie
            }
        response = requests.request("POST", gw_url + url_path, headers=headers, data=payload)

        re = json.loads(response.text)
        print(re)
        if re['code'] != 0:
            print("进线失败",re)
            return re
        else:
            return re

    #学员进线
    def UserComingRuning(self,choose_url,choose_type,mobile,coming_number,areaCode,TransferId):
        global coming_result
        try:
            numbers_list = []
            if choose_type =='appoint':
                coming_number = 1
            for i in range(int(coming_number)):
                print(f"这是第 {i + 1} 次循环")
                global orderNum
                orderNum = self.get_datemobile()
                numbers_list.append(int(orderNum))
                biz_user_info=self.GetBizUserid(orderNum,choose_url,choose_type,mobile,areaCode)
                biz_user_id = biz_user_info['data']['id']
                accessToken = biz_user_info['data']['accessToken']
                mobile = biz_user_info['data']['mobile']
                print("token:"+accessToken)
                coming_result = self.submitUserComing(accessToken, biz_user_id, choose_url,TransferId)
            if choose_type =='appoint':
                result = "手机号："+mobile
            else:
                result = "手机号："+str(numbers_list)
            # print(result)
            # array = np.array(result + str(coming_result['data']['res']))
            return result,coming_result

            # return result,coming_result[['data']['res']]
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
    print("执行开始。。。。")
    choose_url = "test" # test, pro
    choose_type = "random"
    biz_user_id ='3028494873'
    accessToken = 'eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjoid251bHQ2Y1NXV2wxMzBRS25zZlJrSCtVQjR4OHRpZW00M2tYajVDTkZTaE5GcU1weWZMUVlTQjBKUzdCWnhDclJMZjdaT0MvM2llZ01WWnBDYnVJWk05YkFyTEpnYk5ncDVjdnV4TmYvcHc1RFFPS1RxRTlOQlQ5eklvL1gra3J2Wm1aUVNYQnd1YjB1V2N1eWQxa0hod1U4VDlSM3Z5Qk9iZ1JLSXdsZERCSVA2YnVDcXhtVWpRUERoajlqSzRRT0YzSlBFQUxpNERBWEppbkJOcEhSLzFuditXT0xXRHJ1T0pjcExOYkUrQVhZNVJjbTI3UU9OYW1NZFkyQXZGY1U5dFh6bGRQMGNpT25BenhlRXFoQVhYa0czb0lneW1hTnhnL0R3UkFDTy9UVG5LSEVYMWc4ZWcwejAvU0paOWVjQXhHRFE1dHRnWWtVNVZNckU4MzJZZnBKWEpiR2JUQm9KbVRscXBZNGFpa3I3MnEveHBTZGhXVEpQbm1vZkttIiwiZXhwIjoxNzQxNzY5NjY0fQ.7fyKBw_GQwOgzIsYXelOJ_9n6S-ctFChuwK_rru-lPY'
    mobile = '13020122905'
    orderNum='13020241138'
    TransferId=22639706
    introduce=''
    coming_number=1
    areaCode=86
    refundPrice = 0.01
    re = UserComingRun().UserComingRuning(choose_url,choose_type,mobile,coming_number,areaCode,TransferId)
    # re= UserComingRun().GetBizUserid(orderNum,choose_url,choose_type,mobile,86)
    # re=UserComingRun().submitUserComing(accessToken,biz_user_id,choose_url)
    print("执行结束88,")
    print(re)


