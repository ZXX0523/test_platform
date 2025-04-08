import random
from datetime import date

import numpy as np

from bin.runMySQL import mysqlMain
from conf.readconfig import getConfig
from lib.py import hualala_applystandardcourser
from lib.py.hualala_applystandardcourser import ApplyStandardCourserRun
from lib.py.order_V2_script import *
import requests
import json
import os, time
from conf.readconfig import *
# from hualala_applystandardcourser import ApplyStandardCourserRun

# from lib.py.hualala_coming_user import UserComingRun

class WanDouUserComingRun():
    def get_datemobile(self):
        # 获取当前日期
        now = time.time()
        new_phone = '1' + str(int(now))
        return new_phone
    def listChannels(self,choose_url,channel_id):
        Authorization = ApplyStandardCourserRun().getLiuyiToken(choose_url)
        print(channel_id)
        sign_url = getConfig("liuyi-gw-mg-url",choose_url)
        url_path = '/bizcenter-marketing-admin/o/wd/channel/listChannels'
        headers = {
            'content-type': 'application/json',
            'authorization': Authorization
        }
        payload = json.dumps({
            "likeKeyword": int(channel_id),
            "pageNum": 1,
            "pageSize": 1000
        })
        response = requests.request("POST", sign_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        channel_name = self.find_name_by_id(re['data'],channel_id)

        # print("渠道名：" + channel_name)
        if channel_name != None:
            sign_url = getConfig("liuyi-gw-mg-url", choose_url)
            url_path = '/bizcenter-marketing-admin/o/channel/update'
            headers = {
                'content-type': 'application/json',
                'authorization': Authorization
            }
            if choose_url=='test':
                payload = json.dumps({
                  "id": 26240,
                  "name": "益智渠道-验MQ",
                  "parentChannel": "渠道XXtest",
                  "parentId": 163,
                  "level": "S",
                  "peaChannelId": channel_id,
                  "peaChannelName": channel_name,
                })
            else:
                payload=json.dumps({
                  "id": 1293,
                  "name": "益智渠道-验MQ",
                  "parentChannel": "zwp渠道",
                  "parentId": 130,
                  "level": "S",
                  "peaChannelId": channel_id,
                  "peaChannelName": channel_name,
                })
            response = requests.request("POST", sign_url + url_path, headers=headers, data=payload)
            res = json.loads(response.text)
            print(res)
            return "渠道更新成功！"
        else:
            print("渠道更新失败！没有该渠道")
            return "渠道更新失败！没有该渠道id"


    def find_name_by_id(self,data, target_id):
        if isinstance(data, list):
            for item in data:
                result = self.find_name_by_id(item, target_id)
                if result is not None:
                    return result
        elif isinstance(data, dict):
            print(data['id'])
            if 'id' in data and data['id'] == int(target_id):
                return data.get('name')
            if 'children' in data and data['children']:
                return self.find_name_by_id(data['children'], target_id)
        return None

    def GetPlatformUserid(self,choose_url,TransferId,channel):
        if choose_url == "test":
            mysql_conn = mysqlMain('MySQL-Liuyi-test')
        else:
            mysql_conn = mysqlMain('MySQL-Liuyi-preprod')
        sql_user = "SELECT x.platform_user_id FROM `i61-bizcenter-usercenter`.u_platform_user_bind x WHERE channel = '{}' AND channel_user_id ={}".format(channel, TransferId)
        try:
            if TransferId == 0:
                return 0
            else:
                userid = mysql_conn.fetchone(sql_user)
                print(userid)
                if userid is None:
                    return 0
                return userid['platform_user_id']
        except Exception as e:
            return 0
        finally:
            del mysql_conn
    #获取签名sign接口
    def GetBizUserid(self,orderNum,choose_url,choose_type,mobile,areaCode,TransferId):
        global payload
        sign_url = getConfig("liuyi-url-1",choose_url)
        url_path = '/bizcenter-usercenter/o/login/mobileCaptcha?_from=maliang'
        headers = {
            'content-type': 'application/json'
        }
        if areaCode == "":
            areaCode = 86
        if choose_url =='test':
            if choose_type =='appoint':
                usermobile = mobile
            else:
                usermobile = orderNum
            payload = json.dumps({
                "pageLink": "https://pay-test.61info.cn/maliang-test/popularize-31904.html",
                "channel": "PLATFORM",
                "terminal": "WEB",
                "telCode": int(areaCode),
                "countryCode": "AU",
                "mobile": usermobile,
                "captcha": "111111",
                "limitRegister": "false"
            })
        elif choose_url =='pre':
            if TransferId == "0":
                pageLink="https://pay-test.61info.cn/maliang-pre/popularize-50585.htm"
            else:
                transfer_id = UserComingRun().getBizId(TransferId, choose_url, 3)
                pageLink="https://pay-test.61info.cn/maliang-pre/popularize-50585.html?business_Type=checkIn&channelId=22&courseBelong=WANDOU&courseSubjectType=1&fissionInviteConfigId=46&invite_userID="+str(transfer_id)+"&locale=zh-CN&popularId=50585&popularizeId=50585"
            if choose_type =='appoint':
                usermobile = mobile
            else:
                usermobile = orderNum
            payload = json.dumps({
                "terminal": "WEB",
                "pageLink": pageLink,
                "telCode": int(areaCode),
                "countryCode": "",
                "mobile": usermobile,
                "captcha": "111111",
                "channel": "PLATFORM"
            })
        response = requests.request("POST", sign_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        # print("getSign接口的请求体：",payload)
        # print("getSign接口返回内容：",re)
        biz_user_id = re['data']['id'],

        accessToken = re['data']['accessToken'],
        mobile = re['data']['mobile']
        print("res"+mobile)
        return biz_user_id,accessToken,mobile

    #第一步-提交学员进线
    def submitUserComing(self,accessToken,biz_user_id,choose_url,choose_subject,TransferId):
        global payload
        gw_url = getConfig("liuyi-url-1",choose_url)
        url_path = '/bizcenter-order-backend/o/v1/order/placeOrder'
        if choose_url =='test':
            if choose_subject=='VIP_WanDou':
                # "https://market-h5-test.61info.cn/maliang-test/popularize-91251.html?business_Type=lottery&courseBelong=WANDOU&courseSubjectType=2&fissionInviteConfigId=1027&invite_userID=3010064580&popularizeId=91251"
                payload = json.dumps({
                  "pageUrl": "https://market-h5-test.61info.cn/maliang-test/popularize-91251.html",
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 1277,
                  "num": 1,
                  "popularizeId": 91251,
                  "returnUrl": "https://market-h5-test.61info.cn/maliang-test/popularize-91251.html?bizToken=PLATFORM-WEB-3028511972-ee4b984cd65e4ce7be75aa49c1355786&bizChannel=PLATFORM&interactiveConfig=%7B%22action%22%3A%22comp%3ApurchaseEvent%22%2C%22content%22%3A%22purchaseEvent%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22duration%22%3A3%2C%22afterInteractive%22%3A%7B%22action%22%3A%22link%22%2C%22content%22%3A%22https%3A%2F%2Fpay-test.61info.cn%2Fmaliang-pre%2F999-93c72433ef.html%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%7D%2C%22conditionsForSuccess%22%3A%22%22%2C%22orderSuccess%22%3A%7B%22action%22%3A%22%22%2C%22content%22%3A%22%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22duration%22%3A3%2C%22afterInteractive%22%3A%7B%22action%22%3A%22link%22%2C%22content%22%3A%22https%3A%2F%2Fpay-test.61info.cn%2Fmaliang-pre%2F999-93c72433ef.html%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%7D%7D%7D",
                  "formData": {},
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
                # payload = json.dumps({
                #   "pageUrl": "https://market-h5-test.61info.cn/maliang-test/popularize-91251.html?business_Type=lottery&courseBelong=WANDOU&courseSubjectType=2&fissionInviteConfigId=1027&invite_userID=3010064580&popularizeId=91251",
                #   "activityId": 'null',
                #   "activityType": 1,
                #   "addPurchaseActivityReq": {
                #     "addGoods": []
                #   },
                #   "channelCode": "PLATFORM",
                #   "displayActualAmount": 0,
                #   "goodsId": 1277,
                #   "num": 1,
                #   "popularizeId": "91251",
                #   "returnUrl": "https://market-h5-test.61info.cn/maliang-test/popularize-91251.html?business_Type=lottery&courseBelong=WANDOU&courseSubjectType=2&fissionInviteConfigId=1027&invite_userID=3010064580&popularizeId=91251&bizToken=PLATFORM-WEB-3028513125-ffd5729bc40649b580030c0bbec680e9&bizChannel=PLATFORM&interactiveConfig=%7B%22action%22%3A%22comp%3ApurchaseEvent%22%2C%22content%22%3A%22purchaseEvent%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22duration%22%3A3%2C%22afterInteractive%22%3A%7B%22action%22%3A%22link%22%2C%22content%22%3A%22https%3A%2F%2Fpay-test.61info.cn%2Fmaliang-pre%2F999-93c72433ef.html%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%7D%2C%22conditionsForSuccess%22%3A%22%22%2C%22orderSuccess%22%3A%7B%22action%22%3A%22%22%2C%22content%22%3A%22%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22duration%22%3A3%2C%22afterInteractive%22%3A%7B%22action%22%3A%22link%22%2C%22content%22%3A%22https%3A%2F%2Fpay-test.61info.cn%2Fmaliang-pre%2F999-93c72433ef.html%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%7D%7D%7D",
                #   "formData": {},
                #   "price": 0,
                #   "extraInfo": {
                #     "bizUserIdMap": {
                #       "PLATFORM": biz_user_id
                #     }
                #   }
                # })
            elif choose_subject=='VIP_YuWen':
                payload = json.dumps({
                  "pageUrl": "https://pay-test.61info.cn/maliang-test/popularize-91272.html",
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 1755,
                  "num": 1,
                  "popularizeId": 91272,
                  "returnUrl": "https://pay-test.61info.cn/maliang-test/popularize-91272.html?bizToken=PLATFORM-WEB-3028512246-ee43da23cad9488ea4888a07cc7ffee9&bizChannel=PLATFORM&interactiveConfig=%7B%22action%22%3A%22comp%3ApurchaseEvent%22%2C%22content%22%3A%22purchaseEvent%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22conditionsForSuccess%22%3A%22%22%2C%22orderSuccess%22%3A%7B%22action%22%3A%22toast%22%2C%22content%22%3A%22%E9%A2%86%E5%8F%96%E6%88%90%E5%8A%9F~%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22duration%22%3A%224%22%2C%22afterInteractive%22%3A%7B%22action%22%3A%22toPlatformStudyPrepare%22%2C%22content%22%3A%22%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%7D%7D%7D",
                  "formData": {
                    "age": 3,
                    "grade": 'null'
                  },
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
            elif choose_subject=='VIP_MoLi':
                payload = json.dumps({
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 1321,
                  "num": 1,
                  "popularizeId": 12916,
                  "returnUrl": "https://market-h5-test.61info.cn/maliang-test/popularize-12916.html?",
                  "channelId": "166",
                  "formData": {
                    "age": 3
                  },
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
            elif choose_subject=='VIP_MagicCambridge':
                payload = json.dumps({
                  "pageUrl": "https://market-h5-test.61info.cn/maliang-test/server/POPULARIZE/90789",
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 1963,
                  "num": 1,
                  "popularizeId": 90789,
                  "returnUrl": "https://market-h5-test.61info.cn/maliang-test/server/POPULARIZE/90789?",
                  "channelId": "21231",
                  "formData": {},
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
            elif choose_subject=='VIP_XinLi':
                payload = json.dumps({
                  "pageUrl": "https://market-h5-test.61info.cn/maliang-test/server/POPULARIZE/90867",
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 1964,
                  "num": 1,
                  "popularizeId": 90867,
                  "returnUrl": "https://market-h5-test.61info.cn/maliang-test/server/POPULARIZE/90867?",
                  "channelId": "21240",
                  "formData": {},
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
            else:
                payload = json.dumps({
                  "pageUrl": "https://pay-test.61info.cn/maliang-test/popularize-91160.html",
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 2018,
                  "num": 1,
                  "popularizeId": 91160,
                  "returnUrl": "https://pay-test.61info.cn/maliang-test/popularize-91160.html?bizToken=PLATFORM-WEB-3028511479-1d55d4f5e7cd4cb1b51df1356955caf1&bizChannel=PLATFORM&interactiveConfig=%7B%22action%22%3A%22comp%3ApurchaseEvent%22%2C%22content%22%3A%22purchaseEvent%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22conditionsForSuccess%22%3A%22%22%2C%22orderSuccess%22%3A%7B%22action%22%3A%22toast%22%2C%22content%22%3A%22%E9%A2%86%E5%8F%96%E6%88%90%E5%8A%9F~%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22duration%22%3A%224%22%2C%22afterInteractive%22%3A%7B%22action%22%3A%22toPlatformStudyPrepare%22%2C%22content%22%3A%22%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%7D%7D%7D",
                  "formData": {
                    "age": 3
                  },
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
        elif choose_url =='pre':
            if choose_subject=='VIP_WanDou':
                # payload = json.dumps({
                #   "activityId": 122,
                #   "activityType": 1,
                #   "addPurchaseActivityReq": {
                #     "addGoods": []
                #   },
                #   "channelCode": "PLATFORM",
                #   "displayActualAmount": 0,
                #   "goodsId": 188,
                #   "num": 1,
                #   "popularizeId": 36590,
                #   "returnUrl": "https://market-h5-pre.61info.cn/maliang-pre/popularize-36590.html?",
                #   "channelId": "206",
                #   "formData": {
                #     "age": "5"
                #   },
                #   "price": 0,
                #   "extraInfo": {
                #     "bizUserIdMap": {
                #       "PLATFORM": biz_user_id
                #     }
                #   }
                # })
                payload = json.dumps({
                  "pageUrl": "https://pay-test.61info.cn/maliang-pre/popularize-50585.html",
                  "activityId": 206,
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 567,
                  "num": 1,
                  "popularizeId": 50585,
                  "returnUrl": "https://pay-test.61info.cn/maliang-pre/popularize-50585.html?",
                  "channelId": "1293",
                  "formData": {
                    "age": 1,
                    "grade": 'null'
                  },
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                }
                )
            elif choose_subject=='VIP_YuWen':
            #     payload = json.dumps({
            #       "pageUrl": "https://static-h5-pre.61info.cn/maliang-pre/popularize-14199.html",
            #       "activityId": 'null',
            #       "activityType": 1,
            #       "addPurchaseActivityReq": {
            #         "addGoods": []
            #       },
            #       "channelCode": "PLATFORM",
            #       "displayActualAmount": 0,
            #       "goodsId": 145,
            #       "num": 1,
            #       "popularizeId": 14199,
            #       "returnUrl": "https://static-h5-pre.61info.cn/maliang-pre/popularize-14199.html?bizToken=PLATFORM-WEB-3003575878-2595e3a2a1ef43caa20afb88f1778fc0&bizChannel=PLATFORM&interactiveConfig=%7B%22action%22%3A%22comp%3ApurchaseEvent%22%2C%22content%22%3A%22purchaseEvent%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22conditionsForSuccess%22%3A%22%22%2C%22orderSuccess%22%3A%7B%22action%22%3A%22%22%2C%22content%22%3A%22%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%7D%7D",
            #       "formData": {},
            #       "price": 0,
            #       "extraInfo": {
            #         "bizUserIdMap": {
            #           "PLATFORM": biz_user_id
            #         }
            #       }
            #     })
                payload = json.dumps({
                  "pageUrl": "https://pay-test.61info.cn/maliang-pre/popularize-50908.html",
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 224,
                  "num": 1,
                  "popularizeId": 50908,
                  "returnUrl": "https://pay-test.61info.cn/maliang-pre/popularize-50908.html?",
                  "channelId": "1293",
                  "formData": {
                    "age": 3,
                    "grade": 'null'
                  },
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
            elif choose_subject=='VIP_MoLi':
                payload = json.dumps({
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 228,
                  "num": 1,
                  "popularizeId": 14215,
                  "returnUrl": "https://market-h5-pre.61info.cn/maliang-pre/popularize-14215.html?",
                  "channelId": "129",
                  "formData": {
                    "age": 4
                  },
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
            elif choose_subject=='VIP_MagicCambridge':
                payload = json.dumps({
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 564,
                  "num": 1,
                  "popularizeId": 45668,
                  "returnUrl": "https://market-h5-pre.61info.cn/maliang-pre/popularize-45668.html?bizToken=PLATFORM-WEB-3003575880-a32ef64908344a129fde9d11b0b4a48d&bizChannel=PLATFORM&interactiveConfig={\"action\":\"comp:purchaseEvent\",\"content\":\"purchaseEvent\",\"customPopup\":\"\",\"customPopupEvent\":\"\",\"params\":[]}",
                  "formData": {},
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
            elif choose_subject=='VIP_XinLi':
                payload = json.dumps({
                  "pageUrl": "https://market-h5-pre.61info.cn/maliang-pre/popularize-50040.html",
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 577,
                  "num": 1,
                  "popularizeId": 50040,
                  "returnUrl": "https://market-h5-pre.61info.cn/maliang-pre/popularize-50040.html?",
                  "channelId": "21",
                  "formData": {
                    "age": "16"
                  },
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
            else:
                payload = json.dumps({
                  "pageUrl": "https://market-h5-pre.61info.cn/maliang-pre/popularize-50041.html",
                  "activityId": 'null',
                  "activityType": 1,
                  "addPurchaseActivityReq": {
                    "addGoods": []
                  },
                  "channelCode": "PLATFORM",
                  "displayActualAmount": 0,
                  "goodsId": 578,
                  "num": 1,
                  "popularizeId": 50041,
                  "returnUrl": "https://market-h5-pre.61info.cn/maliang-pre/popularize-50041.html?",
                  "channelId": "21",
                  "formData": {
                    "age": "16"
                  },
                  "price": 0,
                  "extraInfo": {
                    "bizUserIdMap": {
                      "PLATFORM": biz_user_id
                    }
                  }
                })
        # headers= {
        #     'content-Type': 'application/json',
        #     'auth': accessToken,
        # }
        if TransferId == "0":
            print("TransferId:" + TransferId)
            headers = {
                'content-Type': 'application/json',
                'Auth': accessToken,
            }
        else:
            transfer_id = self.GetPlatformUserid(choose_url,TransferId,str("WANDOU"))
            # transfer_id = UserComingRun().getBizId(TransferId, choose_url, 3)
            if transfer_id != int(0):
                if choose_url == 'test':
                    cookie="_ga=GA1.2.1849005566.1709897342; _ga_D1FM8TW3RM=GS1.1.1722936724.3.1.1722936929.44.0.0; _ga_PKC3YZCYQ0=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_S200MHJ9H3=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_9NT8CGDND8=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_VMYC3SS2SE=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_0C9G9JD0YT=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_25C04NL7R4=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_LBJJYH0K3G=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_B5BTT07LP1=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_2N593TT8CR=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_HYLVLTP58J=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_Y4K746K2LW=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_YHS3JESL36=GS1.1.1722936724.3.1.1722936929.45.0.0; _ga_9LCSSXV2KP=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_WJKV9R3RVW=GS1.1.1722936724.3.1.1722936929.0.0.0; _gcl_au=1.1.119426728.1732782500; _fbp=fb.1.1732786394243.55125292262667820; LtpaToken=AAECAzY3NjI3NDA2Njc2MzFDQzYxNTU0Njc5NjY4MB6Ew9kDrJbNQxjFxLW2OijAmfQv; popularUrl=https%253A%252F%252Fmarket-h5-test.61info.cn%252Fmaliang-test%252Fpopularize-91251.html%253Fbusiness_Type%253Dlottery%2526courseBelong%253DWANDOU%2526courseSubjectType%253D2%2526fissionInviteConfigId%253D1027%2526invite_userID%253D"+str(transfer_id)+"%2526popularizeId%253D91251; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%223028513125%22%2C%22first_id%22%3A%2218deec60abfc8f-062353c9c7ac484-26001851-2073600-18deec60ac0822%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThkZWVjNjBhYmZjOGYtMDYyMzUzYzljN2FjNDg0LTI2MDAxODUxLTIwNzM2MDAtMThkZWVjNjBhYzA4MjIiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIzMDI4NTEzMTI1In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%223028513125%22%7D%2C%22%24device_id%22%3A%2218deec60abfc8f-062353c9c7ac484-26001851-2073600-18deec60ac0822%22%7D"
                    payload = json.dumps({
                      "pageUrl": "https://market-h5-test.61info.cn/maliang-test/popularize-91251.html?business_Type=lottery&courseBelong=WANDOU&courseSubjectType=2&fissionInviteConfigId=1027&invite_userID=3010064580&popularizeId=91251",
                      "activityId": 'null',
                      "activityType": 1,
                      "addPurchaseActivityReq": {
                        "addGoods": []
                      },
                      "channelCode": "PLATFORM",
                      "displayActualAmount": 0,
                      "goodsId": 1277,
                      "num": 1,
                      "popularizeId": "91251",
                      "returnUrl": "https://market-h5-test.61info.cn/maliang-test/popularize-91251.html?business_Type=lottery&courseBelong=WANDOU&courseSubjectType=2&fissionInviteConfigId=1027&invite_userID=" + str(transfer_id) + "&popularizeId=91251&bizToken=PLATFORM-WEB-3028513125-ffd5729bc40649b580030c0bbec680e9&bizChannel=PLATFORM&interactiveConfig=%7B%22action%22%3A%22comp%3ApurchaseEvent%22%2C%22content%22%3A%22purchaseEvent%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22duration%22%3A3%2C%22afterInteractive%22%3A%7B%22action%22%3A%22link%22%2C%22content%22%3A%22https%3A%2F%2Fpay-test.61info.cn%2Fmaliang-pre%2F999-93c72433ef.html%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%7D%2C%22conditionsForSuccess%22%3A%22%22%2C%22orderSuccess%22%3A%7B%22action%22%3A%22%22%2C%22content%22%3A%22%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%2C%22duration%22%3A3%2C%22afterInteractive%22%3A%7B%22action%22%3A%22link%22%2C%22content%22%3A%22https%3A%2F%2Fpay-test.61info.cn%2Fmaliang-pre%2F999-93c72433ef.html%22%2C%22customPopup%22%3A%22%22%2C%22customPopupEvent%22%3A%22%22%2C%22params%22%3A%5B%5D%7D%7D%7D",
                      "formData": {},
                      "price": 0,
                      "extraInfo": {
                        "bizUserIdMap": {
                          "PLATFORM": biz_user_id
                        }
                      }
                    })
                else:
                    print(transfer_id)
                    cookie="_ga=GA1.2.1849005566.1709897342; _ga_D1FM8TW3RM=GS1.1.1722936724.3.1.1722936929.44.0.0; _ga_PKC3YZCYQ0=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_S200MHJ9H3=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_9NT8CGDND8=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_VMYC3SS2SE=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_0C9G9JD0YT=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_25C04NL7R4=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_LBJJYH0K3G=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_B5BTT07LP1=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_2N593TT8CR=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_HYLVLTP58J=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_Y4K746K2LW=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_YHS3JESL36=GS1.1.1722936724.3.1.1722936929.45.0.0; _ga_9LCSSXV2KP=GS1.1.1722936724.3.1.1722936929.0.0.0; _ga_WJKV9R3RVW=GS1.1.1722936724.3.1.1722936929.0.0.0; _gcl_au=1.1.119426728.1732782500; _fbp=fb.1.1732786394243.55125292262667820; LtpaToken=AAECAzY3NjI3NDA2Njc2MzFDQzYxNTU0Njc5NjY4MB6Ew9kDrJbNQxjFxLW2OijAmfQv; popularUrl=https%253A%252F%252Fpay-test.61info.cn%252Fmaliang-pre%252Fpopularize-50585.html%253Fbusiness_Type%253DcheckIn%2526channelId%253D22%2526courseBelong%253DWANDOU%2526courseSubjectType%253D1%2526fissionInviteConfigId%253D46%2526invite_userID%253D"+str(transfer_id)+"%2526locale%253Dzh-CN%2526popularId%253D50585%2526popularizeId%253D50585; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%223003579539%22%2C%22first_id%22%3A%2218deec60abfc8f-062353c9c7ac484-26001851-2073600-18deec60ac0822%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThkZWVjNjBhYmZjOGYtMDYyMzUzYzljN2FjNDg0LTI2MDAxODUxLTIwNzM2MDAtMThkZWVjNjBhYzA4MjIiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIzMDAzNTc5NTM5In0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%223003579539%22%7D%2C%22%24device_id%22%3A%2218deec60abfc8f-062353c9c7ac484-26001851-2073600-18deec60ac0822%22%7D"
                    payload = json.dumps(
                        {
                            "pageUrl": "https://pay-test.61info.cn/maliang-pre/popularize-50585.html?business_Type=checkIn&channelId=22&courseBelong=WANDOU&courseSubjectType=1&fissionInviteConfigId=46&invite_userID=3003499763&locale=zh-CN&popularId=50585&popularizeId=50585",
                            "activityId": 'null',
                            "activityType": 1,
                            "addPurchaseActivityReq": {
                                "addGoods": []
                            },
                            "channelCode": "PLATFORM",
                            "displayActualAmount": 0,
                            "goodsId": 229,
                            "num": 1,
                            "popularizeId": "50585",
                            "returnUrl": "https://pay-test.61info.cn/maliang-pre/popularize-50585.html?business_Type=checkIn&channelId=22&courseBelong=WANDOU&courseSubjectType=1&fissionInviteConfigId=46&invite_userID=" + str(transfer_id) + "&locale=zh-CN&popularId=50585&popularizeId=50585",
                            "channelId": "1293",
                            "formData": {
                              "age": 1,
                              "grade": 'null'
                            },
                            "price": 0,
                            "extraInfo": {
                                "bizUserIdMap": {
                                    "PLATFORM": biz_user_id
                                }
                            }
                        }
                    )
            else:
                return "查询不到转介绍上级学员的平台id，学员进线失败！"
            headers = {
                'content-Type': 'application/json',
                'Auth': accessToken,
                'Cookie': cookie
            }
        response = requests.request("POST", gw_url + url_path, headers=headers, data=payload)

        re = json.loads(response.text)
        print(re)
        if re['code'] != 0:
            print("进线失败",re)
            return re
        else:
            return re

    #仅申请退款，但退款待审核
    def UserComingRuning(self,choose_url,choose_type,mobile,choose_subject,coming_number,areaCode,TransferId):
        global result, coming_result
        try:
            numbers_list = []
            if choose_type =='appoint':
                coming_number = 1
            for i in range(int(coming_number)):
                print(f"这是第 {i + 1} 次循环")
                orderNum = self.get_datemobile()
                numbers_list.append(int(orderNum))
                biz_user_info=self.GetBizUserid(orderNum,choose_url,choose_type,mobile,areaCode,TransferId)
                biz_user_id = biz_user_info[0][0]
                accessToken = biz_user_info[1][0]
                # mobile1 = biz_user_info[2][0]
                coming_result = self.submitUserComing(accessToken, biz_user_id, choose_url,choose_subject,TransferId)
            if choose_type =='appoint':
                 result = "手机号："+mobile
            else:
                result = "手机号：" + str(numbers_list)
                print(numbers_list)
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
    choose_subject="VIP_WanDou"
    choose_url = "test" # test, pro
    choose_type = "random"
    biz_user_id ='3028494873'
    accessToken = 'eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjoid251bHQ2Y1NXV2wxMzBRS25zZlJrSCtVQjR4OHRpZW00M2tYajVDTkZTaE5GcU1weWZMUVlTQjBKUzdCWnhDclJMZjdaT0MvM2llZ01WWnBDYnVJWk05YkFyTEpnYk5ncDVjdnV4TmYvcHc1RFFPS1RxRTlOQlQ5eklvL1gra3J2Wm1aUVNYQnd1YjB1V2N1eWQxa0hod1U4VDlSM3Z5Qk9iZ1JLSXdsZERCSVA2YnVDcXhtVWpRUERoajlqSzRRT0YzSlBFQUxpNERBWEppbkJOcEhSLzFuditXT0xXRHJ1T0pjcExOYkUrQVhZNVJjbTI3UU9OYW1NZFkyQXZGY1U5dFh6bGRQMGNpT25BenhlRXFoQVhYa0czb0lneW1hTnhnL0R3UkFDTy9UVG5LSEVYMWc4ZWcwejAvU0paOWVjQXhHRFE1dHRnWWtVNVZNckU4MzJZZnBKWEpiR2JUQm9KbVRscXBZNGFpa3I3MnEveHBTZGhXVEpQbm1vZkttIiwiZXhwIjoxNzQxNzY5NjY0fQ.7fyKBw_GQwOgzIsYXelOJ_9n6S-ctFChuwK_rru-lPY'
    mobile = '13020009149'
    orderNum='13020241138'
    refundPrice = 0.01
    coming_number=1
    TransferId=""
    re = WanDouUserComingRun().UserComingRuning(choose_url,choose_type,mobile,choose_subject,coming_number,86,TransferId)
    # re=WanDouUserComingRun().listChannels(choose_url,481699)
    # re= UserComingRun().GetBizUserid(orderNum,choose_url,choose_type,mobile)
    # re=UserComingRun().submitUserComing(accessToken,biz_user_id,choose_url)
    print("执行结束88,")
    print(re)


