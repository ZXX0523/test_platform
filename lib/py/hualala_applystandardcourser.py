# import datetime
import numbers
import random
from datetime import date
from datetime import datetime

import xlwt
from openpyxl import Workbook
import openpyxl
# from spire.xls import *
import pandas as pd
import numpy as np
from openpyxl.reader.excel import load_workbook
from openpyxl.styles.numbers import NumberFormat
from openpyxl.workbook import Workbook

from bin.runMySQL import mysqlMain
from conf.readconfig import getConfig
from lib.py.hualala_update_userinfo import UpdateUserInfoRun
from lib.py.order_V2_script import *
import requests
import xlsxwriter
import json
import pandas as pd
import os, time

# import oss2
# from qcloud_cos import CosConfig
# from qcloud_cos import CosS3Client

from conf.readconfig import *

from datetime import datetime, timedelta

class ApplyStandardCourserRun():

    # 新建学员导入订单excel
    def getFileStream_Order(self, phone, sku_id, marketing_id):
        file_name = "example.xlsx"
        # 获取当前日期和时间
        now = date.today()
        # 将日期和时间转换为字符串格式
        out_orderNumber = time.time()
        print(out_orderNumber)
        # out_orderNumber = date_str
        # 创建一个新的Excel文件并添加一个工作表
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet()
        # 写入数据行
        data = [["填写须知", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                ["填写须知", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                ["填写须知", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                ["*第三方订单号", "*用户姓名", "*手机区号", "*手机号", "*画啦啦学员ID", "学员注册渠道代号", "*套餐ID",
                 "*活动配置ID", "*支付方式",
                 "收款账号", "平台优惠金额", "*支付日期", "是否需要地址", "收件人",
                 "国家", "联系电话", "省", "市", "区", "详细地址", "用户备注", "退费信息留言"],
                [int(out_orderNumber), "测试学员", 86, int(phone), "", "", int(sku_id), int(marketing_id), "抖音小店", "", "", now,
                     0, "", "", "", "", "", "", "", "", ""]
        ]
        for row_num, data_row in enumerate(data, start=0):
            for col_num, value in enumerate(data_row):
                worksheet.write(row_num, col_num, value)
        #将支付时间修改为日期格式
        date_format = workbook.add_format({'num_format': 'yyyy/mm/dd'})
        worksheet.write_datetime(4, 11, now, date_format)
        # 保存工作簿
        workbook.close()
        return file_name

    def getLiuyiToken(self, choose_url):
        auth_url = getConfig("liuyi-url", choose_url)
        account = getConfig("liuyi-login", choose_url + "_phone")

        url_path = "/oa-user-center/sso/login?account=" + account + "&password=e10adc3949ba59abbe56e057f20f883e&smsCode=1234"
        headers = {
            'content-type': 'application/json'
        }
        response = requests.request("POST", auth_url + url_path, headers=headers)
        re = json.loads(response.text)
        print(re)
        try:
            return re['data']['accessToken']
        except KeyError as e:
            # 异常时，执行该块
            return False, e
            pass

    # 调用导入订单的接口
    def importCreateNew(self,mobile, file_path, Authorization, choose_url):
        gw_url = getConfig("liuyi-url", choose_url)
        url_path = "/manager-api/o/standard/applySignUp/importCreateNew"
        headers = {
            'authorization': Authorization,
            'Accept': 'application/json, text/plain, */*',
            'priority': 'u=1, i'
        }
        files = {
            'file': open(file_path, 'rb')
        }
        print(files)
        response = requests.request("POST", gw_url + url_path, headers=headers, files=files)
        print("导入订单" + response.text)
        time.sleep(2)
        res=self.user_order_status(mobile,choose_url)
        return res

    # 查询数据库，学员的首报订单导入结果1
    def user_order_status(self,mobile,choose_url):
        if choose_url == "test":
            mysql_conn = mysqlMain('MySQL-Liuyi-test')
        else:
            mysql_conn = mysqlMain('MySQL-Liuyi-preprod')

        sql_user = "SELECT UserId FROM i61.userinfo  WHERE Account ='%s'" % mobile +""
        try:
            # 根据手机号查询数据表是否有该用户，判断
            # 用户是否已进线
            if mobile is not None:
                userid = mysql_conn.fetchone(sql_user)
                if userid is None:
                    # print(userid['UserId'])
                    return False, "导入失败，该手机号没有进线学员"
                else:
                    # 查询用户的订单导入结果
                    user=userid['UserId']
                    print(userid['UserId'])
                    order_import_sql = "SELECT * FROM `i61-hll-manager`.`import_user_standard_course_record`  WHERE `user_id` ='%s'" % user+"ORDER BY id DESC"
                    order = mysql_conn.fetchall(order_import_sql)
                    print(order)
                    order_id=order[0]['id']
                    order_user_id=order[0]['user_id']
                    order_state=order[0]['state']
                    order_fail_reason=order[0]['fail_reason']
                    # 判断订单导入状态（3：则导入失败）
                    if order_state ==3 :
                        return False,order_user_id,order_fail_reason
                    else:
                        return True,order_id,order_user_id,"导入成功"
            else:
                return False,"导入失败"
        except Exception as e:
            print("数据修改失败：", e)
            return False
        finally:
            del mysql_conn

    # 调用接口，将首报订单审批通过
    def order_audit(self,Authorization,import_id,choose_url):
        gw_url = getConfig("liuyi-url", choose_url)
        url_path = "/manager-api/o/standard/applySignUp/batchAudit"
        headers = {
            'content-type': 'application/json',
            'authorization': Authorization
        }
        datas = json.dumps({
              "ids": [import_id],
              "state": 3
            })
        print(datas)
        response = requests.request("POST", gw_url + url_path, headers=headers, data=datas)
        print("审批通过" + response.text)
        re = json.loads(response.text)
        # 判断接口的审批结果是否失败，成功则继续往下查数据库的审批结果
        if re['code'] != 0:
            print("审批失败",re)
            return False,re
        else:
            if choose_url == "test":
                mysql_conn = mysqlMain('MySQL-Liuyi-test')
            else:
                mysql_conn = mysqlMain('MySQL-Liuyi-preprod')
            order_import_sql = "SELECT * FROM `i61-hll-manager`.`import_user_standard_course_record`  WHERE `id` ='%s'" % import_id + "ORDER BY id DESC"
            order = mysql_conn.fetchall(order_import_sql)
            order_state=order[0]['state']
            order_fail_reason=order[0]['fail_reason']
            # 从数据库判断是否审批失败（order_state=2：成功，1或3都是失败），若审批失败，返回失败原因
            if order_state == 2:
                return True,re
            else:
                return False,order_fail_reason

    # 查询套餐
    def select_applystandercourse(self,choose_url,choose_sku_id,choose_tools):
        gw_url = getConfig("liuyi-gw-mg-url", choose_url)
        # print(gw_url)
        Authorization = self.getLiuyiToken(choose_url)
        url_path = '/hll-standard-course/o/standard/course/get/detail/info?skuIds='+str(choose_sku_id)+'&isOriginalPrice=0&isTwins=0&hasTools='+str(choose_tools)+'&tagName=%E5%85%A8%E9%87%8F&teacherId='
        headers = {
            # 'content-type': 'application/json',
            'authorization': Authorization
        }
        response = requests.request("POST", gw_url + url_path, headers=headers)
        print("查询结果：" + response.text)
        re = json.loads(response.text)
        return re

    # 提交续费——手动
    def submit_renewal(self,choose_url,mobile,sku_id, marketing_id,coupon_id):
        # 获取今天的日期
        current_date = date.today()
        # 将日期转换为字符串
        date_str = current_date.strftime('%Y-%m-%d')

        out_orderNumber = time.time()
        # 通过数据库，根据手机号查询学员id和昵称
        if choose_url == "test":
            mysql_conn = mysqlMain('MySQL-Liuyi-test')
        else:
            mysql_conn = mysqlMain('MySQL-Liuyi-preprod')
        userinfo_sql = "SELECT * FROM i61.userinfo WHERE Account ='%s'" %mobile
        standardcourseskuinfo_sql="SELECT * FROM i61_service.standardcoursesku WHERE Id ='%s'" %sku_id
        userinfo = mysql_conn.fetchone(userinfo_sql)
        standardcourseskuinfo = mysql_conn.fetchone(standardcourseskuinfo_sql)
        tools = standardcourseskuinfo['HasTools']
        price= standardcourseskuinfo['Price']
        tools_price=standardcourseskuinfo['ToolsPrice']
        period_id=standardcourseskuinfo['PeriodId']
        if userinfo is None:
            return False, "导入失败，该手机号没有进线学员"
        else:
            user_id = userinfo['UserId']
            remark_name = userinfo['RemarkName']
            gw_url = getConfig("liuyi-url", choose_url)
            Authorization = self.getLiuyiToken(choose_url)
            url_path = '/manager-api/o/renewal/upgrade/submit'
            headers = {
                'content-type': 'application/json',
                'authorization': Authorization
            }

            datas = json.dumps({
              "couponValue": 0,
              "couponId": coupon_id,
              "marketingId": marketing_id,
              "isOriginalPrice": 0,
              "needInvoice": 0,
              "applyState": 3,
              "payDate": "",
              "paywayId": 10,
              "price": price,
              "toolsPrice": tools_price,
              "hasTools": tools,
              "isTwins": 0,
              "periodId": period_id,
              "payType": 4,
              "payForm": 1,
              "preSkuId": "",
              "areaCode": "01",
              "bigGiftCourseNum": "",
              "drawCurrencyNum": 0,
              "taskNames": "",
              "videoCourseGift": [],
              "goodsGift": [],
              "renewOrders": [
                {
                  "renewOrderId": "",
                  "order": int(out_orderNumber),
                  "payWay": 1,
                  "payDate": date_str,
                  "price": price,
                  "imageUrl": [
                    "https://hualala-common.oss-cn-shenzhen.aliyuncs.com/test/cms/679355becc3ccb0001f3269f.png"
                  ],
                  "foreignCurrency": "",
                  "imgLoading": "false"
                }
              ],
              "mealId": 0,
              "skuId": sku_id,
              "headerTeacherName": "zxx01(zxx01)",
              "userId": user_id,
              "userName": remark_name,
              "changeApplyType": 1
            })
            response = requests.request("POST", gw_url + url_path, headers=headers, data=datas)
            print("查询结果：" + response.text)
            re = json.loads(response.text)
            order_id = re['data']
            if re['code'] == 0 and re['data'] is not None:
                self.renewal_audit(choose_url, Authorization, order_id)
                result = "学员id："+str(user_id)+"，学员生成续费订单成功！"
                print("审批成功")
                return result
            else:
                result = "学员id："+str(user_id)+"，学员提交续费订单失败！失败原因："+re['data']
                print("提交续费订单失败")
                return result

    def renewal_audit(self,choose_url,Authorization,order_id):
        gw_url = getConfig("liuyi-gw-mg-url", choose_url)
        url_path = '/manager-api/o/renewal/upgrade/review'
        headers = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'authorization': Authorization
        }
        datas = {
            "id": order_id
        }
        response = requests.request("POST", gw_url + url_path, headers=headers, data=datas)
        print(json.loads(response.text))
        response = requests.request("POST", gw_url + url_path, headers=headers, data=datas)

    def run(self, choose_url, phone, sku_id, marketing_id):
        # if choose_url == 'pro' : channel_id = 467263
        Authorization = self.getLiuyiToken(choose_url)
        if Authorization is False: return False, "登录失败"
        file_path = self.getFileStream_Order(phone, sku_id, marketing_id)
        if file_path is False: return False, "excel文件创建失败"
        UpdateUserInfoRun().UpdateUserInfo(phone,choose_url)
        try:
            res = self.importCreateNew(phone,file_path, Authorization, choose_url)
            os.remove(file_path)
            if res[0]:
                time.sleep(3)
                order_audit_result = self.order_audit(Authorization,res[1],choose_url)
                if order_audit_result[0]==True:
                    result = "学员id："+str(res[2])+"，学员生成首报订单成功！"
                else:
                    result= "学员id："+str(res[2])+"，首报订单审批失败！失败原因："+order_audit_result[1]
                return result
            else:
                return False,res
            # 主代码块
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
    choose_url = "test"  # test, pro
    # Authorization = ''
    phone = '19104182356'
    sku_id = 201
    marketing_id = 603
    coupon_id=0
    sku_id1 = 275
    marketing_id1 = 936
    # sku_id = 313
    # marketing_id = 295
    Authorization = "eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjoicElsYnJxeGh4dmlqbWFCamR5b3F5ZzV0YW1kRk9Qdzg2azRCQ0FGbzhUdmNWMERJcFpXaFlyMnk5ZDk3RkR3bjRhbDAxRUxmUlNqVUVlbm56QzV6clR5T2xRT0UvUUhQdGhmOFBCdEJUV0VBN2h4Yzh0ZDRyT1k5MzFXWGpRL1JmTmdYclVDeERnYjUzeEVCcFI1ejFoOXFHWTdjZGNCVG53aE1xWVZRREtPVlV3OFF1Ry9GYWZtMWZwaXBWLzdaNG5xL3h4ZXRlRzFJd2FSdHRqZEJXbVNia1pHUVFEbDdraCt2MEJtS005eDgyd2FtaFlpNSt3bUVtSGlGZVFNWjMwd2NMY2U0Y01iWTI3WTB5MWxsM3dBWFovVEEwNndjVVdDNzFqZlhHb0p1aWRjS2xBR0FmVS9wYnphbVlDS0YiLCJleHAiOjE3Mzc1MzE1Mjd9.emZdVPH3BbQgdIf7m4zqnxXOqTltLz8TlfCzaZjCcaA"
    user_id=1409329
    # re = ApplyStandardCourserRun().getFileStream_V3_yuwen_batch(user_id,Authorization)

    file_path = "example.xlsx"
    # re = ApplyStandardCourserRun().getFileStream_Order(phone, sku_id, marketing_id)
    # re = ApplyStandardCourserRun().getLiuyiToken(choose_url)
    # re = ApplyStandardCourserRun().importCreateNew(mobile,file_path,Authorization,choose_url)
    # re = ApplyStandardCourserRun().run(choose_url,phone, sku_id, marketing_id)
    # re = ApplyStandardCourserRun().user_order_status(phone, choose_url)
    # re=ApplyStandardCourserRun().select_applystandercourse(choose_url,sku_id,str(0))
    re=ApplyStandardCourserRun().submit_renewal(choose_url,phone,sku_id1,marketing_id1,coupon_id)
    #
    # re=ApplyStandardCourserRun().renewal_audit(choose_url,phone,sku_id1)

    print("执行结束88,", re)
