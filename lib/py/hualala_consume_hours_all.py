import random
from datetime import date

import numpy as np

from bin.runMySQL import mysqlMain
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

class UserConsumeHoursRun():
    #获取签名sign接口
    def getLiuyiToken(self, choose_url):
        auth_url = getConfig("liuyi-url", choose_url)
        account = getConfig("liuyi-login", choose_url + "_phone")
        # print(auth_url)

        url_path = "/oa-user-center/sso/login?account=" + account + "&password=e10adc3949ba59abbe56e057f20f883e&smsCode=1234"
        headers = {
            'content-type': 'application/json'
        }
        response = requests.request("POST", auth_url + url_path,  headers=headers)
        re = json.loads(response.text)
        print(re)
        # print(re['data']['accessToken'])
        # print(re['data']['token'])
        try:
            return re['data']['accessToken']
        except KeyError as e:
            # 异常时，执行该块
            return False, e
            pass

    # 到课消课记录，查询待消课的记录
    def get_takeAndConsume_list(self,choose_url,Authorization,userid,course_type):

        cms_url = getConfig("liuyi-gw-mg-url", choose_url)
        print(cms_url)
        url = '/manager-api/o/course/takeAndConsume/getList'
        headers = {
            'content-type': 'application/json',
            "authorization": Authorization
        }
        params_data = {
                        "page":1,
                        "size":30,
                        "startDate": "2020-01-01",
                        "endDate": "2026-12-31",
                        "courseTimeScheduleId":0,
                        "workGroupId":0,
                        "teacherId":0,
                        "consumeStatus":0,
                        "courseType":course_type,
                        "userName":userid,
                        "groupName":"",
                        "belongArea":"",
                        "userId":"",
                        "teacherName":""
                       }
        res = requests.get(url=cms_url+url, params=params_data,headers=headers)
        print(json.loads(res.text))
        if json.loads(res.text)["data"]["count"] == 0:
            # print(userid['UserId'])
            print("消课失败")
            return "消课失败，该学员没有可消课的上课记录"

        else:
            # res = requests.request("POST", cms_url + url, params=params_data, headers=headers)
            print("输出"+res.text)
            re_data = json.loads(res.text)["data"]["data"]
            # print("data:"+re_data)
            for i in range(len(re_data)):
                id = json.loads(res.text)["data"]["data"][i]["id"]
                print(id)
                self.commit_manual_consume(id,choose_url,Authorization)
                i += 1
            self.query_playback_record(choose_url, Authorization, userid)
            return "消课成功!"



    # 到课消课记录，操作手动消课
    def commit_manual_consume(self,id,choose_url,Authorization):

        cms_url = getConfig("liuyi-gw-mg-url", choose_url)
        url = cms_url + '/manager-api/o/course/takeAndConsume/commitManualConsume'
        headers = {
            "authorization": Authorization,
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "accept":"application/json, text/plain, */*"
        }
        data = {
                "id":id,
                "url":"https%3A%2F%2Fhualala-common.oss-cn-shenzhen.aliyuncs.com%2Ftest%2Fcms%2F6550cf8ef4edcc0001ac66df.png",
                "reason": "9512345678977777777",
                "type": 2
        }
        res = requests.session().post(url=url, data=data,headers=headers)
        print(json.loads(res.text))


    # 消课审核-查询接口
    def query_playback_record(self,choose_url,Authorization,userid):
        cms_url = getConfig("liuyi-gw-mg-url", choose_url)
        url = cms_url + '/manager-api/o/apply/playbackRecord/query.json'
        headers = {
            "authorization": Authorization
        }
        data = {
                "groupId": 0,
                "teacherId": 0,
                "user": userid,
                "page": 1,
                "size": 20,
                "state": 1
        }
        res = requests.session().post(url=url, data=data,headers=headers)
        print(json.loads(res.text))
        re_data = json.loads(res.text)["data"]["list"]

        for i in range(len(re_data)):
            id = json.loads(res.text)["data"]["list"][i]["id"]
            self.agree_playback_record(id,choose_url,Authorization)
            i += 1



    # 同意消课审核
    def agree_playback_record(self,id,choose_url,Authorization):
        cms_url = getConfig("liuyi-gw-mg-url", choose_url)
        url = cms_url + '/manager-api/o/apply/playbackRecord/updateState.json'
        headers = {
            "authorization": Authorization
        }
        data = {
                "id": id,
                "state": 2,
                "reason": "",
                "type": 2,

        }
        res = requests.session().post(url=url, data=data,headers=headers)
        print(json.loads(res.text))

    def run(self,choose_url,user_id,course_type):
        Authorization = self.getLiuyiToken(choose_url)
        res = self.get_takeAndConsume_list(choose_url,Authorization,user_id,course_type)
        return res

    def join_class(self,choose_url,user_id):
        auth_url = getConfig("liuyi-gw-mg-url", choose_url)
        url_path = "/manager-api/o/new/allocate/group/insideJoinGroup.json?userId="+user_id+"&allocationGroupId=2087&forceJoin=false"
        Authorization=self.getLiuyiToken(choose_url)
        headers = {
            'content-type': 'application/json',
            "authorization": Authorization
        }
        response = requests.request("GET", auth_url + url_path, headers=headers)
        re = json.loads(response.text)
        print(re)
        return re
