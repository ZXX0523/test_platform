# -*- coding: utf-8 -*-
import requests
import json,uuid

from bin.runMySQL import mysqlMain
from conf.readconfig import getConfig

order_error_code = (10000004,10000006,500003,9000004,500005)

#课程类型key：1-体验课、2-正式课、3-特训课、4-录播课;
#value1: 0-课包类型code（hourAttributeCode）、1-暂不使用（hourCategoryId）、2-套餐类目id（categoryId）、3-propertyId、4-propertyCode、5-propertyName
order_type = {"1":[20,402021106,1279,10653,"b6321272339c4ce085f422507355f99b","入门课程iD"],
              "2":[21,401002000,1317,10650,"c8668b5ec2ba483d80e4ada4b0aff4b3","编程课程iD"],
              "3":[1009,401009000,20043,10650,"c8668b5ec2ba483d80e4ada4b0aff4b3","编程课程iD"],
              "4":[2,401000,1337]}

class orderCreatSkuV2():

    # 获取CRMtoken
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
        # print(re['data']['token'])
        try:
            return re['data']['token'],re['data']['uid']
        except KeyError as e:
            # 异常时，执行该块
            return False, e
            pass

    # 创建课包
    def creatHour(self,choose_url,Authorization,course_id,course_type,hour_name):
        gw_url = getConfig("gw-url",choose_url)
        url_path = "/api/commodity-center/items/create"
        payload = json.dumps({"name":hour_name,
                              "mulitiBrandList":[{"brandCode":"VIP_BianCheng","brandName":"豌豆编程"}],
                              "categoryId":0,
                              "operator":getConfig("crm-login",choose_url+"_name"),
                              "operatorId":getConfig("crm-login",choose_url+"_id"),
                              "status":1,
                              "type":1,
                              "skuList":[{"isDefault":True,
                                   "originalPrice":1,
                                   "salePrice":0.01,
                                   "skuExtension":
                                       {"baseClass":500,
                                        "campId":0,
                                        "userHourType":order_type[str(course_type)][0],
                                        "expiryDate":999,
                                        "giveClass":100,
                                        "repeatCount":50,
                                        "trialPeriod":1,
                                        "courseTypeId":1,
                                        "openPackageDate":0
                                        },
                                   "type":0,
                                   "skuRule":{"ruleCate":[course_id],"ruleSignedNumber":""},
                                   "skuName":""}]})
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'authorization': Authorization
        }
        response = requests.request("POST", gw_url+url_path, headers=headers, data=payload)
        print("--创建课包--"+response.text)
        re=json.loads(response.text)
        if int(re['code']) in order_error_code:return int(re['code']),re['message']
        return re['data']['id']

    # 审核
    def approved(self,choose_url,Authorization,hour_id):
        gw_url = getConfig("gw-url",choose_url)
        url_path = "/api/commodity-center/items/audit"
        payload = json.dumps({"idList":[hour_id],
                              "status":2,
                              "operator":getConfig("crm-login",choose_url+"_name"),
                              "operatorId":getConfig("crm-login",choose_url+"_id")})
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", gw_url+url_path, headers=headers, data=payload)
        re=json.loads(response.text)
        print("--审核--"+response.text)
        if int(re['code']) in order_error_code:return int(re['code']),re['message']
        return re['data']['result']

    # 上架
    def shelves(self,choose_url,Authorization,hour_id):
        gw_url = getConfig("gw-url",choose_url)
        url_path = "/api/commodity-center/items/shelf"
        payload = json.dumps({"itemIdList":[hour_id],
                              "status":4,
                              "operator":getConfig("crm-login",choose_url+"_name"),
                              "operatorId":getConfig("crm-login",choose_url+"_id")})
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", gw_url+url_path, headers=headers, data=payload)
        re=json.loads(response.text)
        print("--上架--"+response.text)
        return re['data']['result']

    # 创建套餐
    def creatSku(self,choose_url,Authorization,hour_sku_id,course_id,course_name,course_type,sku_name):
        agreement_id = 100051 # test 协议id
        gw_url = getConfig("gw-url", choose_url)
        url_path = "/api/commodity-center/items/create"
        payload = json.dumps({
            "name": sku_name,
            "mulitiBrandList": [
                {
                    "id": 3,
                    "brandName": "豌豆编程",
                    "brandCode": "VIP_BianCheng",
                    "relateCategory": {
                        "categoryId": 1277,
                        "categoryName": "编程套餐"
                    },
                    "status": 1,
                    "deleted": False,
                    "createBy": 1,
                    "createName": "超级管理员1",
                    "createTime": "2021-07-15 14:45:07",
                    "updateBy": 4968,
                    "updateName": "密码a@123456789",
                    "updateTime": "2021-10-29 20:01:26"
                }
            ],
            "gift": False,
            "exchange": False,
            "categoryId": order_type[str(course_type)][2],
            "operatorId": getConfig("crm-login",choose_url+"_id"),
            "operator": getConfig("crm-login",choose_url+"_name"),
            "status": 1,
            "type": 1,
            "skuList": [
                {
                    "skuName": sku_name,
                    "originalPrice": 1,
                    "salePrice": 0.01,
                    "channelPrice": None,
                    "skuExtension": {
                        "agreementId": agreement_id,
                        "expiryDate": 0
                    },
                    "type": 1,
                    "skuGroupDetail": [
                        {
                            "realSkuId": hour_sku_id,
                            "quantity": 1,
                            "realSku": {
                                "skuName": sku_name,
                                "mulitiBrandList": [
                                    {
                                        "brandCode": "VIP_BianCheng",
                                        "brandName": "豌豆编程"
                                    }
                                ],
                                "originalPrice": 1,
                                "salePrice": 0.01,
                                "skuExtension": {
                                    "baseClass": 500,
                                    "giveClass": 100,
                                    "expiryDate": 999,
                                    "openPackageDate": 0,
                                    "remedialTeachClass": 0,
                                    "repeatCount": 50,
                                    "trialPeriod": 1,
                                    "agreementId": 0,
                                    "campId": None,
                                    "packageType": 0,
                                    "courseTypeId": 1,
                                    "userHourType": order_type[str(course_type)][0]
                                },
                                "skuRule": {
                                    "ruleCate": [course_id],
                                    "cateList": [
                                        {
                                            "id": course_id,
                                            "name": course_name
                                        }
                                    ],
                                    "ruleEntrance": None,
                                    "ruleGift": None,
                                    "ruleGivePackage": None,
                                    "ruleIsExchangeCourse": None,
                                    "rulePackageCourseTypeSub": None,
                                    "ruleIsPresent": None,
                                    "ruleBanFormulateList": None,
                                    "ruleBanFormulateType": None,
                                    "ruleIsStock": None,
                                    "ruleIsChannel": None,
                                    "ruleIsApple": None,
                                    "ruleRepeatBuy": None,
                                    "ruleFrontbuyList": None,
                                    "ruleSuccesUrl": None,
                                    "ruleSignedNumber": None,
                                    "ruleMoliCoin": None,
                                    "ruleMoliCoinThaw": None,
                                    "ruleActivityRegister": None
                                }
                            }
                        }
                    ],
                    "shelfConfiguration": {
                        "onShelfDate": "",
                        "offShelfDate": ""
                    },
                    "consumeRatiosList": [
                        {
                            "classType": 1,
                            "consumeCurrency": 0
                        },
                        {
                            "classType": 2,
                            "consumeCurrency": 0
                        }
                    ],
                    "skuRule": {
                        "ruleEntrance": 10001,
                        "ruleActivityRegister": None,
                        "ruleMoliCoin": None,
                        "ruleGivePackage": [],
                        "ruleIsExchangeCourse": "",
                        "rulePackageCourseTypeSub": "",
                        "ruleIsPresent": 0,
                        "ruleFrontbuyList": [],
                        "ruleIsStock": None,
                        "ruleIsChannel": 0,
                        "ruleIsApple": "",
                        "ruleRepeatBuy": "",
                        "ruleSuccesUrl": "",
                        "ruleBanFormulateType": [],
                        "ruleBanFormulateList": []
                    },
                    "properties": [],
                    "isDefault": True
                }
            ],
            "itemProperty": [
                {
                    "propertyId": order_type[str(course_type)][3],
                    "propertyCode": order_type[str(course_type)][4],
                    "propertyName": order_type[str(course_type)][5],
                    "propertyDesc": "",
                    "inputType": 1,
                    "status": True,
                    "required": False,
                    "propertyType": 2,
                    "propertyValue": [course_id],
                    "originalPropertyValueList": []
                }
            ]
        })
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", gw_url + url_path, headers=headers, data=payload)
        print("--4--"+response.text)
        re = json.loads(response.text)
        sku_id = re['data']['id']
        return sku_id

    # 获取SKUID
    def getSkuid(self,choose_url,Authorization,item_id):
        gw_url = getConfig("gw-url",choose_url)
        url_path = "/api/commodity-center/items/findOne"
        payload = json.dumps({"id":item_id})
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", gw_url+url_path, headers=headers, data=payload)
        print("--5--"+response.text)
        re = json.loads(response.text)
        sku_id = re['data']['skuList'][0]['id']
        # sku_price = re['data']['skuList'][0]['salePrice']
        return sku_id

    # 主流程
    def run(self,choose_url,Authorization,course_id,course_name,course_type,sku_name):
        sqlconnet = mysqlMain('MySQL-Database')
        search_course = "SELECT course_id,sku_id FROM `qa_platform`.`test_sku_info` WHERE `course_id` = "+course_id+" AND `course_type` = "+course_type
        qa_course = sqlconnet.fetchone(search_course)
        if qa_course is not None:
            del sqlconnet
            return True, "已存在可用套餐，不创建", qa_course['sku_id'], 0.01

        if choose_url == "test":Authorization = self.getCrmToken(choose_url)[0]
        icode_sqlconnet = mysqlMain('MySQL-iCode')
        search_course = "SELECT `pid` FROM `uat_vipthink_icode`.`bc_course` WHERE `course_id` = "+course_id
        pid = icode_sqlconnet.fetchall(search_course)
        del icode_sqlconnet

        # 主代码块
        hour_id = self.creatHour(choose_url,Authorization,pid[0]['pid'],course_type,sku_name) # 课时id
        self.approved(choose_url,Authorization,hour_id)
        self.shelves(choose_url,Authorization,hour_id)
        hour_sku_info = self.getSkuid(choose_url,Authorization,hour_id) # 课时：sku_id
        sku_id = self.creatSku(choose_url, Authorization, hour_sku_info,course_id,course_name,course_type,sku_name) # 套餐skuid
        self.approved(choose_url,Authorization,sku_id)
        self.shelves(choose_url,Authorization,sku_id)
        sku_info = self.getSkuid(choose_url,Authorization,sku_id) # 套餐信息：sku_id、sku_price
        sql_sku_info = "INSERT INTO `qa_platform`.`test_sku_info`" \
                          "(`course_id`, `course_name`, `course_type`, `sku_id`, `sku_name`, `sku_price`, `env`, `source`) " \
                          "VALUES ({}, '{}', {}, {}, '{}', 0.01, {}, 1);".format(course_id,str(course_name),course_type,sku_info,str(sku_name),1)
        sqlconnet.execute(sql_sku_info)
        del sqlconnet
        return True, "套餐创建成功",sku_info,0.01

if __name__ == '__main__':
    choose = "test"  # test, pro
    course_id = "5730"
    course_name = "专用---勿动"
    course_type = 3  #1-体验课、2-正式课、3-特训课、4-录播课;
    sku_name = "icode_auto_test-4"
    print(orderCreatSkuV2().run(choose,None,course_id,course_name,course_type,sku_name))
