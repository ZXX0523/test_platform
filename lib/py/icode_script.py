#-*_coding:utf8-*-
import requests,json,time
from bin.runMySQL import mysqlMain
from conf.readconfig import *

class icodeScript(object):
    def sqlupdate(self,choose,learner_id,start_time,schedule_id,section_id,phone,brand_id):
        """
        :param choose: 1：解绑学员微信关联，2:更新讲次数据
        """
        sqlconnet = mysqlMain('MySQL-iCode')
        if choose == 1:
            # 解绑学员微信关联
            wxclear_sql1 = "update bc_learner_wechat set learner_id = 0 where learner_id = %s;"%learner_id
            wxclear_sql2 = "update bc_learner_admin_user set learner_id = 0 where learner_id = %s;"%learner_id
            content1 = sqlconnet.fetchall(wxclear_sql1)
            content2 = sqlconnet.fetchall(wxclear_sql2)
        elif choose == 2:
            # 更新班期的讲次开始时间
            wxclear_sql1 = "UPDATE `bc_schedule` SET `start_time` = '%s' WHERE `id` = %s;"%start_time,schedule_id
            wxclear_sql2 = "UPDATE `bc_schedule_section` SET `start_time` = '%s' WHERE `schedule_id` = %s;"%start_time,schedule_id
            wxclear_sql3 = "UPDATE `bc_schedule_class` SET `start_time` = '%s' WHERE `schedule_id` = %s;"%start_time,schedule_id
            content1 = sqlconnet.fetchall(wxclear_sql1)
            content2 = sqlconnet.fetchall(wxclear_sql2)
            content3 = sqlconnet.fetchall(wxclear_sql3)
        elif choose == 3:
            # 更新学员的讲次开始时间
            wxclear_sql1 = "UPDATE `vipthink_icode_classroom_uat`.`bc_learner_section` SET `start_time` = '"+start_time+"' WHERE `learner_id` = "+learner_id+" AND `schedule_id` = "+schedule_id+" and `section_id`= "+section_id+";"
            # 更新班期的讲次开始时间
            wxclear_sql2 = "UPDATE `uat_vipthink_icode`.`bc_schedule` SET `start_time` = '"+start_time+"' WHERE `id` = "+schedule_id+";"
            wxclear_sql3 = "UPDATE `uat_vipthink_icode`.`bc_schedule_class` SET `start_time` = '"+start_time+"' WHERE `schedule_id` = "+schedule_id+";"
            wxclear_sql4 = "UPDATE `uat_vipthink_icode`.`bc_schedule_section` SET `start_time` = '"+start_time+"' WHERE `schedule_id` = "+schedule_id+" and `section_id`= "+section_id+";"
            content1 = sqlconnet.fetchall(wxclear_sql1)
            content2 = sqlconnet.fetchall(wxclear_sql2)
            content3 = sqlconnet.fetchall(wxclear_sql3)
            content4 = sqlconnet.fetchall(wxclear_sql4)
        elif choose == 4:
            wxclear_sql1 = "SELECT * FROM `vipthink_icode_classroom_uat`.`bc_learner_section` where learner_id = %s;" % learner_id
            wxclear_sql2 = "UPDATE `vipthink_icode_classroom_uat`.`bc_learner_section` SET unlock_time = '2021-10-15 00:00:01',update_studying_time = '2021-10-15 00:00:01',`finish_time` = '2021-10-09 21:30:00' where learner_id = %s;"%learner_id
            content1 = sqlconnet.fetchall(wxclear_sql1)
            content2 = sqlconnet.fetchall(wxclear_sql2)
            print(content1)
            print(content2)
        del sqlconnet

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
        try:
            return re['data']['token'],re['data']['uid']
        except KeyError as e:
            # 异常时，执行该块
            return False, e

    # 批量调整班主任，临时使用
    def changeHeadmaster(self,Authorization,learnerId):
        icode_url = "https://icode.vipthink.cn"
        url_path = "/v1/web/learner/headmaster"
        payload = json.dumps({
            "courseId": 1769,
            "learnerId": learnerId,
            "scheduleId": 226,
            "headmasterType": 2,
            "preHeadmasterId": 75,
            "postHeadmasterId": 78
        })
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("PUT", icode_url+url_path, headers=headers, data=payload)
        print(response.text)
        return True,"success"

    # 查询账号，获取brand_id
    def getBrandId(self,choose_url,Authorization,phone):
        member_url = getConfig("member-url",choose_url)
        url_path = "/member/back/ol-user/getUserInfoByMobileOrUserId"
        payload = json.dumps({"mobile": phone})
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'appid': '46620446',
            'authorization': Authorization,
        }
        response = requests.request("POST", member_url+url_path, headers=headers, data=payload)
        re=json.loads(response.text)
        try:
            return True, re['data'][0]['userId']
        except KeyError as e:
            return False, e

    # 获取learner_id
    def getLearnerId(self,choose_url,Authorization,brand_id):
        gw_url = getConfig("gw-url",choose_url)
        url_path = "/api/member/back/ol-user/getUserInfoByUnificationIdOrUserId"
        payload = json.dumps({"userId":brand_id})
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", gw_url+url_path, headers=headers, data=payload)
        re=json.loads(response.text)
        try:
            return True, re['data'][0]['unificationId']
        except KeyError as e:
            return False, e

    # 修改测试账号-中台
    def crmTestUser(self,choose_url,Authorization,brand_id):
        member_url = getConfig("member-url",choose_url)
        url_path = "/member/v1/back/auth/ol-user/updateUserIsTestUser"
        payload = json.dumps({"isTestUser":1,"changeReason":"测试账号修改","userId":brand_id})
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'appid': '46620446',
            'seq': str(time.time()*1000),
            'authorization': Authorization,
        }
        response = requests.request("POST", member_url+url_path, headers=headers, data=payload)
        re=json.loads(response.text)
        try:
            if re['message'] == '操作成功':return True, "中台修改成功"
            else:return False, str(brand_id)+"中台修改失败"
        except KeyError as e:
            return False, e

    # 修改测试账号-编程
    def icodeTestUser(self,choose_url,Authorization,learner_id):
        icode_url = getConfig("icode-url",choose_url)
        url_path = "/v1/web/learner/updateIsTest"
        payload = json.dumps({"isTest":1,"learnerId":learner_id})
        headers = {
            'content-type': 'application/json;charset=UTF-8',
            'authorization': Authorization,
        }
        response = requests.request("POST", icode_url+url_path, headers=headers, data=payload)
        re=json.loads(response.text)
        try:
            if re['message'] == 'OK':return True, "编程修改成功"
            else:False, str(learner_id)+"-编程修改失败"
        except KeyError as e:
            return False, e


    def changeTest(self,choose_url,phone):
        Authorization = self.getCrmToken(choose_url)[0]
        brand_id = self.getBrandId(choose_url,Authorization,phone)
        try:
            if brand_id[0]:
                learner_id = self.getLearnerId(choose_url,Authorization,brand_id[1])
                self.crmTestUser(choose_url,Authorization,brand_id[1])
                self.icodeTestUser(choose_url,Authorization,learner_id[1])
                return True, str(phone)+"已修改为测试账号", phone
            else:return False, "未找到"+str(phone)+"用户", phone
        except KeyError as e:
            return False, e ,phone

# if __name__ == '__main__':
#     choose = 4
#     learner_id = '12099841'
#     start_time = '2021-09-28 16:00:00'
#     schedule_id = '32121'
#     section_id = '47234'
#     phone = None
#     brand_id = None
#     re = {}
#     learnerIdList = [elem['learnerId'] for elem in re['records']]
#     for learner_id in learnerIdList:
#         print(str(learner_id))
#         # orderImportPackage().test(learner_id)
#         time.sleep(5)
