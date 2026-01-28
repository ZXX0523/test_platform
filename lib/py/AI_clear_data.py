
from bin.runMySQL import mysqlMain

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







if __name__ == '__main__':
    print("执行开始。。。。")
    choose_url = "test" # test, pro
    # Authorization = ''
    orderNum = '19115762043'
    re=select_user_active_log_reason(17403783,"符合激活反向配置，不允许激活 ==》 ")
    # re = UpdateUserInfoRun().UpdateUserInfo(orderNum,choose_url)
    print("执行结束,",re)
    # print("执行结束88,",orderNum,re)