# # 系统消课
#     def update_can_comsume_status(self,choose_url,user_id):
#         if choose_url == "test":
#             mysql_conn = mysqlMain('MySQL-Liuyi-test')
#         else:
#             mysql_conn = mysqlMain('MySQL-Liuyi-preprod')
#         sql ="UPDATE `i61-hll-manager`.group_user_course_schedule_info gucsi JOIN `i61-hll-manager`.group_course_schedule_info gcsi ON gucsi.group_course_schedule_id = gcsi.id SET gucsi.can_auto_consume = 1 WHERE gucsi.user_id = '%s'" % user_id +" AND gucsi.consume_status = 0 AND gucsi.status = 0  AND gcsi.course_date < NOW();"
#         try:
#             if user_id is not None:
#                 print("执行更新sql"+user_id)
#                 mysql_conn.execute(sql)
#                 return True
#             else:
#                 return False
#         except Exception as e:
#             print("数据修改失败：", e)
#             return False
#         finally:
#             del mysql_conn
#     def getLiuyiJobToken(self, choose_url):
#         auth_url = getConfig("liuyi-xxl-job-url", choose_url)
#         url_path = "/login"
#         headers = {
#             'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
#         }
#
#         data = {
#                 "userName": "admin",
#                 "password": "admin"
#         }
#         response = requests.request("POST", auth_url + url_path, data=data,headers=headers)
#         re = json.loads(response.text)
#         print(response.headers['Set-Cookie'])
#         return response.headers['Set-Cookie']
#
#     def run_comsume_job(self,choose_url,user_id):
#         update_result=self.update_can_comsume_status(choose_url,user_id)
#         if update_result:
#             time.sleep(3)
#             header_cookie=self.getLiuyiJobToken(choose_url)
#             job_id=getConfig("liuyi-consume_course_id", choose_url)
#             auth_url = getConfig("liuyi-xxl-job-url", choose_url)
#             url_path = "/jobinfo/trigger"
#             headers = {
#                 'content-type': 'application/x-www-form-urlencoded',
#                 'Cookie':header_cookie
#             }
#             data = {
#                 "id": job_id
#             }
#             response = requests.request("POST", auth_url + url_path, data=data, headers=headers)
#             re = json.loads(response.text)
#             print(re)
#             try:
#                 return True
#             except KeyError as e:
#                 # 异常时，执行该块
#                 return False, e
#                 pass
#         else:
#             return "出错了，消课失败！"

if __name__ == '__main__':
    print("执行开始。。。。")
    env_select = "test" # test, pro
    # Authorization = ''
    user_id='22643861'
    orderNum = '132456'
    course_type=10
    re = UserConsumeHoursRun().run(env_select,user_id,course_type)
    print("执行结束88,",user_id,re)


