
# from bin.runMySQL import mysqlMain

import pymysql
class UpdateUserInfoRun():
    #获取签名sign接口
    def UpdateUserInfo(self,stu_wechat_id,user_id):
        # if choose_url == "test":
        #     mysql_conn = mysqlMain('MySQL-Liuyi-test')
        # else:
        #     mysql_conn = mysqlMain('MySQL-Liuyi-preprod')

        mysql_conn = pymysql.connect(host='172.16.253.113', port=3306, user='root',
                                     password='dbtest', db='pjx', charset='utf8')
        cursor = mysql_conn.cursor()
        # cursor = mysql_conn.cursor()
        sql = "set @stu_wechat_id ='%s'" % stu_wechat_id
        sql = "set @user_id ='%s'" % user_id
        sql_1= "DELETE FROM `i61-bizcenter-copilot`.`dm_wechat_conversation` WHERE `wechat_id` = @stu_wechat_id;"
        sql_2= "DELETE FROM `i61-bizcenter-copilot`.`dm_wechat_user_intent` WHERE `wechat_id` =  @stu_wechat_id;"
        sql_3= "DELETE FROM `i61-bizcenter-corpwechat`.cw_chat_data where msg_time > 1720348933341 and external_user =  @stu_wechat_id"
        sql_4= "DELETE FROM `i61-bizcenter-corpwechat`.`cw_biz_external_user_relation` WHERE external_user_id = @stu_wechat_id;"
        sql_5= "DELETE FROM `i61-bizcenter-corpwechat`.cw_biz_external_user_relation_history WHERE user_id = @user_id and external_user_id =  @stu_wechat_id;"
   # try:
   #          if stu_wechat_id is not None:
   #                  cursor.execute(sql)
   #              # print(userid['UserId'])
   #              if userid is None:
   #                  return False,"修改失败，该手机号没有进线学员"
   #              else:
   #                  mysql_conn.execute(sql)
   #                  mysql_conn.execute(sql1)
   #                  mysql_conn.execute(sql2)
   #                  mysql_conn.execute(sql3)
   #                  mysql_conn.execute(sql5)
   #                  mysql_conn.execute(sql6)
   #                  mysql_conn.execute(sql4)
   #                  str1="手机号："+mobile
   #                  str2="用户id："+str(userid['UserId'])
   #                  return True,"修改成功",str1,str2
   #          else:
   #              return False
   #      except Exception as e:
   #          print("数据修改失败：", e)
   #          return False
   #      finally:
   #          del mysql_conn


def select_user_active_log_reason(userid,content):
    mysql_conn =pymysql.connect(host='preprod-public-mysql-rw.vipthink.net', port=3306, user='ywxt', password='YW4sLR910Ndt', db='eos_basic', charset='utf8')
    cursor = mysql_conn.cursor()
    sql = f"SELECT failure_reason FROM cc_leads.active_log WHERE uuid = {userid} ORDER BY id desc limit 1"
    try:
        cursor.execute(sql)
        mysql_conn.commit()
        result = cursor.fetchone()
        print(result)
        if result is not None:
            # print(result[0])
            if result[0] in content:
                return int(1)
            else:
                return False
        else:
            return False
    except Exception as e:
        mysql_conn.rollback()
        print("数据查询失败：", e)
    finally:
        cursor.close()
        mysql_conn.close()





