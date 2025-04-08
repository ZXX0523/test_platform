from conf.readconfig import getConfig
from lib.py.order_V2_script import *
import requests
import json
import pandas as pd
import os, time

# import oss2
# from qcloud_cos import CosConfig
# from qcloud_cos import CosS3Client

from conf.readconfig import *

class RedundOrder():
    #获取签名sign接口
    def getSign(self,data,choose_url):
        sign_url = getConfig("sign-url",choose_url)
        url_path = '/assets/v1/signature/get'
        payload = data
        headers = {
            'content-type': 'application/json',
            'appid': '46620464',
            'Authorization': 'EFXfxsRDN9EwQXvqrMDWkboJT9E9btZl',
            'key': '40g3ndAr2a9mHrTdJbNEapT5sjLmr1uX'
        }
        response = requests.request("POST", sign_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        # print("getSign接口的请求体：",payload)
        # print("getSign接口返回内容：",re)
        sign = re['data']['v1']
        return sign
        print("获取到的sign:",sign)

    #第一步-内部提交退费申请
    def submitRefundApply(self,orderNum,refundPrice,sign1,choose_url):
        gw_url = getConfig("gateway-url",choose_url)
        url_path = '/api/order/v1/collection-refund/internal/submitRefundApply'
        payload = json.dumps({"createAdminUser": 666954,
                "detainmentResult": "refund33",
                "orderNumber": orderNum,
                "refundFileUrl": "https://cc-vipthink-pub.oss-cn-beijing.aliyuncs.com/invoice_order1574481642127.jpg",
                "refundPrice": refundPrice,
                "refundReason": "refundtest",
                "refundType": 1,
                "sysRefundPrice": refundPrice
            })
        headers= {
            'content-Type': 'application/json',
            'appid': '46620464',
            'sign': sign1,
            'x-auth-type': 'sign'
        }
        response = requests.request("POST", gw_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        # print("内部提交退费申请接口的请求头：",headers)
        # print("内部提交退费申请接口的请求体：",payload)
        # print("内部提交退费申请接口响应数据：",re)
        if re['code'] != 0:
            print("内部提交退费申请失败",re)
            return re
        else:
            return re
            # collectionRefundNo = re['data']['collectionRefundNo']
            # oldRefundId = re['data']['oldRefundId']
            # print("获取到collectionRefundNo：",collectionRefundNo)
            # return collectionRefundNo, oldRefundId

        # if collectionRefundNo is None:
        #     print("获取不到collectionRefundNo")
        # else:
        #     print("获取到collectionRefundNo：",collectionRefundNo)
        # return collectionRefundNo,oldRefundId

    #第二步-内部审核退费回调
    def refundApprovalCallBack(self,sign2,orderNum,collectionRefundNo,oldRefundId,choose_url):
        gw_url = getConfig("gateway-url",choose_url)
        url_path = '/api/order/v1/collection-refund/internal/refundApprovalCallBack'
        payload = json.dumps({ "approvalStatus": 2,
                "collectionRefundOrderNumber": collectionRefundNo,
                "orderNumber": orderNum,
                "refundOrderId": oldRefundId,
                "refundType": 1
            })
        headers = {
            'content-Type': 'application/json',
            'appid': '46620464',
            'sign': sign2,
            'x-auth-type': "sign"
        }
        response = requests.request("POST", gw_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        message = re['message']
        if message != "操作成功":
            print("退款回调失败：",re)
            return re
        else:
            print("退款回调成功")
            return re


   #第三步-原路退费
    def toRefund(self,sign3,orderNum,collectionRefundNo,oldRefundId,choose_url):
        gw_url = getConfig("gateway-url",choose_url)
        url_path = '/api/order/v1/collection-refund/toRefund'
        payload = json.dumps({
                "collectionRefundOrderNumber": collectionRefundNo,
                "refundOrderId": oldRefundId,
                "refundType": 1,
                "orderNumber": orderNum
            })
        headers = {
            'content-Type': 'application/json',
            'appid': '46620464',
            'sign': sign3,
            'x-auth-type': "sign"
        }
        response = requests.request("POST", gw_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        message = re['message']
        if message != "操作成功":
            print("退款失败：",re)
            return re
        else:
            print("退款成功")
            return re
    #获取token
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
        re = json.loads(response.text)
        try:
            return re['data']['token'],re['data']['uid']
        except KeyError as e:
            # 异常时，执行该块
            return False, e
            pass

    #获取退费审核子订单号
    def getqueryRefundApprovalInfo(self,no,Authorization,choose_url):
        order_url = getConfig("order-url",choose_url)
        url_path = '/order/v1/collection-refund/queryRefundApprovalInfo'
        params = {
            'no': no
        }
        headers = {
            'content-Type': 'application/json',
            'authorization': Authorization
        }
        response = requests.get(url=order_url + url_path, headers=headers, params=params)
        re = json.loads(response.text)
        message = re['message']
        if message != "操作成功":
            print("获取退费审核子订单号失败")
        else:
            orderChildNumber = re['data']['payDetailVos'][0]['orderChildNumber']
            print("获取退费审核子订单号成功:",orderChildNumber)
        return orderChildNumber

    #获取退费审核no
    def getpageRefundList(self,orderNumber,Authorization):
        order_url = getConfig("order-url", choose_url)
        url_path = '/order/v1/collection-refund/pageRefundList'
        params = {
            'refundType': 1,
            'page': 1,
            'limit': 20,
            'orderNumber': orderNumber
        }
        headers = {
            'content-Type': 'application/json',
            'authorization': Authorization
        }
        response = requests.get(url=order_url + url_path, headers=headers, params=params)
        re = json.loads(response.text)
        print(re)
        message = re['message']
        if message != "操作成功":
            print("获取退费审核no失败")
        else:
            no = re['data'][0]['no']
            print("获取退费审核no成功：",no)
        return no

    #审核退费订单
    def confirmRefund(self,orderChildNumber,no,refundPrice,Authorization,choose_url):
        order_url = getConfig("order-url", choose_url)
        url_path = '/order/v1/collection-refund/confirmRefund'
        payload = json.dumps({
                "collectionDetailDtoList": [{
                    "orderChildNumber": orderChildNumber,
                    "refundType": 3,
                    "remarks": "",
                    "preRefundPrice": refundPrice
                }],
                "no": no
            })
        headers = {
            'content-Type': 'application/json',
            'authorization': Authorization
        }
        response = requests.post(url=order_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        message = re['message']
        if message != "操作成功":
            print("退费订单审批成功")
        else:
            print("退费订单审批失败")



    def get_data1(self,orderNum,refundPrice):
        data1 = json.dumps({"createAdminUser": 666954,
                "detainmentResult": "refund33",
                "orderNumber": orderNum,
                "refundFileUrl": "https://cc-vipthink-pub.oss-cn-beijing.aliyuncs.com/invoice_order1574481642127.jpg",
                "refundPrice": refundPrice,
                "refundReason": "refundtest",
                "refundType": 1,
                "sysRefundPrice": refundPrice
            })
        return data1


    def get_data2(self,collectionRefundNo,oldRefundId,orderNum):
        data2 = json.dumps({ "approvalStatus": 2,
            "collectionRefundOrderNumber": collectionRefundNo,
            "orderNumber": orderNum,
            "refundOrderId": oldRefundId,
            "refundType": 1
        })
        return data2

    def get_data3(self,collectionRefundNo,oldRefundId,orderNum):
         data3 = json.dumps({
            "collectionRefundOrderNumber": collectionRefundNo,
            "refundOrderId": oldRefundId,
            "refundType": 1,
            "orderNumber": orderNum
        })
         return data3

    #仅申请退款，但退款待审核
    def refun(self,orderNum,refundPrice,choose_url):
        try:
            data1 = self.get_data1(orderNum, refundPrice)
            print("第一个data1:", data1)
            sign1 = self.getSign(data1,choose_url)
            print("第一个sign1:", sign1)
            refund_info_result = self.submitRefundApply(orderNum, refundPrice, sign1,choose_url)
            print("打印refund_info_result",refund_info_result)
            if refund_info_result['message'] != "操作成功":
                return refund_info_result
            else :
                collectionRefundNo = refund_info_result['data']['collectionRefundNo']
                oldRefundId = refund_info_result['data']['oldRefundId']
                data2 = self.get_data2(collectionRefundNo, oldRefundId,orderNum)
                sign2 = self.getSign(data2,choose_url)
                callback_result = self.refundApprovalCallBack(sign2, orderNum, collectionRefundNo, oldRefundId,choose_url)
                data3 = self.get_data3(collectionRefundNo, oldRefundId,orderNum)
                sign3 = self.getSign(data3, choose_url)
                torefund_result = self.toRefund(sign3, orderNum, collectionRefundNo, oldRefundId, choose_url)
                return torefund_result

            # return True, "Success"
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
    # Authorization = ''
    orderNum = '20220615142147676356870'
    refundPrice = 0.01
    re = RedundOrder().refun(orderNum, refundPrice,choose_url)
    print("执行结束88,",re)


