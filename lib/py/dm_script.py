import uuid
from datetime import datetime, timedelta, timezone
import re

# from operate_basics.database_mainpulation import database
import requests
import json
import time

from bin.runMySQL import mysqlMain

import re
class Dm_Script():
    def UpdateUserOpenclasstime(self,choose_url,external_user,open_class_time):

        if choose_url == "test":
            mysql_conn = mysqlMain('MySQL-Gubi-test')
        else:
            mysql_conn = mysqlMain('MySQL-Gubi-preprod')
        sql = "select esu.enrollment_id from experience_sign_up esu inner join enrollment  e on esu.enrollment_id = e.id where user_id='{}' and esu.course_category_id=4 order by esu.id desc limit 1".format(external_user)
        sql_result = mysql_conn.fetchone(sql)
        print(sql_result)
        if sql_result== None :
            return False, "修改失败，查询不到该学员的批次信息"
        else:
            enrollment_id = sql_result['enrollment_id']
            sql1 = "UPDATE enrollment SET open_course_time = '{}' WHERE id = '{}';".format(open_class_time,enrollment_id)
            try:
                mysql_conn.execute(sql1)
            except Exception as e:
                return False, "执行异常",
            str="开课日更新为：",open_class_time
            return True, "修改成功", str


    def select_dm_wechat_data_for_name(self, name,business_id):
        sql1 = """SELECT * FROM `i61-bizcenter-copilot`.`dm_wechat_conversation` WHERE `nick_name` = '{}' and business_id = {} limit 1""".format(
            name,business_id)
        print(sql1)
        mysql_conn = mysqlMain('MySQL-Liuyi-test')
        sql_result = mysql_conn.fetchall(sql1)
        print(sql_result)
        if len(sql_result)== 0:
            print("没有查询到数据")
            return None

        dm_wechat_conversation_id = sql_result[0]["id"]
        conversation_id =  sql_result[0]["dify_conversation_id"]
        wechat_id =   sql_result[0]["wechat_id"]
        print(wechat_id)


        print(dm_wechat_conversation_id)
        data = {
            "dm_wechat_conversation_id":dm_wechat_conversation_id,
            "conversation_id":conversation_id,
            "wechat_id":wechat_id
        }
        print(data)
        return data


    def select_dm_wechat_data(self, wechat_id):
        sql1 = """SELECT * FROM `i61-bizcenter-copilot`.`dm_wechat_conversation` WHERE `wechat_id` = '{}'""".format(
            wechat_id)

        print(sql1)
        # sql_result1 = database("mysql_hualala_test", "i61-bizcenter-copilot").database_manipulation(operate_sql_type=1,
        #                                                                                             sql=sql1)
        mysql_conn = mysqlMain('MySQL-Liuyi-test')
        sql_result1 = mysql_conn.fetchall(sql1)
        print(sql_result1)
        if len(sql_result1)== 0:
            print("没有查询到数据")
            return None

        dm_wechat_conversation_id = sql_result1[0]["id"]
        conversation_id =  sql_result1[0]["dify_conversation_id"]
        wechat_id =   sql_result1[0]["wechat_id"]

        # dm_wechat_conversation_id = sql_result1[0][0]
        # conversation_id = sql_result1[0][13]
        # wechat_id = sql_result1[0][4]
        print(dm_wechat_conversation_id)
        data = {
            "dm_wechat_conversation_id":dm_wechat_conversation_id,
            "conversation_id":conversation_id,
            "wechat_id":wechat_id
        }
        return data


    def select_dm_wechat_data2(self, id):
        sql1 = """SELECT * FROM `i61-bizcenter-copilot`.`dm_wechat_conversation` WHERE `id` = '{}'""".format(
            id)
        # sql_result1 = database("mysql_hualala_test", "i61-bizcenter-copilot").database_manipulation(operate_sql_type=1,
        #                                                                                             sql=sql1)
        mysql_conn = mysqlMain('MySQL-Liuyi-test')
        sql_result1 = mysql_conn.fetchall(sql1)
        if len(sql_result1)== 0:
            print("没有查询到数据")
            return None

        dm_wechat_conversation_id = sql_result1[0]["id"]
        conversation_id =  sql_result1[0]["dify_conversation_id"]
        wechat_id =   sql_result1[0]["wechat_id"]

        # dm_wechat_conversation_id = sql_result1[0][0]
        # conversation_id = sql_result1[0][13]
        # wechat_id = sql_result1[0][4]

        data = {
            "dm_wechat_conversation_id":dm_wechat_conversation_id,
            "conversation_id":conversation_id,
            "wechat_id":wechat_id
        }
        return data



    def delete_dm_wechat_data(self, wechat_id):

        sql1 = """DELETE FROM `i61-bizcenter-copilot`.`dm_wechat_conversation` WHERE `wechat_id` = '{}';""".format(
            wechat_id)
        print(sql1)
        mysql_conn = mysqlMain('MySQL-Liuyi-test')
        mysql_conn.execute(sql1)
        sql2 = """DELETE FROM `i61-bizcenter-copilot`.`dm_wechat_user_intent` WHERE `wechat_id` = '{}';""".format(
            wechat_id)
        print(sql2)
        mysql_conn.execute(sql2)



    def delete_cw_biz_external_user_relation_data(self,wechat_id):

        sql1 = """DELETE FROM `i61-bizcenter-corpwechat`.`cw_biz_external_user_relation` WHERE external_user_id = '{}';""".format(
            wechat_id)
        # sql_result1 = database("mysql_hualala_test", "i61-bizcenter-copilot").database_manipulation(operate_sql_type=2,
        #                                                                                             sql=sql1)
        mysql_conn = mysqlMain('MySQL-Liuyi-test')
        mysql_conn.execute(sql1)

    def select_cw_biz_external_user_relation_data(self,wechat_id):
        sql1 = """SELECT * FROM `i61-bizcenter-corpwechat`.`cw_biz_external_user_relation` WHERE `external_user_id` = '{}'""".format(
            wechat_id)
        # sql_result1 = database("mysql_hualala_test", "i61-bizcenter-copilot").database_manipulation(operate_sql_type=1,
        #                                                                                             sql=sql1)
        mysql_conn = mysqlMain('MySQL-Liuyi-test')
        sql_result1 = mysql_conn.fetchall(sql1)
        if len(sql_result1)== 0:
            print("没有查询到数据")
            return None

        bind_mobile = sql_result1[0]["bind_mobile"]
        data = {
            "bind_mobile":bind_mobile
        }
        return data


    def delete_cw_chat_data_data(self,external_user):
        sql = "DELETE FROM `i61-bizcenter-corpwechat`.cw_chat_data WHERE external_user = '{}' and msg_time > 1720348933341".format(external_user)
        print(sql)
        # delete_cw_chat_data_result = database("mysql_hualala_test" ,"i61-bizcenter-corpwechat").database_manipulation(operate_sql_type=2, sql=sql)
        mysql_conn = mysqlMain('MySQL-Liuyi-test')
        mysql_conn.execute(sql)

    def delete_cw_biz_external_user_relation_history_data(self,user_id,external_user):
        sql = "DELETE FROM `i61-bizcenter-corpwechat`.cw_biz_external_user_relation_history WHERE user_id = '{}' and external_user_id = '{}' ".format(user_id,external_user)
        print(sql)
        # delete_cw_chat_data_result = database("mysql_hualala_" + self.data_env_switch,"i61-bizcenter-corpwechat").database_manipulation(operate_sql_type=2, sql=sql)
        mysql_conn = mysqlMain('MySQL-Liuyi-test')
        mysql_conn.execute(sql)

    def dm_wechat_script_all(self,user_id,name,business_id,clear_wechat_data):
        print("开始执行清理数据")
        print("打印环境choose_env：", user_id, name, business_id,clear_wechat_data)
        business_id_int=int(business_id)

        clear_wechat_data_int=int(clear_wechat_data)
        try:
            print("17123123")
            select_data = self.select_dm_wechat_data_for_name(name, business_id)
            if select_data == None:
                print("没有数据")
                return False, "查询不到该会话数据"
            wechat_id = select_data["wechat_id"]

            print("开始处理删除学员会话相关表")
            self.delete_dm_wechat_data(wechat_id)

            if clear_wechat_data_int ==1:
                print("开始处理cw_chat_data相关表")
                self.delete_cw_chat_data_data(wechat_id)

                print("开始处理cw_biz_external_user_relation_history相关表")
                self.delete_cw_biz_external_user_relation_history_data(user_id,wechat_id)

                phone_number_data = self.select_cw_biz_external_user_relation_data(wechat_id)
                print(phone_number_data)

                print("开始删除cw_biz_external_user_relation")
                self.delete_cw_biz_external_user_relation_data(wechat_id)

            print("数据处理成功")
            return True, "处理成功"

        except Exception as e:
            print("数据处理异常")
            return False, "执行异常"

    def insert_user_chat_data(self,env,user_id,external_user_id,data_str,brand_code):
        data_str = re.sub(r'[\x00-\x1F]|\x7F', '', data_str)  # 删除控制字符
        data_str = re.sub(r'\\(?![/u"])', r'', data_str)  # 修复非法反斜杠
        cleaned_data = data_str.encode('utf-8', errors='ignore').decode('utf-8')
        data = json.loads(cleaned_data)
        try:
            # 获取当前时间戳（秒级）
            current_timestamp = int(time.time() * 1000)
            seq = int(time.time())

            for item in data:
                # 生成唯一msg_id（UUID4）
                msg_id: str = str(uuid.uuid4())

                # 提取内容和角色
                content = item['content']
                role = item['role']
                # 确定发送方和接收方
                if role == 'user':
                    from_user = external_user_id
                    to_user = user_id
                else:
                    from_user = user_id
                    to_user = external_user_id
                print(seq,msg_id,from_user,to_user,to_user,current_timestamp,content)
                # 构造插入语句
                sql = "INSERT INTO `i61-bizcenter-corpwechat`.cw_chat_data (biz_code,corpid,seq,msg_id,msg_type,`action`,from_user,to_user,external_user,room_id,msg_time,content,transfer_file_status,create_time,update_time) VALUES ('{}','ww0af8bc32673add13','{}','{}' ,'text','send', '{}' , '{}' ,'{}' ,NULL,'{}' , '{}' ,2,'2025-08-13 10:34:08','2025-08-13 10:34:08')".format(brand_code,seq,msg_id,from_user,to_user,external_user_id,current_timestamp,content)
                print(sql)
                # 执行插入
                if env=='test':
                    mysql_conn = mysqlMain('MySQL-Liuyi-test')
                else:
                    mysql_conn = mysqlMain('MySQL-Liuyi-preprod')

                sql_result1=mysql_conn.execute(sql)
                print(sql_result1)
                # 可以根据需要调整时间戳（如果需要更精确的时间顺序）
                seq += 1
                time.sleep(1)
                current_timestamp = int(time.time() * 1000)  # 毫秒级时间戳
            data=f"成功插入 {len(data)} 条数据"
            print(data)
            return True, data

        except Exception as e:
            data=f"插入失败: {str(e)}"
            return False, data
        # finally:
            # if cursor:
            #     cursor.close()
            # if conn:
            #     conn.close()
    def update_course_finished_status(self,choose_url,user_id,finished):
        try:
            if choose_url == "test":
                mysql_conn = mysqlMain('MySQL-Gubi-test')
            else:
                mysql_conn = mysqlMain('MySQL-Gubi-preprod')
            sql="""
                select uc.id
                from user_course_line ucl
                inner join (select id
                from user_course_line
                where user_id = '{}'
                and course_category_id = 4
                and course_type = 1 order by id desc limit 1) mucl on mucl.id = ucl.id
                inner join user_course_line_stage ucls on ucl.id = ucls.user_course_line_id
                inner join user_course uc on ucls.id = uc.user_course_line_stage_id
                order by uc.id asc limit 300000
                """.format(user_id)
            sql_result1 = mysql_conn.fetchall(sql)
            if len(sql_result1) == 0:
                print("没有查询到数据")
                return False,"没有查询到学员的体验课数据"
            else:
                now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(finished)
                course_id=sql_result1[0]["id"]
                if int(finished) == 1:
                    sql="UPDATE pjx.user_course SET course_status=15,comment_time='{}' WHERE id='{}';".format(now_time,course_id)
                else:
                    sql="UPDATE pjx.user_course SET course_status=0,comment_time=NULL WHERE id='{}';".format(course_id)
                mysql_conn.execute(sql)
                return True,"更新成功"
        except Exception as e:
            data=f"插入失败: {str(e)}"
            return False, data

    def update_go_pk_record(self,choose_url,user_id,win,lose):
        try:
            if choose_url == "test":
                mysql_conn = mysqlMain('MySQL-Gubi-test')
            else:
                mysql_conn = mysqlMain('MySQL-Gubi-preprod')

            # if not isinstance(int(win), int) or not isinstance(int(lose), int):
            #     return False,"对弈次数非正整数"
            if user_id is not None and win is not None and lose is not None:
                sql_pk_record ='DELETE FROM pjx_go.t_go_play_pk_record where user_id ={}'.format(user_id)
                mysql_conn.execute(sql_pk_record)
                sql_win_insert ="INSERT INTO pjx_go.t_go_play_pk_record VALUES(NULL, 2, {}, '2026-01-19 18:09:05', 1, '9路吃子', 1, 1, 'Ceslin', 46, 'test', 2, 2, 2, 0, 0, 1, 3, 5.5, 3, 0, 0, 1, NULL, 1, 1, 0, '白吃3子', 0, 3, 0, 0, 0.00, 0.00, 33, 16, '2025-12-04 14:56:11', '2026-01-19 18:09:05');".format(user_id)
                sql_lose_insert ="INSERT INTO pjx_go.t_go_play_pk_record VALUES(NULL, 2, {}, '2026-01-19 18:09:05', 1, '9路吃子', 1, 1, 'Ceslin', 46, 'test', 2, 2, 2, 0, 0, 1, 3, 5.5, 3, 0, 0, 1, NULL, 2, 1, 0, '白吃3子', 0, 3, 0, 0, 0.00, 0.00, 33, 16, '2025-12-04 14:56:11', '2026-01-19 18:09:05');".format(user_id)
                win_count=0
                lose_count = 0
                while int(win) > win_count:
                    mysql_conn.execute(sql_win_insert)
                    win_count += 1  # 等价于 A = A + 1
                    print(f"插入第：{win_count}条数据")  # 打印过程，可根据需要删除
                while int(lose) > lose_count:
                    mysql_conn.execute(sql_lose_insert)
                    lose_count += 1  # 等价于 A = A + 1
                    print(f"插入第：{lose_count}条数据")  # 打印过程，可根据需要删除
                return True,"对弈数据更新成功"
            else:
                return False, "对弈数据更新成功"
        except Exception as e:
            data=f"插入失败: {str(e)}"
            return False, data

    def delete_review_record(self,choose_url,user_id):
        try:
            if choose_url == "test":
                mysql_conn = mysqlMain('MySQL-Gubi-test')
            else:
                mysql_conn = mysqlMain('MySQL-Gubi-preprod')

            # if not isinstance(int(win), int) or not isinstance(int(lose), int):
            #     return False,"对弈次数非正整数"
            if user_id is not None :
                sql_delect_review_time ='DELETE FROM pjx.help_util_user_remind_relation WHERE user_id={};'.format(user_id)
                mysql_conn.execute(sql_delect_review_time)

                if choose_url=='test':
                    mysql_conn = mysqlMain('MySQL-Liuyi-test')
                else:
                    mysql_conn = mysqlMain('MySQL-Liuyi-preprod')
                sql_select_user_review_tag = """
                    SELECT c2.id,c1.user_id,c1.external_user_id FROM 
                      `i61-bizcenter-corpwechat`.cw_biz_external_user_relation AS c1
                    INNER JOIN `i61-bizcenter-corpwechat`.cw_external_user_follow AS c2
                    ON c1.user_id = c2.user_id AND c1.external_user_id = c2.external_user_id
                    WHERE c1.biz_user_id = {}
                    ORDER BY c1.id DESC;
                        """.format(user_id)

                sql_result1 = mysql_conn.fetchall(sql_select_user_review_tag)
                if len(sql_result1) != 0:
                    follow_id = sql_result1[0]["id"]
                    print(follow_id)
                    sql_delete_user_review_tag = "DELETE FROM `i61-bizcenter-corpwechat`.cw_external_user_follow_tag WHERE follow_id={};".format(follow_id)
                    mysql_conn.execute(sql_delete_user_review_tag)
                return True,"复盘数据清理成功"
            else:
                return False, "请输入用户id"
        except Exception as e:
            data=f"更新失败: {str(e)}"
            return False, data
    def _fetch_st_ids(self,choose_url, user_id):
        """私有方法：获取用户demo课的st_id列表"""
        if choose_url=="test":
            url = 'https://sht-cc.vipthink.cn/gateway/route__cc/api_admin.php/core/route__php_project_common/mvp/user_demo_lesson'
        else:
            url = 'https://preprod-cc.vipthink.cn/gateway/route__cc/api_admin.php/core/route__php_project_common/mvp/user_demo_lesson'
        headers = {'Content-Type': 'application/json'}
        payload = {"user_id": str(user_id)}


        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            print(result)
            if result.get('code') == 0 and 'data' in result:
                return [item['st_id'] for item in result['data'] if 'st_id' in item]
            else:
                print(f"获取st_id失败: {result.get('info', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"获取st_id时发生错误: {str(e)}")
            return []

    def _cancel_demo_lesson(self, choose_url,user_id, st_id):
        """私有方法：取消单个demo课"""
        if choose_url=="test":
            url = 'https://sht-cc.vipthink.cn/gateway/route__cc/api_admin.php/core/route__php_project_common/mvp/cancel_demo_lesson'
        else:
            url = 'https://preprod-cc.vipthink.cn/gateway/route__cc/api_admin.php/core/route__php_project_common/mvp/cancel_demo_lesson'
        headers = {'Content-Type': 'application/json'}
        payload = {
            "user_id": str(user_id),
            "st_id": st_id
        }
        print(payload)

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()

            if result.get('code') == 0:
                print(f"成功取消st_id: {st_id}")
                return True
            else:
                print(f"取消st_id {st_id} 失败: {result.get('info', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"取消st_id {st_id} 时发生错误: {str(e)}")
            return False

    def cancel_user_demo_lessons(self, choose_url,user_id):
        """取消用户的所有demo课"""
        print(f"\n开始处理用户 {user_id} 的demo课...")

        st_ids = self._fetch_st_ids(choose_url,user_id)
        print(st_ids)
        if not st_ids:
            print("没有找到可处理的demo课")
            return False,"没有找到可处理的demo课"

        print(f"获取到 {len(st_ids)} 个st_id: {st_ids}")

        results = []
        for st_id in st_ids:
            success = self._cancel_demo_lesson(choose_url,user_id, st_id)
            results.append(success)

        return True,"取消demo课成功"

if __name__ == '__main__':
    print("执行开始。。。。")
    choose_url = "test" # test, pro
    external_user=601348494
    open_class_time='2025-09-21'
    # re = Dm_Script().UpdateUserOpenclasstime(choose_url,external_user,open_class_time)

    # re = Dm_Script().dm_wechat_script_all("x","Flow",16,0)

    # Dm_Script().dm_wechat_script_all("2cbd0ce7e7a9ded1922e74164b742a2d","[太阳]白日梦想家🍊",16,0)
    # Dm_Script().dm_wechat_script_all("x","x",16,1)
    # re= UserComingRun().GetBizUserid(orderNum,choose_url,choose_type,mobile,86)
    # re=UserComingRun().submitUserComing(accessToken,biz_user_id,choose_url)

    # re = Dm_Script().update_course_finished_status(choose_url,601348506,0)

    # re = Dm_Script().update_go_pk_record(choose_url,601348506,1,0)
    # re = Dm_Script().delete_review_record(choose_url,601348506)
    re = Dm_Script().cancel_user_demo_lessons(2095639448)
    print(re)
    print("执行结束88,")