def update_or_insert_student_pool(student_id):
    """
    检查学员ID是否存在于leads_distribution_pool表，存在则更新pool_id为9，不存在则插入
    :param student_id: 学员ID（整数类型）
    :return: 操作结果描述
    """
        # 建立数据库连接
    conn =pymysql.connect(host='testdb.61info.com', port=3306, user='root', password='dbtest', db='i61_leads', charset='utf8')
    cursor = conn.cursor()

    # 1. 检查学员ID是否存在
    check_sql = "SELECT 1 FROM leads_distribution_pool WHERE user_id = %s LIMIT 1"
    cursor.execute(check_sql, (student_id,))
    exists = cursor.fetchone() is not None

    if exists:
        # 2. 存在则更新pool_id为9
        update_sql = """
            UPDATE leads_distribution_pool test
            SET pool_id = 9, gmt_modify = NOW() 
            WHERE user_id = %s
        """
        cursor.execute(update_sql, (student_id,))
        conn.commit()
        return f"学员ID {student_id} 已存在，已更新pool_id为9"
    else:
        # 3. 不存在则插入记录
        insert_sql = """
            INSERT INTO leads_distribution_pool (user_id, pool_id, gmt_create, gmt_modify)
            VALUES (%s, 9, NOW(), NOW())
        """
        cursor.execute(insert_sql, (student_id,))
        conn.commit()
        return f"学员ID {student_id} 不存在，已插入新记录（pool_id=9）"
def select_user_mobile_encrypt(userid,environment=None):

    if environment == "test":
        mysql_conn =pymysql.connect(host='10.4.32.47', port=3306, user='shdev', password='6JrpIH4DbtE1w2YH', db='eos_basic', charset='utf8')
    elif environment == "pro":
        mysql_conn =pymysql.connect(host='preprod-public-mysql-rw.vipthink.net', port=3306, user='ywxt', password='YW4sLR910Ndt', db='eos_basic', charset='utf8')

    cursor = mysql_conn.cursor()
    sql = f"SELECT mobile_encrypt FROM eos_basic.user_unification uu  WHERE id = {userid}"
    try:
        cursor.execute(sql)
        mysql_conn.commit()
        result = cursor.fetchone()
        print(result)
        # column=[index[0] for index in cursor.description  ]# 列名[
        return result[0]
    except Exception as e:
        mysql_conn.rollback()
        print("数据查询失败：", e)
    finally:
        cursor.close()
        mysql_conn.close()

def select_user_unlockstatus(environment=None):
    if environment == "test":
        mysql_conn =pymysql.connect(host='10.4.32.47', port=3306, user='shdev', password='6JrpIH4DbtE1w2YH', db='eos_basic', charset='utf8')
    else:
        mysql_conn =pymysql.connect(host='preprod-public-mysql-rw.vipthink.net', port=3306, user='ywxt', password='YW4sLR910Ndt', db='eos_basic', charset='utf8')
    cursor = mysql_conn.cursor()
    sql = f"SELECT user_id FROM eos_basic.user_biz WHERE business_id =15 AND lock_status =2  and user_id !=0 order by id desc limit 1;"
    try:
        cursor.execute(sql)
        mysql_conn.commit()
        result = cursor.fetchall()
        userid = [row[0] for row in result]
        # print(userid[0])
        return userid[0]
    except Exception as e:
        mysql_conn.rollback()
        print("数据查询失败：", e)
    finally:
        cursor.close()
        mysql_conn.close()
       
def select_user_and_mobile_encrypt(environment=None):
    if environment == "test":
        mysql_conn =pymysql.connect(host='10.4.32.47', port=3306, user='shdev', password='6JrpIH4DbtE1w2YH', db='eos_basic', charset='utf8')
    else:
        mysql_conn =pymysql.connect(host='preprod-public-mysql-rw.vipthink.net', port=3306, user='ywxt', password='YW4sLR910Ndt', db='eos_basic', charset='utf8')

    cursor = mysql_conn.cursor()
    
    sql = f"SELECT unification_id FROM eos_basic.user_biz WHERE business_id =15 AND lock_status =2  and user_id !=0 order by id desc limit 1;"

    cursor.execute(sql)
    mysql_conn.commit()
    result = cursor.fetchall()
    userid = [row[0] for row in result]
    print(userid)
        
    sql = f"SELECT mobile_encrypt FROM eos_basic.user_unification uu  WHERE id = {userid[0]}"
    print(sql)  
    try:
        cursor.execute(sql)
        mysql_conn.commit()
        result = cursor.fetchone()
        # column=[index[0] for index in cursor.description  ]# 列名[
        return result[0]
    except Exception as e:
        mysql_conn.rollback()
        print("数据查询失败：", e)
    finally:
        cursor.close()
        mysql_conn.close()
        
