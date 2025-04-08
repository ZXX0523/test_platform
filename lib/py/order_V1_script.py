# coding:utf-8
import json
import locale
import requests
import sys
import oss2
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import pandas as pd
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder
from conf.readconfig import *

# 文件地址
import_excel_path = rootPath() + "/docs/import_files/"
order_error_code = (10000004,10000006,500003,9000004,500005)
class orderImportPackageV1():
    def orderV1Xlsx(self,name,area_code,phone,hourId,hour_price,channel_id,filename=None):
        i=0
        title = ["*外部订单号","*用户姓名","*手机区号","*手机号","学员ID","渠道ID","*套餐ID","*订单支付金额","*支付时间","*支付方式","*收款渠道ID","获得原因","父订单号","扩展信息","*是否需要地址","收件人","国家","联系电话","省","市","区","详细地址","活动ID"]
        df = pd.DataFrame(columns=title)
        now_time = time.localtime()
        df.loc[1] = title

        while i != len(name):
            imputInfo = [int(time.strftime("%Y%m%d%H%M%S", now_time))+i+1,name[i],area_code[i],phone[i],"",channel_id,hourId,hour_price,
                         time.strftime("%Y-%m-%d %H:%M:%S", now_time),"第三方售卖",12,1999,"",
                         "{\"ad_id\":\"123\",\"team_id\":\"123\"}",0,"","","","","","","",""]
            df.loc[i + 2] = imputInfo
            i = i + 1


        xlsx_name = time.strftime("%Y{Y}%m{m}%d{d}",now_time).format(Y='年',m='月',d='日') + "-商品V1测试-" + time.strftime("%Y{Y}%m{m}%d{d}%H{H}%M{M}%S{S}",now_time).format(Y='年',m='月',d='日',H='时',M='分',S='秒') + ".xlsx"
        df.to_excel(import_excel_path+xlsx_name, sheet_name='导入主表', index=False)
        size_B = os.path.getsize(import_excel_path+xlsx_name)
        # print(import_excel_path+xlsx_name)
        print("xlsx生成成功！"+str(size_B))
        return xlsx_name,size_B

    # 获取CRMtoken
    def getCrmToken(self, choose_url):
        auth_url = getConfig("auth-url", choose_url)
        url_path = "/v1/auth/admin/token"
        payload = json.dumps({
               "username": getConfig("crm-login", choose_url + "_phone"),
            "password": getConfig("crm-login", choose_url + "_pwd"),
            "__fields": "token,uid"
        })
        headers = {
                'content-type': 'application/json'
        }
        response = requests.request("POST", auth_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        print("获取token：", re)
        try:
            return re['data']['token'], re['data']['uid']
        except KeyError as e:
            # 异常时，执行该块
            return False, e

    # 导入Excel
    def importV1(self, choose_url, Authorization, file_name):
        order_url = getConfig("order-url", choose_url)
        url_path = '/order/v1/order/import'
        headers = {
            'content-type': 'multipart/form-data; boundary=${boundary}',
            'authorization': Authorization
        }
        form_data = MultipartEncoder(
            fields={
                'file': ('豌豆商品V1导入.xlsx', open(import_excel_path + file_name, 'rb'),
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            })
        headers.update({'content-type': form_data.content_type})
        response = requests.post(order_url + url_path, data=form_data, headers=headers)
        re = json.loads(response.text)
        print("打印导入Excel结果：",re)
        importNum = re['data']['importNum']
        if importNum == '':
            print("导入excel失败")
            return False, "false"
        else:
            print("导入excel成功")
            return importNum

    #检查导入是否成功
    def checkStatus(self,choose_url,Authorization,importNum):
        order_url = getConfig("order-url", choose_url)
        url_path = '/order/v1/order/importResultList'
        payload = json.dumps({
            'importNum':importNum,
            'status':2,
            'page':1,
            'limit':100
        })
        headers = {
            'content-type':'application/json',
            'authorization':Authorization
        }
        response = requests.request("POST", order_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)

        data_info = re['data']['data']
        print("data_info:",data_info)
        allNum = re['data']['allNum']
        print("allNum:",allNum)
        checkMsg = []
        for i in range(0,int(allNum)):
            checkMsg.append(re['data']['data'][i]['checkMsg'])
        print("checkMsg:",checkMsg)
        if checkMsg == [None]:
            print("导入校验成功！")
        else:
            print("导入校验失败！")
        return allNum


    #提交审核
    def orderConfirm(self,choose_url,Authorization,allNum,importNum):
        order_url = getConfig("order-url", choose_url)
        url_path = '/order/v1/order/orderConfirm'
        payload = json.dumps({
            "explainContent":"测试",
            "importNum":importNum
        })
        headers = {
            'content-type': 'application/json',
            'authorization': Authorization
        }
        response = requests.request("POST", order_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        re_msg = re['message']
        print("打印提交审核结果：",re)
        if re_msg == '操作成功':
            print("提交审核成功，待审核！")
            # return re_msg
        else:
            print("提交审核失败！")
            # return re_msg

    #待审核明细
    def importDetailList(self,choose_url,Authorization,importNum):
        order_url = getConfig("order-url", choose_url)
        url_path = '/order/v1/order/importDetailList'
        payload = json.dumps({
            "status":1,
            "page":1,
            "limit":100,
            "importNum":importNum
        })
        headers = {
            'content-type': 'application/json',
            'authorization': Authorization
        }
        response = requests.request("POST", order_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        import_data_info = re['data']['data']
        ids = []
        allNum = re['data']['allNum']
        for i in range(0,allNum):
            ids.append(re['data']['data'][i]['id'])
            # print(ids)
        return ids,import_data_info

    #导入审批通过
    def handleMetadata(self,choose_url,Authorization,importNum,ids):
        order_url = getConfig('order-url',choose_url)
        url_path = '/order/v1/order/handleMetadata'
        payload = json.dumps({
            "handleType":1,
            "metadataIdList":ids,
            "importNum":importNum
        })
        headers = {
            'content-type': 'application/json',
            'authorization': Authorization
        }
        print("导入审核请求体：",payload)
        response = requests.request("POST", order_url + url_path, headers=headers, data=payload)
        re = json.loads(response.text)
        print("导入审核结果：",re)
        re_msg = re['message']
        if re_msg == "操作成功":
            print("导入审批完成")
            return True, "Success"
        else:
            print("导入审批失败")
            return False, "false"
        

    def chenckPhoneIsTest(self, phone, Authorization, suiteId):
        # crm系统查询账号有没有注册
        UserInfoByTestUrl = 'https://gw.vipthink.cn/api/member/back/ol-user/getUserInfoByMobile'
        body = json.dumps({"mobile": phone})
        headers = {
            'content-type': 'application/json',
            'authorization': Authorization
        }
        response = requests.request("POST", url=UserInfoByTestUrl, headers=headers, data=body)
        re = json.loads(response.text)
        try:
            if not re['data']:
                # 没有豌豆id，查询白名单存不存在
                whiteListUrl = 'https://gw.vipthink.cn/api/member/back/whitelist/pageQueryWhitelistInfos'
                wbody = json.dumps({"mobile": phone, "page": 1, "limit": 20})
                wheaders = {
                    'content-type': 'application/json',
                    'authorization': Authorization,
                    'Appid': '46620446'
                }
                wresponse = requests.request("POST", url=whiteListUrl, headers=wheaders, data=wbody)
                wre = json.loads(wresponse.text)
                if wre['data']['records'][0]['status'] == 0:
                    # 存在白名单且该账号状态=启用中
                    return '白名单账号已禁用'
            else:
                # 有豌豆id，查账号是不是测试账号
                userId = re['data'][0]['userId']
                wheaders = {
                        'content-type': 'application/json',
                        'authorization': Authorization,
                        'Appid': '46620446'
                    }
                userDetailUrl = f'https://member.vipthink.cn/member/v1/back/ol-user/findDetailById?userId={userId}'
                uresponse = requests.request("GET", url=userDetailUrl, headers=wheaders)
                ure = json.loads(uresponse.text)
                if ure['data']['user']['boolTestUser'] is False:
                    return '该账号不是测试账号'
        except KeyError:
            return '该账号未注册也不在白名单内，请使用测试账号'
        
        try:
            checkBytestSuiteUrl = 'https://commodity.vipthink.cn/commodity/v1/ol-package/list'
            cbody = json.dumps({"idOrName":suiteId,"status":1,"isTest":0,"page":1,"limit":20})
            cresponse = requests.request("POST", url=checkBytestSuiteUrl, headers=headers, data=cbody)
            cre = json.loads(cresponse.text)
            if cre['data'][0]['isTest'] != 1:
                return '请使用测试套餐'
            else:
                return 0
        except KeyError:
            return '套餐id不存在，请检查'
        # return response



    #主流程
    def run(self,choose_url,name,area_code,phone,hourId,hour_price,channel_id):
        if choose_url == 'pro' : channel_id = 467263
        Authorization = self.getCrmToken(choose_url)[0]
        if Authorization is False:return False, "登录失败"
        if choose_url == 'pro':
            if type(phone) == list:
                for mobile in phone:
                    result =  self.chenckPhoneIsTest(mobile, Authorization, hourId)
                    if result != 0:
                        return False, result
        try:
            # 主代码块
            xlsx_file = self.orderV1Xlsx(name,area_code, phone, hourId, hour_price,channel_id)
            importNum = self.importV1(choose_url, Authorization, xlsx_file[0])
            os.remove(import_excel_path + xlsx_file[0])
            checkStauts_info = self.checkStatus(choose_url,Authorization,importNum)
            print("checkStauts_info:",checkStauts_info)
            if checkStauts_info == 0:
                print("导入校验失败!！！")
                return False, "false"
            else:
                #提交审核
                self.orderConfirm(choose_url,Authorization,checkStauts_info[0],importNum)
                #审核审核明细
                importDetail_list = self.importDetailList(choose_url,Authorization,importNum)
                print("待审核明细：",importDetail_list)
                #审核通过
                result = self.handleMetadata(choose_url,Authorization,importNum,importDetail_list[0])
                return result
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
#      choose_url = "pre"  # test, pro,pre
#      # Authorization = ''
#      nameList = ['小明']
#      area_codeList = [86]
#      phoneList = [14700000004]
#      sku_id = 10016141
#      sku_price = 0
#      channel_id = '470636'
#      orderImportPackageV1().run(choose_url,nameList,area_codeList,phoneList,sku_id,sku_price,channel_id)















