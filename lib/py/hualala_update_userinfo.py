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

class UpdateUserInfoRun():
    #获取签名sign接口
    def UpdateUserInfo(self,mobile,choose_url):
        if choose_url == "test":
            mysql_conn = mysqlMain('MySQL-Liuyi-test')
        else:
            mysql_conn = mysqlMain('MySQL-Liuyi-preprod')
        # cursor = mysql_conn.cursor()
        sql = "set @Account ='%s'" % mobile
        sql_user = "SELECT UserId FROM i61.userinfo  WHERE Account ='%s'" % mobile
        sql1 = "set @UserId = (SELECT UserId FROM i61.userinfo  WHERE Account = @Account);"
        sql2 = f"UPDATE `i61_leads`.`leads_user_info` SET `user_name` = @Account, `wx_code` =  @Account,`country` = '中国', `province` = '北京', `belong_area` = '中国大陆', `city` = '北京市', `area` = '朝阳区' WHERE `user_id` = @UserId;"
        sql3 = "UPDATE `i61`.`userinfo` SET  `NickName` = @Account,RemarkName= @Account, `BirthMonth` = '2019-01-01',`timeZone` = '8', `PaintingInterest` = '高', `BasicDrawing` = '没有基础', `PaintingLearning` = '学校', `OtherOnline` = '数学' WHERE `Account` =@Account;"
        sql5 = f"UPDATE `i61`.`applystandardcourse` SET  `BirthMonth` = '2019-01-01',`Receiver` = '实物收货地址-测试', `Phone` = @Account, `Address` = '实物收货地址-测试地址,请勿发货' WHERE `UserId` = @UserId;"
        sql6 = f"REPLACE INTO `i61`.`experiencefollow` (`UserId`, `TeacherId`, `GroupId`, `TableId`, `ArriveLive_del`, `ExperienceReport`, `ExperienceReportTime`, `ChildEvaluation`, `ParentEvaluation`, `BeginCourseStage`) VALUES (@UserId, 401971, 1, 3, 0, '', NOW(), '[null,null,null,null,null]', '[1,null,null,null,null,null,null,\"1\",6,null]', 0);"
        sql4 = "REPLACE INTO `i61-hll-manager`.`questionnaire_user_intro` (`user_id`, `questionnaire_id`, `teacher_id`, `answer`, `status`, `gmt_create`, `gmt_modify`) VALUES (@UserId, 2, 401971, '{\"51\":77,\"14\":\"提高绘画技巧\"}', 2,NOW(), NOW());"
        try:
            if mobile is not None:
                userid = mysql_conn.fetchone(sql_user)
                # print(userid['UserId'])
                if userid is None:
                    return False,"修改失败，该手机号没有进线学员"
                else:
                    mysql_conn.execute(sql)
                    mysql_conn.execute(sql1)
                    mysql_conn.execute(sql2)
                    mysql_conn.execute(sql3)
                    mysql_conn.execute(sql5)
                    mysql_conn.execute(sql6)
                    mysql_conn.execute(sql4)
                    str1="手机号："+mobile
                    str2="用户id："+str(userid['UserId'])
                    return True,"修改成功",str1,str2
            else:
                return False
        except Exception as e:
            print("数据修改失败：", e)
            return False
        finally:
            del mysql_conn







if __name__ == '__main__':
    print("执行开始。。。。")
    choose_url = "test" # test, pro
    # Authorization = ''
    orderNum = '19115762043'
    re = UpdateUserInfoRun().UpdateUserInfo(orderNum,choose_url)
    print("执行结束88,",orderNum,re)