#debugtalk.py
#可以使用GLOBAL_VAR['']引用环境变量
import json
data = '{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "orderNewSigningPaidLogic", "compareType": "$eq", "compareValue": true, "ruleKeyCascade": null, "optionalValues": [{"value": true, "label": "已新签", "children": null}, {"value": false, "label": "未新签", "children": null}], "inputType": "select", "type": 1, "condition": null, "compareTypeList": [{"label": "等于", "value": "$eq"}]}]}, {"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "latestCcFollowTimeLogic", "compareType": "$le", "compareValue": "7", "ruleKeyCascade": null, "optionalValues": null, "inputType": "text", "type": 2, "condition": {"unit": "天", "min": 0, "max": 10000}, "compareTypeList": [{"label": "小于等于", "value": "$le"}]}, {"ruleKey": "leadsCCLogic", "compareType": "$in", "compareValue": {"orgIds": ["3860_2_615_0"]}, "ruleKeyCascade": null, "optionalValues": null, "inputType": "org-selector", "type": 3, "condition": {"type": 1}, "compareTypeList": [{"label": "满足其一", "value": "$in"}, {"label": "不在列表中", "value": "$nin"}]}]}], "rules": []}'
# 不允许激活配置，在激活黑名单列表里
data1= '{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "isInActiveBlackListLogic", "compareType": "$eq", "compareValue": true, "ruleKeyCascade": null, "optionalValues": [{"value": true, "label": "在激活黑名单内", "children": null}, {"value": false, "label": "不在激活黑名单内", "children": null}], "inputType": "select", "type": 1, "condition": null, "compareTypeList": [{"label": "等于", "value": "$eq"}]}]}], "rules": []}'
# 不允许激活配置，用户已新签
data2= '{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "orderNewSigningPaidLogic", "compareType": "$eq", "compareValue": true, "ruleKeyCascade": null, "optionalValues": [{"value": true, "label": "已新签", "children": null}, {"value": false, "label": "未新签", "children": null}], "inputType": "select", "type": 1, "condition": null, "compareTypeList": [{"label": "等于", "value": "$eq"}]}]}], "rules": []}'
#不允许激活配置，用户分配给当前CC小于9999天
data3= '{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "latestCcAllotTimeLogic", "compareType": "$le", "compareValue": "9999", "ruleKeyCascade": null,"optionalValues": null,"inputType": "text", "type": 2, "condition": {"unit": "天","min": 0,"max": 10000},"compareTypeList": [{"label": "大于等于","value": "$ge"},{"label": "小于等于","value": "$le"}]}]}],"rules": []}'
#不允许激活配置，当前CC跟进记录在9999天内
data4= '{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "latestCcFollowTimeLogic", "compareType": "$le", "compareValue": "9999", "ruleKeyCascade": null, "optionalValues": null, "inputType": "text", "type": 2, "condition": {"unit": "天", "min": 0, "max": 10000}, "compareTypeList": [{"label": "小于等于", "value": "$le"}]}]}], "rules": []}'
#不允许激活配置，进公海9999天内
data5= '{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "latestIntoCcPublicPoolTimeLogic", "compareType": "$le", "compareValue": "9999", "ruleKeyCascade": null, "optionalValues": null, "inputType": "text", "type": 2, "condition": {"unit": "天", "min": 0, "max": 10000}, "compareTypeList": [{"label": "小于等于", "value": "$le"}]}]}], "rules": []}'
#不允许激活配置，最新激活渠道在所选范围内
data6= '{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "latestActiveChannelLogic", "compareType": "$in", "compareValue": [470640], "ruleKeyCascade": null, "optionalValues": null, "inputType": "channel-selector", "type": 3, "condition": null, "compareTypeList": [{"label": "满足其一", "value": "$in"}]}]}], "rules": []}'
#不允许激活配置，用户分配给当前TMK小于9999天
data7= '{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "latestTmkAllotTimeLogic", "compareType": "$le", "compareValue": "9999", "ruleKeyCascade": null, "optionalValues": null, "inputType": "text", "type": 2, "condition": {"unit": "天", "min": 0, "max": 10000}, "compareTypeList": [{"label": "大于等于", "value": "$ge"}, {"label": "小于等于", "value": "$le"}]}]}], "rules": []}'
#不允许激活配置，当前TMk跟进记录在9999天内
data8='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "latestTmkFollowTimeLogic", "compareType": "$le", "compareValue": "9999", "ruleKeyCascade": null, "optionalValues": null, "inputType": "text", "type": 2, "condition": {"unit": "天", "min": 0, "max": 10000}, "compareTypeList": [{"label": "小于等于", "value": "$le"}]}]}], "rules": []}'
#咕比-入池规则配置
data9='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "courseMealLogic", "compareType": "$in", "compareValue": [635], "ruleKeyCascade": null, "optionalValues": null, "inputType": "courseMeal-selector", "type": 3, "condition": null, "compareTypeList": [{"label": "满足其一", "value": "$in"}]}]}], "rules": []}'
#咕比-激活池池规则配置
data10='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "leadsAgeLogic", "compareType": "$ge", "compareValue": "1", "ruleKeyCascade": null, "optionalValues": null, "inputType": "text", "type": 2, "condition": null, "compareTypeList": [{"label": "大于", "value": "$gt"}, {"label": "小于", "value": "$lt"}, {"label": "等于", "value": "$eq"}, {"label": "大于等于", "value": "$ge"}, {"label": "小于等于", "value": "$le"}]}]}], "rules": []}'
#咕比-入池规则配置2
data11='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "courseMealLogic", "compareType": "$in", "compareValue": [635], "ruleKeyCascade": null, "optionalValues": null, "inputType": "courseMeal-selector", "type": 3, "condition": null, "compareTypeList": [{"label": "满足其一", "value": "$in"}]}, {"ruleKey": "channelLogic", "compareType": "$in", "compareValue": [1000], "ruleKeyCascade": null, "optionalValues": null, "inputType": "channel-selector", "type": 3, "condition": null, "compareTypeList": [{"label": "满足其一", "value": "$in"}]}]}], "rules": []}'
#画啦啦-允许激活范围
data12='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"compareType": "$in", "ruleKey": "incomingNotifyTypeLogic", "compareValue": [2, 3], "ruleKeyCascade": [], "optionalValues": [{"value": 1, "label": "注册", "children": null}, {"value": 2, "label": "登录", "children": null}, {"value": 3, "label": "引流订单", "children": null}], "compareTypeList": [{"label": "等于", "value": "$in"}, {"label": "不在列表中", "value": "$nin"}], "inputType": "multiple", "condition": null, "type": 3}]}], "rules": []}'
#画啦啦-不允许激活范围
data13='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "leadsTransformedLogic", "compareType": "$eq", "compareValue": true, "ruleKeyCascade": null, "optionalValues": [{"value": true, "label": "是", "children": null}, {"value": false, "label": "否", "children": null}], "inputType": "select", "type": 1, "condition": null, "compareTypeList": [{"label": "等于", "value": "$eq"}]}, {"compareType": "$gt", "ruleKey": "leadsAgeLogic", "compareValue": "23", "ruleKeyCascade": [], "optionalValues": null, "compareTypeList": [{"label": "等于", "value": "$eq"}, {"label": "大于", "value": "$gt"}, {"label": "小于", "value": "$lt"}, {"label": "大于等于", "value": "$ge"}], "inputType": "text", "condition": {"unit": "岁", "min": 0, "max": 100}, "type": 2}]}], "rules": []}'
#画啦啦-渠道更新规则1
data14='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "incomingChannelLogic", "compareType": "$in", "compareValue": [{"ids": [5, 370, 1616]}], "ruleKeyCascade": null, "optionalValues": null, "inputType": "channel-selector", "type": 1, "condition": null, "compareTypeList": [{"label": "等于", "value": "$in"}, {"label": "不在列表中", "value": "$nin"}]}]}], "rules": []}'
#画啦啦-渠道更新规则2
data15='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "incomingChannelLogic", "compareType": "$nin", "compareValue": [{"ids": [5, 370, 1616]}], "ruleKeyCascade": null, "optionalValues": null, "inputType": "channel-selector", "type": 1, "condition": null, "compareTypeList": [{"label": "等于", "value": "$in"}, {"label": "不在列表中", "value": "$nin"}]}]}], "rules": []}'
#画啦啦-剔除首发学员
data16='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "lastActiveNotifyTypeLogic", "compareType": "$in", "compareValue": [2], "ruleKeyCascade": null, "optionalValues": [{"value": 1, "label": "注册", "children": null}, {"value": 2, "label": "登录", "children": null}, {"value": 3, "label": "引流订单", "children": null}], "inputType": "multiple", "type": 3, "condition": null, "compareTypeList": [{"label": "等于", "value": "$in"}, {"label": "不在列表中", "value": "$nin"}]}]}], "rules": []}'
#画啦啦-剔除成交学员
data17='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "lastActiveChannelLogic", "compareType": "$in", "compareValue": [{"ids": [5, 370, 1616]}], "ruleKeyCascade": null, "optionalValues": null, "inputType": "channel-selector", "type": 1, "condition": null, "compareTypeList": [{"label": "等于", "value": "$in"}, {"label": "不在列表中", "value": "$nin"}]}]}], "rules": []}'
#咕比-入池规则配置
data18='{"logic": "$or", "subRuleTreeNode": [{"logic": "$and", "subRuleTreeNode": [], "rules": [{"ruleKey": "courseMealLogic", "compareType": "$in", "compareValue": [1693], "ruleKeyCascade": null, "optionalValues": null, "inputType": "courseMeal-selector", "type": 3, "condition": null, "compareTypeList": [{"label": "满足其一", "value": "$in"}]}]}], "rules": []}'

data_list = [data1, data2, data3, data4, data5,
             data6, data7, data8, data9, data10,
             data11, data12, data13, data14, data15,
             data16, data17, data18]

def json_value(number):
    # 处理数字范围：1~17用对应数据，其他用data1（列表索引0）
    idx = number - 1 
    # 安全解析JSON（可选：增加异常处理，避免解析失败崩溃）
    try:
        return json.loads(data_list[idx])
    except json.JSONDecodeError as e:
        print(f"JSON解析失败：{e}")
        return None  # 或返回默认值/抛异常，根据需求调整
    
def select_user_pool_relation(userid,pool_type,environment=None):
    if environment == "test":
        mysql_conn =pymysql.connect(host='10.4.32.47', port=3306, user='shdev', password='6JrpIH4DbtE1w2YH', db='cc_leads', charset='utf8')
    else:
        mysql_conn = pymysql.connect(host='preprod-public-mysql-rw.vipthink.net', port=3306, user='ywxt',
                                 password='YW4sLR910Ndt', db='cc_leads', charset='utf8')
    cursor = mysql_conn.cursor()
    sql = f"SELECT pool_type FROM `cc_leads`.`leads_pool_relation` WHERE `uuid` = {userid} AND `biz_id` = '15' ORDER BY id desc limit 1;"
    try:
        cursor.execute(sql)
        mysql_conn.commit()
        result = cursor.fetchone()
        if result is not None:
            if result[0] == pool_type:
                return int(1)
            else:
                return False
        else:
            return False
    except Exception as e:
        mysql_conn.rollback()
        print("数据查询失败：", e)
    finally:
        cursor.close()
        mysql_conn.close()
        
# def update_user_baseinfo(mobile,environment):
#     if environment == "test":
#         mysql_conn =pymysql.connect(host='testdb.61info.com', port=3306, user='root', password='dbtest', charset='utf8')
#     else:
#         mysql_conn =pymysql.connect(host='db.preprod.61draw.com', port=3306, user='root', password='dbtest', charset='utf8')
#     cursor = mysql_conn.cursor()
#     sql = "set @Account ='%s'" %mobile
#     sql1="set @UserId = (SELECT UserId FROM i61.userinfo  WHERE Account = @Account);"
#     sql2=f"UPDATE `i61_leads`.`leads_user_info` SET `user_name` = @Account, `wx_code` =  @Account,`country` = '中国', `province` = '北京', `belong_area` = '中国大陆', `city` = '北京市', `area` = '朝阳区' WHERE `user_id` = @UserId;"
#     sql3="UPDATE `i61`.`userinfo` SET  `NickName` = @Account,RemarkName= @Account, `BirthMonth` = '2018-01-01',`timeZone` = '8', `PaintingInterest` = '高', `BasicDrawing` = '没有基础', `PaintingLearning` = '学校', `OtherOnline` = '数学' WHERE `Account` =@Account;"
#     sql5=f"UPDATE `i61`.`applystandardcourse` SET  `BirthMonth` = '2018-01-01',`Receiver` = '实物收货地址-测试', `Phone` = @Account, `Address` = '实物收货地址-测试地址,请勿发货' WHERE `UserId` = @UserId;"
#     sql6=f"INSERT INTO `i61`.`experiencefollow` (`UserId`, `TeacherId`, `GroupId`, `TableId`, `ArriveLive_del`, `ExperienceReport`, `ExperienceReportTime`, `ChildEvaluation`, `ParentEvaluation`, `BeginCourseStage`) VALUES (@UserId, 401971, 1, 3, 0, '', NOW(), '[null,null,null,null,null]', '[1,null,null,null,null,null,null,\"1\",6,null]', 0);"
#     sql4="INSERT INTO `i61-hll-manager`.`questionnaire_user_intro` (`user_id`, `questionnaire_id`, `teacher_id`, `answer`, `status`, `gmt_create`, `gmt_modify`) VALUES (@UserId, 2, 401971, '{\"51\":77,\"14\":\"提高绘画技巧\"}', 2,NOW(), NOW());"
#     try:
#         if mobile is not None:
#             cursor.execute(sql)
#             cursor.execute(sql1)
#             cursor.execute(sql2)
#             cursor.execute(sql3)
#             cursor.execute(sql5)
#             cursor.execute(sql6)
#             cursor.execute(sql4)
#             mysql_conn.commit()
#         else:
#             return False
#     except Exception as e:
#         mysql_conn.rollback()
#         print("数据修改失败：", e)
#     finally:
#         cursor.close()
#         mysql_conn.close()
        
def update_user_baseinfo(mobile,environment):
    if environment == "test":
        mysql_conn =pymysql.connect(host='testdb.61info.com', port=3306, user='root', password='dbtest', charset='utf8')
    else:
        mysql_conn =pymysql.connect(host='db.preprod.61draw.com', port=3306, user='root', password='dbtest', charset='utf8')
            # 获取当前时间
    # current_time = datetime.now()

    # 获取用户地址表的最大id
    max_id = mysql_conn.fetchone("SELECT MAX(id) FROM `i61`.recieverinfo")
    # 给max_id加1
    next_id = max_id['MAX(id)'] + 1

    sql = "set @Account ='%s'" % mobile
    sql_user = "SELECT UserId FROM i61.userinfo  WHERE Account ='%s'" % mobile
    sql1 = "set @UserId = (SELECT UserId FROM i61.userinfo  WHERE Account = @Account);"
    sql2 = f"UPDATE `i61_leads`.`leads_user_info` SET `user_name` = @Account, `wx_code` =  @Account,`country` = '中国', `province` = '北京', `belong_area` = '中国大陆', `city` = '北京市', `area` = '朝阳区' WHERE `user_id` = @UserId;"
    sql3 = "UPDATE `i61`.`userinfo` SET  `NickName` = @Account,RemarkName= @Account, `BirthMonth` = '2020-01-01',`timeZone` = '8', `PaintingInterest` = '高', `BasicDrawing` = '没有基础', `PaintingLearning` = '学校', `OtherOnline` = '数学' WHERE `Account` =@Account;"
    sql5 = f"UPDATE `i61`.`applystandardcourse` SET  `BirthMonth` = '2019-01-01',`Receiver` = '实物收货地址-测试', `Phone` = @Account, `Address` = '实物收货地址-测试地址,请勿发货' WHERE `UserId` = @UserId;"
    sql6 = f"REPLACE INTO `i61`.`experiencefollow` (`UserId`, `TeacherId`, `GroupId`, `TableId`, `ArriveLive_del`, `ExperienceReport`, `ExperienceReportTime`, `ChildEvaluation`, `ParentEvaluation`, `BeginCourseStage`) VALUES (@UserId, 401971, 1, 3, 0, '', NOW(), '[null,null,null,null,null]', '[1,null,null,null,null,null,null,\"1\",6,null]', 0);"
    sql4 = "REPLACE INTO `i61-hll-manager`.`questionnaire_user_intro` (`user_id`, `questionnaire_id`, `teacher_id`, `answer`, `status`, `gmt_create`, `gmt_modify`) VALUES (@UserId, 2, 401971, '{\"51\":77,\"14\":\"提高绘画技巧\"}', 2,NOW(), NOW());"
    sql7="INSERT INTO i61.recieverinfo (Id,Name,Tel,area_code,country,post_code,province,City,District,DetailAddress,DefaultFlag,UserId,`Type`,UpdateTime,bi_update_time) VALUES ('{}' ,'测试学员',@Account,'86','中国','510700','广东省','广州市','黄埔区','11',1, @UserId,0,NOW() , NOW() );".format(next_id)

    try:
        if mobile is not None:
            userid = mysql_conn.fetchone(sql_user)
            print(userid['UserId'])
            if userid is None:
                return False
            else:
                str1="手机号："+mobile
                str2="用户id："+str(userid['UserId'])

                mysql_conn.execute(sql)
                mysql_conn.execute(sql1)
                mysql_conn.execute(sql2)
                mysql_conn.execute(sql3)
                mysql_conn.execute(sql5)
                mysql_conn.execute(sql6)
                mysql_conn.execute(sql4)
                # userid_address = mysql_conn.fetchone("SELECT UserId FROM `i61`.recieverinfo where UserId = @UserId")
                # if userid_address is None:
                mysql_conn.execute(sql7)
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
    # re=select_user_active_log_reason(17403783,"符合激活反向配置，不允许激活 ==》 ")
    # re=update_or_insert_student_pool(22644761)
    # re=select_user_unlockstatus("test")
    # re=select_user_mobile_encrypt(60000650,"test")
    # re=select_user_and_mobile_encrypt("test")
    # re=json_value(18)
    
    # re=select_user_pool_relation(60000617,11,"test")
    # re=update_user_baseinfo('12026316742',"test")
    re=update_user_baseinfo('12026319510',"pre")
    
    # re = UpdateUserInfoRun().UpdateUserInfo(orderNum,choose_url)
    print("执行结束,",re)
    # print("执行结束88,",orderNum,re)


