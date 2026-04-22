"""
DM工具箱 - 数据库操作脚本
提供用户、课程、学情、直播课等数据的增删改查功能
"""

import uuid
from datetime import datetime, timedelta, timezone
import re
import requests
import json
import time
import random
import redis
import sys
import os

# 添加项目根目录到系统路径，解决模块导入问题
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from bin.runMySQL import mysqlMain


class Dm_Script():
    """
    DM工具箱主类
    封装各类数据库操作方法，支持测试/预发环境切换
    """

    # ==================== 配置信息 ====================

    # 数据库连接配置：按环境(test/pre)和业务类型(liuyi/gubi/ob)分类
    DB_CONFIG = {
        'liuyi': {'test': 'MySQL-Liuyi-test', 'pre': 'MySQL-Liuyi-preprod'},
        'gubi': {'test': 'MySQL-Gubi-test', 'pre': 'MySQL-Gubi-preprod'},
        'ob': {'test': 'MySQL-ob-test', 'pre': 'MySQL-ob-preprod'}
    }

    # 接口URL配置：demo课相关接口
    URL_CONFIG = {
        'test': {
            'demo_lesson': 'https://sht-cc.vipthink.cn/gateway/route__cc/api_admin.php/core/route__php_project_common/mvp/user_demo_lesson',
            'cancel_demo': 'https://sht-cc.vipthink.cn/gateway/route__cc/api_admin.php/core/route__php_project_common/mvp/cancel_demo_lesson'
        },
        'pre': {
            'demo_lesson': 'https://preprod-cc.vipthink.cn/gateway/route__cc/api_admin.php/core/route__php_project_common/mvp/user_demo_lesson',
            'cancel_demo': 'https://preprod-cc.vipthink.cn/gateway/route__cc/api_admin.php/core/route__php_project_common/mvp/cancel_demo_lesson'
        }
    }

    # ==================== 私有方法 ====================

    def _get_mysql_conn(self, env, db_type='liuyi'):
        """获取数据库连接"""
        env_key = 'test' if env == 'test' else 'pre'
        db_name = self.DB_CONFIG.get(db_type, {}).get(env_key, 'MySQL-Liuyi-test')
        return mysqlMain(db_name)

    def _get_url(self, env, url_type):
        """获取接口URL"""
        env_key = 'test' if env == 'test' else 'pre'
        return self.URL_CONFIG.get(env_key, {}).get(url_type, '')

    def _delete_redis_key(self, choose_url, key_pattern):
        """删除Redis缓存键，用于数据更新后清除缓存"""
        try:
            # 根据环境选择Redis主机
            redis_host = 'redis-test.61info.cn' if choose_url == "test" else 'preprod1.61draw.com'
            redis_client = redis.Redis(host=redis_host, port=6379, db=7)
            if redis_client.exists(key_pattern):
                redis_client.delete(key_pattern)
                print(f"已删除Redis缓存键: {key_pattern}")
            else:
                print(f"Redis缓存键不存在: {key_pattern}")
            redis_client.close()
        except Exception as redis_e:
            print(f"删除Redis缓存失败: {str(redis_e)}")

    def _select_dm_wechat_data(self, env, where_clause):
        """查询微信会话数据（通用查询方法）"""
        sql = f"""SELECT * FROM `i61-bizcenter-copilot`.`dm_wechat_conversation` WHERE {where_clause}"""
        print(sql)
        mysql_conn = self._get_mysql_conn(env, 'liuyi')
        sql_result = mysql_conn.fetchall(sql)
        print(sql_result)
        
        if len(sql_result) == 0:
            print("没有查询到数据")
            return None
        
        # 返回关键信息：会话ID、对话ID、微信ID
        return {
            "dm_wechat_conversation_id": sql_result[0]["id"],
            "conversation_id": sql_result[0]["dify_conversation_id"],
            "wechat_id": sql_result[0]["wechat_id"]
        }

    def _fetch_st_ids(self, choose_url, user_id):
        """获取用户demo课的st_id列表（用于取消demo课）"""
        url = self._get_url(choose_url, 'demo_lesson')
        headers = {'Content-Type': 'application/json'}
        payload = {"user_id": str(user_id)}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            print(result)
            if result.get('code') == 0 and 'data' in result:
                # 提取所有st_id
                return [item['st_id'] for item in result['data'] if 'st_id' in item]
            else:
                print(f"获取st_id失败: {result.get('info', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"获取st_id时发生错误: {str(e)}")
            return []

    def _cancel_demo_lesson(self, choose_url, user_id, st_id):
        """取消单个demo课"""
        url = self._get_url(choose_url, 'cancel_demo')
        headers = {'Content-Type': 'application/json'}
        payload = {"user_id": str(user_id), "st_id": st_id}
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

    # ==================== 用户相关操作 ====================

    def UpdateUserOpenclasstime(self, choose_url, external_user, open_class_time):
        """更新用户开课时间"""
        mysql_conn = self._get_mysql_conn(choose_url, 'gubi')
        # 查询用户最近的体验课批次
        sql = "select esu.enrollment_id from experience_sign_up esu inner join enrollment e on esu.enrollment_id = e.id where user_id='{}' and esu.course_category_id=4 order by esu.id desc limit 1".format(external_user)
        sql_result = mysql_conn.fetchone(sql)
        print(sql_result)
        if sql_result is None:
            return False, "修改失败，查询不到该学员的批次信息"
        
        enrollment_id = sql_result['enrollment_id']
        # 更新开课时间
        sql1 = "UPDATE enrollment SET open_course_time = '{}' WHERE id = '{}';".format(open_class_time, enrollment_id)
        try:
            mysql_conn.execute(sql1)
            # 清除Redis缓存
            redis_key = f"i61-eos-copilot:cache:pjx:getUserOpenCourseTimeList{external_user}_1"
            self._delete_redis_key(choose_url, redis_key)
        except Exception as e:
            return False, "执行异常"
        return True, "修改成功", f"开课日更新为：{open_class_time}"

    def select_dm_wechat_data_for_name(self, env, name, business_id):
        """根据名称查询微信数据"""
        return self._select_dm_wechat_data(env, f"`nick_name` = '{name}' and business_id = {business_id} limit 1")

    def select_dm_wechat_data(self, env, wechat_id):
        """根据wechat_id查询微信数据"""
        return self._select_dm_wechat_data(env, f"`wechat_id` = '{wechat_id}'")

    def select_dm_wechat_data2(self, env, id):
        """根据id查询微信数据"""
        return self._select_dm_wechat_data(env, f"`id` = '{id}'")

    def delete_dm_wechat_data(self, env, wechat_id):
        """删除微信会话数据（同时删除会话表和意图表）"""
        mysql_conn = self._get_mysql_conn(env, 'liuyi')
        sql1 = f"""DELETE FROM `i61-bizcenter-copilot`.`dm_wechat_conversation` WHERE `wechat_id` = '{wechat_id}';"""
        print(sql1)
        mysql_conn.execute(sql1)
        sql2 = f"""DELETE FROM `i61-bizcenter-copilot`.`dm_wechat_user_intent` WHERE `wechat_id` = '{wechat_id}';"""
        print(sql2)
        mysql_conn.execute(sql2)

    def delete_cw_biz_external_user_relation_data(self, env, wechat_id):
        """删除企微外部用户关系数据"""
        sql1 = f"""DELETE FROM `i61-bizcenter-corpwechat`.`cw_biz_external_user_relation` WHERE external_user_id = '{wechat_id}';"""
        print(sql1)
        mysql_conn = self._get_mysql_conn(env, 'liuyi')
        mysql_conn.execute(sql1)

    def select_cw_biz_external_user_relation_data(self, env, wechat_id):
        """查询企微外部用户关系数据"""
        sql1 = f"""SELECT * FROM `i61-bizcenter-corpwechat`.`cw_biz_external_user_relation` WHERE `external_user_id` = '{wechat_id}'"""
        mysql_conn = self._get_mysql_conn(env, 'liuyi')
        sql_result1 = mysql_conn.fetchall(sql1)
        if len(sql_result1) == 0:
            print("没有查询到数据")
            return None
        return {"bind_mobile": sql_result1[0]["bind_mobile"]}

    def delete_cw_chat_data_data(self, env, external_user):
        """删除企微聊天数据"""
        sql = f"DELETE FROM `i61-bizcenter-corpwechat`.cw_chat_data WHERE external_user = '{external_user}' and msg_time > 1720348933341"
        print(sql)
        mysql_conn = self._get_mysql_conn(env, 'liuyi')
        mysql_conn.execute(sql)

    def delete_cw_biz_external_user_relation_history_data(self, env, user_id, external_user):
        """删除企微外部用户关系历史数据"""
        sql = f"DELETE FROM `i61-bizcenter-corpwechat`.cw_biz_external_user_relation_history WHERE user_id = '{user_id}' and external_user_id = '{external_user}'"
        print(sql)
        mysql_conn = self._get_mysql_conn(env, 'liuyi')
        mysql_conn.execute(sql)

    def dm_wechat_script_all(self, env, user_id, name, business_id, clear_wechat_data):
        """清理微信会话相关数据（批量操作，可选择性清理聊天记录）"""
        print("开始执行清理数据")
        print("打印环境choose_env：", env, user_id, name, business_id, clear_wechat_data)
        
        try:
            # 查询会话数据
            select_data = self.select_dm_wechat_data_for_name(env, name, business_id)
            if select_data is None:
                print("没有数据")
                return False, "查询不到该会话数据"
            wechat_id = select_data["wechat_id"]

            print("开始处理删除学员会话相关表")
            self.delete_dm_wechat_data(env, wechat_id)

            # 如果clear_wechat_data=1，则额外清理聊天记录和用户关系
            if int(clear_wechat_data) == 1:
                print("开始处理cw_chat_data相关表")
                self.delete_cw_chat_data_data(env, wechat_id)

                print("开始处理cw_biz_external_user_relation_history相关表")
                self.delete_cw_biz_external_user_relation_history_data(env, user_id, wechat_id)

                phone_number_data = self.select_cw_biz_external_user_relation_data(env, wechat_id)
                print(phone_number_data)

                print("开始删除cw_biz_external_user_relation")
                self.delete_cw_biz_external_user_relation_data(env, wechat_id)

            print("数据处理成功")
            return True, "处理成功"

        except Exception as e:
            print("数据处理异常")
            return False, "执行异常"

    def insert_user_chat_data(self, env, user_id, external_user_id, data_str, brand_code):
        """插入用户聊天数据（支持文本和图片消息）"""
        # 清理JSON字符串中的特殊字符
        data_str = re.sub(r'[\x00-\x1F]|\x7F', '', data_str)
        data_str = re.sub(r'\\(?![/u"])', r'', data_str)
        cleaned_data = data_str.encode('utf-8', errors='ignore').decode('utf-8')
        data = json.loads(cleaned_data)
        mysql_conn = self._get_mysql_conn(env, 'liuyi')
        
        try:
            current_timestamp = int(time.time() * 1000)
            seq = int(time.time())

            for item in data:
                msg_id = str(uuid.uuid4())
                content = item['content']
                role = item['role']
                
                # 根据角色确定发送方和接收方
                if role == 'user':
                    from_user, to_user = external_user_id, user_id
                else:
                    from_user, to_user = user_id, external_user_id
                    
                print(seq, msg_id, from_user, to_user, to_user, current_timestamp, content)
                
                # 图片消息和文本消息使用不同的SQL
                if '【图片】' in content:
                    sql = "INSERT INTO `i61-bizcenter-corpwechat`.cw_chat_data (biz_code,corpid,seq,msg_id,msg_type,`action`,from_user,to_user,external_user,room_id,msg_time,file_sdk_id,file_size,file_md5,file_url,transfer_file_status,create_time,update_time) VALUES ('{}','ww0af8bc32673add13','{}','{}' ,'image','send', '{}' , '{}' ,'{}' ,NULL,'{}' ,'CtYBMzA2OTAyMDEwMjA0NjIzMDYwMDIwMTAwMDIwNDNhOWYwODEwMDIwMzBmNGRmYjAyMDQyNjQxZTg3ODAyMDQ2ODQyNjMyZDA0MjQzMzYyMzE2MTM0NjQzNDM1MmQzOTMyNjYzMTJkMzQzNjMyNjEyZDM4NjM2MjMwMmQzNTYyMzMzMzMxMzkzNzY2NjE2MzYzMzYwMjAxMDAwMjAzMDUzMWYwMDQxMDM4MTVlZGVmMjRmMmEyNWY2ZTE0YjU4Y2JiYjc0M2NkMDIwMTAyMDIwMTAwMDQwMBI4TkRkZk1UWTRPRGcxTlRFek9EY3pNakEwT0Y4eE5UVXpNams1T1RnM1h6RTNORGt4T0RFeU16TT0aIGE4ZTE4NWJmOGQ2NDQ3MGU5YTczOTQ5MWJmNjU5MmRm',340462,'3815edef24f2a25f6e14b58cbbb743cd3815edef24f2a25f6e14b58cbbb743cd','https://hualala-common.oss-cn-shenzhen.aliyuncs.com/test/corporate-wechat-backend/6842c73145c657000140e748.png',2,NOW(),NOW())".format(brand_code, seq, msg_id, from_user, to_user, external_user_id, current_timestamp)
                else:
                    sql = "INSERT INTO `i61-bizcenter-corpwechat`.cw_chat_data (biz_code,corpid,seq,msg_id,msg_type,`action`,from_user,to_user,external_user,room_id,msg_time,content,transfer_file_status,create_time,update_time) VALUES ('{}','ww0af8bc32673add13','{}','{}' ,'text','send', '{}' , '{}' ,'{}' ,NULL,'{}' , '{}' ,2,NOW(),NOW())".format(brand_code, seq, msg_id, from_user, to_user, external_user_id, current_timestamp, content)

                sql_result1 = mysql_conn.execute(sql)
                print(sql_result1)
                seq += 1
                time.sleep(1)
                current_timestamp = int(time.time() * 1000)
                
            return True, f"成功插入 {len(data)} 条数据"

        except Exception as e:
            return False, f"插入失败: {str(e)}"

    # ==================== 课程相关操作 ====================

    def update_course_finished_status(self, choose_url, user_id, finished, finished_2=None):
        """更新课程完成状态（可将课程标记为已完成或未完成）"""
        try:
            mysql_conn = self._get_mysql_conn(choose_url, 'gubi')
            # 查询用户的体验课课程ID
            sql = """
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
                return False, "没有查询到学员的体验课数据"
            
            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(finished)
            
            # 内部函数：生成更新SQL
            def update_course(course_id, is_finished):
                if is_finished:
                    return f"UPDATE pjx.user_course SET course_status=15,comment_time='{now_time}' WHERE id='{course_id}';"
                return f"UPDATE pjx.user_course SET course_status=0,comment_time=NULL WHERE id='{course_id}';"
            
            # 更新第一节课状态
            mysql_conn.execute(update_course(sql_result1[0]["id"], int(finished) == 1))
            
            # 如果有第二节课且指定了状态，则更新第二节课
            if len(sql_result1) > 1 and finished_2 is not None:
                mysql_conn.execute(update_course(sql_result1[1]["id"], int(finished_2) == 1))
                
            return True, "更新成功"
        except Exception as e:
            return False, f"插入失败: {str(e)}"

    def update_go_pk_record(self, choose_url, user_id, win, lose):
        """更新围棋对弈记录（先删除旧记录，再插入新记录）"""
        try:
            mysql_conn = self._get_mysql_conn(choose_url, 'gubi')

            if user_id is not None and win is not None and lose is not None:
                # 先删除旧的对弈记录
                mysql_conn.execute(f'DELETE FROM pjx_go.t_go_play_pk_record where user_id ={user_id}')
                
                # 胜利记录SQL（result=1表示胜利）
                sql_win = "INSERT INTO pjx_go.t_go_play_pk_record VALUES(NULL, 2, {}, '2026-01-19 18:09:05', 1, '9路吃子', 1, 1, 'Ceslin', 46, 'test', 2, 2, 2, 0, 0, 1, 3, 5.5, 3, 0, 0, 1, NULL, 1, 1, 0, '白吃3子', 0, 3, 0, 0, 0.00, 0.00, 33, 16, '2025-12-04 14:56:11', '2026-01-19 18:09:05');".format(user_id)
                # 失败记录SQL（result=2表示失败）
                sql_lose = "INSERT INTO pjx_go.t_go_play_pk_record VALUES(NULL, 2, {}, '2026-01-19 18:09:05', 1, '9路吃子', 1, 1, 'Ceslin', 46, 'test', 2, 2, 2, 0, 0, 1, 3, 5.5, 3, 0, 0, 1, NULL, 2, 1, 0, '白吃3子', 0, 3, 0, 0, 0.00, 0.00, 33, 16, '2025-12-04 14:56:11', '2026-01-19 18:09:05');".format(user_id)
                
                # 批量插入胜利记录
                for i in range(int(win)):
                    mysql_conn.execute(sql_win)
                    print(f"插入第：{i+1}条数据")
                    
                # 批量插入失败记录
                for i in range(int(lose)):
                    mysql_conn.execute(sql_lose)
                    print(f"插入第：{i+1}条数据")
                    
                # 清除Redis缓存
                redis_key = f"i61-eos-copilot:cache:pjx:getUserPlayChessData{user_id}"
                self._delete_redis_key(choose_url, redis_key)
                
                return True, "对弈数据更新成功"
            else:
                return False, "对弈数据更新成功"
        except Exception as e:
            return False, f"插入失败: {str(e)}"

    def delete_review_record(self, choose_url, user_id):
        """删除复盘记录（包括提醒关系和关注标签）"""
        try:
            mysql_conn = self._get_mysql_conn(choose_url, 'gubi')

            if user_id is not None:
                # 删除提醒关系
                mysql_conn.execute(f'DELETE FROM pjx.help_util_user_remind_relation WHERE user_id={user_id};')

                # 查询并删除关注标签
                mysql_conn = self._get_mysql_conn(choose_url, 'liuyi')
                sql_select = """
                    SELECT c2.id,c1.user_id,c1.external_user_id FROM 
                      `i61-bizcenter-corpwechat`.cw_biz_external_user_relation AS c1
                    INNER JOIN `i61-bizcenter-corpwechat`.cw_external_user_follow AS c2
                    ON c1.user_id = c2.user_id AND c1.external_user_id = c2.external_user_id
                    WHERE c1.biz_user_id = {}
                    ORDER BY c1.id DESC;
                        """.format(user_id)

                sql_result1 = mysql_conn.fetchall(sql_select)
                if len(sql_result1) != 0:
                    follow_id = sql_result1[0]["id"]
                    print(follow_id)
                    mysql_conn.execute(f"DELETE FROM `i61-bizcenter-corpwechat`.cw_external_user_follow_tag WHERE follow_id={follow_id};")
                return True, "复盘数据清理成功"
            else:
                return False, "请输入用户id"
        except Exception as e:
            return False, f"更新失败: {str(e)}"

    def cancel_user_demo_lessons(self, choose_url, user_id):
        """取消用户所有demo课（批量取消）"""
        print(f"\n开始处理用户 {user_id} 的demo课...")

        # 获取所有demo课的st_id
        st_ids = self._fetch_st_ids(choose_url, user_id)
        print(st_ids)
        if not st_ids:
            print("没有找到可处理的demo课")
            return False, "没有找到可处理的demo课"

        print(f"获取到 {len(st_ids)} 个st_id: {st_ids}")

        # 逐个取消demo课
        results = []
        for st_id in st_ids:
            success = self._cancel_demo_lesson(choose_url, user_id, st_id)
            results.append(success)

        return True, "取消demo课成功"

    # ==================== 助力工具相关 ====================

    def delete_help_util_userinfo(self, choose_url, user_id):
        """删除助力工具用户信息（包括扩展信息和关系表）"""
        try:
            mysql_conn = self._get_mysql_conn(choose_url, 'gubi')

            if user_id is not None:
                # 删除扩展信息
                mysql_conn.execute(f'DELETE FROM pjx.user_enterprise_extend_info WHERE user_id={user_id};')
                # 删除关系表数据
                mysql_conn.execute(f'DELETE FROM pjx.user_enterprise_extend_info_relation WHERE user_id={user_id};')
                # 清除Redis缓存
                redis_key = f"i61-eos-copilot:cache:pjxCache:userExInfo:{user_id}"
                self._delete_redis_key(choose_url, redis_key)
                
                return True, "删除助力工具用户信息成功"
            else:
                return False, "请输入用户id"
        except Exception as e:
            return False, f"更新失败: {str(e)}"

    # ==================== 学情数据相关 ====================

    def clear_learning_situation_data(self, choose_url, student_id, node_types):
        """清理学习情况数据（软删除，标记为已删除）"""
        mysql_conn = self._get_mysql_conn(choose_url, 'ob')
        
        try:
            # 解析节点类型（支持逗号分隔的多个类型）
            if isinstance(node_types, str):
                node_type_list = node_types.split(',')
            else:
                node_type_list = [str(node_types)]
            
            results = []
            success_count = 0
            
            for node_type in node_type_list:
                node_type = node_type.strip()
                if not node_type:
                    continue
                    
                # 查询学习情况数据
                query = "SELECT * FROM `i61-eos-ai-advisor`.learning_situation_student WHERE student_id = %s AND node_type = %s AND is_deleted = 0"
                result = mysql_conn.fetchone(query, (student_id, node_type))
                
                if result:
                    intervention_task_id = result.get('intervention_task_id', 0)
                    
                    # 软删除学习情况数据
                    update_query = "UPDATE `i61-eos-ai-advisor`.learning_situation_student SET is_deleted = 1 WHERE student_id = %s AND node_type = %s"
                    mysql_conn.execute(update_query, (student_id, node_type))
                    print(f"已标记学习情况数据为已删除，student_id: {student_id}, node_type: {node_type}")
                    
                    # 如果有关联的干预任务，也进行软删除
                    if intervention_task_id != 0:
                        update_intervention_query = "UPDATE `i61-eos-ai-advisor`.learning_situation_intervention_task SET is_deleted = 1 WHERE id = %s"
                        mysql_conn.execute(update_intervention_query, (intervention_task_id,))
                        print(f"已标记干预任务数据为已删除，intervention_task_id: {intervention_task_id}")
                    
                    results.append(f"节点类型{node_type}: 操作成功")
                    success_count += 1
                else:
                    print(f"未找到学习情况数据，student_id: {student_id}, node_type: {node_type}")
                    results.append(f"节点类型{node_type}: 未找到学习情况数据")
            
            if success_count > 0:
                return True, f"成功清理{success_count}个节点类型，详细信息：{'; '.join(results)}"
            else:
                return False, f"所有节点类型均未找到数据。详细信息：{'; '.join(results)}"
                
        except Exception as e:
            print(f"操作失败: {str(e)}")
            return False, f"操作失败: {str(e)}"
        finally:
            del mysql_conn

    # ==================== 直播课数据相关 ====================

    def insert_dm_edu_com_lrn_user_live_f(self, user_id, user_unification_id, rank_asc,
                                          is_delete=None, is_update=None,
                                          user_name=None, brand_code=None, lp_id=None, lp_name=None,
                                          teacher_id=None, teacher_name=None, cate_sid=None, cate_stage=None,
                                          is_attend=None, is_late=None, is_prepare=None, frontal_face_rate=None,
                                          is_homework_submit=None, is_homework_correct=None, is_quick_answer=None,
                                          quick_answer_cnt=None, smile_rate=None, completion_rate=None,
                                          question_unlock_cnt=None, course_evaluate_score=None,
                                          first_answer_true_rate=None, homework_true_rate=None, is_exit=None,
                                          asr_content=None, knowledge_point=None):
        """
        向dm_edu_com_lrn_user_live_f表插入/更新/删除直播课数据
        支持批量操作：多个rank_asc用逗号分隔
        支持删除模式：is_delete=1时执行删除
        支持更新模式：is_update=1时执行更新（只更新传入的非空字段）
        :param user_id: 用户ID
        :param user_unification_id: 用户统一ID
        :param rank_asc: 排名（支持多个，用逗号分隔）
        :param is_delete: 是否执行删除操作
        :param is_update: 是否执行更新操作
        :return: (成功状态, 消息)
        """
        try:
            mysql_conn = mysqlMain('MySQL-wd-dw')
            
            # 解析rank_asc列表
            rank_asc_list = [r.strip() for r in str(rank_asc).split(',') if r.strip()]
            
            # 删除模式：根据user_id、user_unification_id和rank_asc删除数据
            if is_delete:
                placeholders = ','.join(['%s'] * len(rank_asc_list))
                delete_sql = f"""
                    DELETE FROM dm_edu_com_lrn_user_live_f 
                    WHERE user_id = %s AND user_unification_id = %s AND rank_asc IN ({placeholders})
                """
                row_count = mysql_conn.execute(delete_sql, (user_id, user_unification_id, *rank_asc_list))
                del mysql_conn
                return True, f"成功删除{row_count}条数据"
            
            # 更新模式：根据user_id、user_unification_id和rank_asc更新数据
            if is_update:
                update_fields = []
                update_params = []
                
                # 构建更新字段（只更新传入的非空字段）
                field_mapping = {
                    'user_name': user_name,
                    'brand_code': brand_code,
                    'lp_id': lp_id,
                    'lp_name': lp_name,
                    'teacher_id': teacher_id,
                    'teacher_name': teacher_name,
                    'cate_sid': cate_sid,
                    'cate_stage': cate_stage,
                    'is_attend': is_attend,
                    'is_late': is_late,
                    'is_prepare': is_prepare,
                    'frontal_face_rate': frontal_face_rate,
                    'is_homework_submit': is_homework_submit,
                    'is_homework_correct': is_homework_correct,
                    'is_quick_answer': is_quick_answer,
                    'quick_answer_cnt': quick_answer_cnt,
                    'smile_rate': smile_rate,
                    'completion_rate': completion_rate,
                    'question_unlock_cnt': question_unlock_cnt,
                    'course_evaluate_score': course_evaluate_score,
                    'first_answer_true_rate': first_answer_true_rate,
                    'homework_true_rate': homework_true_rate,
                    'is_exit': is_exit,
                    'asr_content': asr_content,
                    'knowledge_point': knowledge_point
                }
                
                for field, value in field_mapping.items():
                    if value is not None and value != '':
                        update_fields.append(f"{field} = %s")
                        update_params.append(value)
                
                if not update_fields:
                    del mysql_conn
                    return False, "没有需要更新的字段"
                
                # 添加更新时间
                update_fields.append("etl_time = NOW()")
                
                success_count = 0
                results = []
                
                for single_rank_asc in rank_asc_list:
                    # 检查数据是否存在
                    check_sql = """
                        SELECT rank_asc FROM dm_edu_com_lrn_user_live_f 
                        WHERE user_id = %s AND user_unification_id = %s AND rank_asc = %s
                    """
                    existing = mysql_conn.fetchone(check_sql, (user_id, user_unification_id, single_rank_asc))
                    
                    if not existing:
                        results.append(f"rank_asc={single_rank_asc}: 数据不存在，跳过")
                        continue
                    
                    # 执行更新
                    update_sql = f"""
                        UPDATE dm_edu_com_lrn_user_live_f 
                        SET {', '.join(update_fields)}
                        WHERE user_id = %s AND user_unification_id = %s AND rank_asc = %s
                    """
                    params = update_params + [user_id, user_unification_id, single_rank_asc]
                    mysql_conn.execute(update_sql, params)
                    success_count += 1
                    results.append(f"rank_asc={single_rank_asc}: 更新成功")
                    print(f"成功更新数据: user_id={user_id}, user_unification_id={user_unification_id}, rank_asc={single_rank_asc}")
                
                del mysql_conn
                return True, f"更新完成: 成功{success_count}条, 详情: {'; '.join(results)}"
            
            # 插入模式：先检查已存在的rank_asc，避免重复插入
            placeholders = ','.join(['%s'] * len(rank_asc_list))
            check_sql = f"""
                SELECT rank_asc FROM dm_edu_com_lrn_user_live_f 
                WHERE user_id = %s AND user_unification_id = %s AND rank_asc IN ({placeholders})
            """
            existing_ranks = mysql_conn.fetchall(check_sql, (user_id, user_unification_id, *rank_asc_list))
            existing_rank_set = {str(r['rank_asc']) for r in existing_ranks} if existing_ranks else set()
            
            # 随机数据样本（用于未指定字段时生成默认值）
            teacher_names = ['孙林可']
            lp_names = ['谭新贵']
            stages = ['S6']
            knowledge_points = [
'''1. 理解数方游戏中数字的含义，掌握基本的游戏规则；
2. 通过数方中的数字寻找突破口，进一步进行观察推理，熟练掌握解决数方游戏的技巧；
3. 在解决数方游戏的过程中，充分培养学生的理解、推理和分析能力。
4. 一个数字分一份，切成长方或正方，先从大数开始找。''', 
'''1. 先数单个的，再数组合的
2. 正方形计数：点数图形中正方形的数量
3. 包含物品的正方形计数：其中一个正方形中有图片，求包含图片的正方形数量
4. 复杂正方形计数：正方形里外包含，点数较为复杂的图中正方形的数量''', 
'''1. 求余数时，可先看除数对应的整除特征，再用特征部分直接计算余数。小口诀:看除数，想特征，抓关键，去求余
2. 整除规律对于判断余数同样适用
3. 余数的可加性：和的余数=余数的和(若≥除数,再取余)
4. 余数的可减性：差的余数=余数的差(若不够减,先加除数再减)
5. 余数的可乘性：积的余数 = 余数的积（再取余）''', 
'''1. 找一找，找到图形代表的数字（先找单独的零件）
2. 拼一拼，外层在左，内层在右
3. 找一找，找到图形代表的数字（没有单独找重复）
4. 写数字，外层在左，内层在右
5. 找一找，找到图形代表的数字（没有单独找重复）
6. 写数字，内外层要分清
7. 找一找，找到图形代表的数字（先找单独的零件,没有单独找重复）
8. 写数字，内外层要分清''',
'''1. 读数量，有妙招，瞄准头顶向左瞧。比多少，更简单，看看谁的个子高！
2. 对准左边找数字，数字是几就涂到几，读出量，做减法，算得又快又对啦！
3. 一读已知数，二想减法和算式，三算结果补图表。记住“总数减部分，等于另一部分”！''', 
'''1. 方法小结：一堵、二隔、三补齐。先解决能直接确定的棋子。
2. 总结技巧：
    - 同色隔三格，外部邻格为异色，注意行列不重复
    - 同色隔四格，内部邻格为异色''']            
            
            asr_contents = ['好，做好上课准备哦。好，还是蛮准时的呀。对，那大家做做准备。呃，新来的宝贝可以先做神秘任务啊。嗯你先玩玩这个游戏，我去喊一下没到的朋友啊。好，你们需要自己把这个喇叭点开，把左上角的喇叭点开，听听要求啊。来。点开左上角的喇叭，听听要求。.哇。哦，是拼好这个机器人是吧？嗯，缺什么咱们就给他什么啊，他左右两边得长得一样，对不对？嗯.再找找眼睛得长得一样，手跟脚身体都要长，左边右边都要长得一样哦。对他的脚上是一颗是一颗星星，是不是？但是要开开心心。哦，最后按红色按钮修复它好，太厉害了。好，收回啊，先给大家送欣星奖励啊，来检查一下嗯课前预习都完成了，没问题。然后就是大家的作业。好，我先把预习欣欣送一下，再把作业星欣送一下啊。然后我再说一下满分的小朋友啊。好，卢卡，还有小昭是满分啊。对。那我就给卢卡多5颗星星奖励，小张还没有来，那我们现在出发喽，好不好？来该着我出对，看还有小昭，你们是有错题的啊。对，看有两个错题，就是第三题还有第六题对，第三题，第六题啊。好，再仔细一丢丢吧。来，我们出发喽。 . .嗯，我们来看看这个牛奶杯它有哪两种颜色呀，看到了吗？嗯，白色和红色对，而且白色在上方，红色在下方是不是非常棒啊？然后这个杯子它还有一个小把手，这个小把手在哪边呀？你能告诉老师好。好而不统一吗？好，太掉线喽。好，来，宝贝们告诉老师啊，这个小把手是在左边还是右边？左边非常好啊。对，如果你要是忘记了，你就注意哦。小喇叭的这边是左边对不对？小喇叭的这边是左边啊。好，行，所以我们知道这个小把小把手是左边。好，老师把镜子放上去啊。把镜子放上去嗯。是因为小星星吗？那你不觉得更有挑战性吗？宝贝嗯，等一下你在上课的过程中还能挣更多的星星，你还能反超，是不是很有趣？好，快来帮我看看啊。来，那我们看镜中的这个杯子。它是什么颜色在上，什么颜色在下。，来一个一个说，这次请卢卡上台来说什么颜色在上，什么颜色在下。好，那原来的杯子也是。好，谢谢你。所以我们发现这个杯子的上下没有发生改变，对不对？上下是不变的啊。好，但是你看一看好，谢谢卢卡。但是咱们看看这个小把手。小把手的方向是不是换了位置呀？小把手本来在左边，现在跑到哪边去了？嗯，对，现在跑到右边去了啊，特别棒。好来。那小张，你来总结总结。你来总结总结好不好？你来看看这个小杯子啊，就是它在镜中的样子，跟原来的样子是什么不变呀？上下嗯。그.哦，所以就很清晰，就是它的左右会改变，是不是好，很好啊，谢谢你来，接下来我再拿这个镜子看一看啊，它的把手本来在左边，现在跑到哪边去了呀？嗯。右边对，所以你们特别棒啊，你们就知道了，它在镜子中左右会变，上下不变，好不好？就是左右会发生变化啊。好，没问题哦，两个都要放，好不好？两个都放就成功了啊。嗯，你看。行，那接下来下面的挑战交给你们来完成了，好不好？好，来快快来好好尝试一下啊，小赵也快好好尝试一下哈来。嗯哦，没有哪个杯子是他在镜中的样子呀？对，哪个杯子呀？把手的左右会变太棒了，把手的左右会变哦。本来把手朝右。.嗨赶紧来解决问题了啊，我要准备送星星哦，我要准备给你补上星星哦。你看本来他的把手朝向右边，对不对？那你现在就应该小张，你现在就应该找把手朝左边的啊。一号、2号、3号、4号、几号杯子的把手朝向左边。3号对，而且它的上下没有改变，所以3号就是咱们要找的杯子哦。对，非常棒。来继续。那认真观察，看看这个香蕉的小香蕉的这个板儿好吧，好吧，这个把手啊是朝向哪边啊。对，来。..行，那接下来再来一个哦再来一个哦呃，看看咪咪猫的蝴蝶结朝向哪边呀，咱们就每次找一个特征，好不好？找一个特征来解决问题啊，看看蝴蝶结朝向哪边。그.是的呀，因为你找到它的影子了，对你找到它在镜中的样子了。咪咪猫的蝴蝶结本来在左边，现在应该。嗯，本来在右边，那就要换到哪边。对，你自己好好想一想哦。好，小小张有什么提示呀？嗯，对呀，所以他是不会倒立的啊，他在竞争的样子是不会倒立的。这么厉害，注意安全哦。好。好，小张，你刚刚来迟了一会儿啊，我再给你介绍一下好不好？你认真看，你看咪咪猫的蝴蝶结现在是在左边还是在右边？在左边对，那它在镜中的蝴蝶结就应该跑到右边去了啊，为啥呢？因为照镜子的时候，左右会反过来。那你来看一看啊。一号、2号两个迷咪猫，哪个迷咪猫的蝴蝶结在右边呀？2号对呀，所以我们就找到正确的咪咪猫了呀，对不对？下面两个咪咪猫不用看了，因为咪咪猫照镜子的时候，它是不会倒立的对吧？它镜中的样子是不会倒立的，是不是这生活常识嘛，是吧？来，那最后我们就找到它的影子了啊？好，这就很清晰，左右会变，上下不变。好，大家来领一次星星好不好？.好，行，没问题。那接下来咱们就继续出发喽。呃，嗨小朋友，你能不能快点过来，可不可以快点过来加入我们第二关。遇到什么问题啦，那我们出发喽。.嗯，好的，那我们赶紧找一找吧。그.好，说了，咱们要找对称呀，就得找特点啊，找特征。那你观察观察这个房子有什么特点。对，都可以。我举个例子，好不好？举个例子啦，我发现这个房子的左下角有一个冰块。我发现这个房子的左下角有一个冰块，你有发现什么特点呢？你有什么特点？好，小张，你发现了什么特点？哦，谢谢你啊，很好，小昭就告诉朋友们啦，冰块的它跟镜子中的样子左右会反过来，对不对？所以冰块应该在房子的最右边。好，谢谢小昭啊。来，那我们来看看。好，3号房子啊，宝贝，我来标上序号，一号、2号、3号、几号房子的冰块是在右边。그.是不是3号房子的冰块在右边呀，是不是？所以咱们就找到这个对称的房子了。对，就是镜中左右对称的房子啊。好行，这样就找到了？对，因为我们知道镜子里的物品左右会反过来嘛，是不是好行，那我刚刚找的是冰块，你换一个好不好？你不能跟老师。그.对，镜面对称就是左右反过来。好，那你不能找跟我一样的特征哦。我刚刚找了冰块，你还可以找什么？好，小张又提示，你找什么宝贝。找木桶哦，好，你说嗯。哦，行，谢谢你，非常好，是不是就超清晰了啊。那我们再看看呃，那只有一号房子和3号房子的木桶在左边，对不对？然后咱们再结合冰块来考虑就可以了啊，所以最后是不是还是三号房子符合条件呀，是吧？你看这个木桶在左边好，卢卡，你也找一个啊，刚刚呃有找冰。块的有找木桶的，你也找一个宝贝，你找什么？嗯嗯，红色的是是这里吗？是这里哦，可以可以，好，有一个红色的装饰，对吧？它本来是在哪个位置呀？那现在镜子中就跑到哪里了呀？그.跑到右边去了。对的，没问题啊，谢谢卢卡，非常好，就是这样的。所以我们重点就是找特征啊，把这些特征结合起来就可以了，好不好？好来按，镜面对称一定是怎么样，左右怎么样呀，左右会怎么样。反过来对，左面对称呃，左右对称左右反过来，但是上下不变好不好？好，行，小张还想给提示，来，你说吧，还有什么提示？그.哦，可以可以，没问题，非常好。对，那咱们还可以结合多个特征一起来看，对不对？然后找到符合条件的那一个啊，所有的特点一起观察。好，既然这么会找的话，现在自己来的喽。嗯，来你开始挑战。点喇叭点喇叭。车头朝哪边，车的尾巴朝哪边嗯。味道做的挺好啊，再来再来。好好观察哟，嗯，好多好多好多好多特点啊，所以你要好几个特点都满足，好不好？来啊。刚刚那个做的太快了，我就说吧，小张，你太着急了。小昭，你也是你太着急了。嗯，那这样吧，因为你们很着急，你们每次只满足一个特点就选了啊。那接下来一人找一个特点好不好？看看哪幅图全部都满足啊。好，这次卢卡最先来好不好？你来找你来找一个特点，你看哪里。妻子。哦，非常好，谢谢卢卡啊。第一个条件哈，棋子朝右，所以我们现在要找的是棋子朝左的。对，这两个都是朝左。好，小张掉线了。小张小张也是认真看，所以你看你们这个时候就有点着急了，对吧？棋子朝左的有两个呀，如果你直接选的话，是不是就出错了呀，对不对？所以可不可以耐心一点，再继续找第二个特点呢？对不对？只有中间这个不合适嘛，但是一和三都还可以呀，是吧？小张。是不是？所以不要太着急，你看有两个还是符合的呀。再来那小张，你再来找一个特点吧。你再来找一个特点吧，是嗯可以看颜色。看这个蓝色的外墙好不好？这个蓝色的墙朝哪边，那就是右边，对不对？那近。所以镜子中就朝哪边呀？咦，那竞中就朝左边呀，对不对？所以就反过来呀。好，所以你现在告诉我哪一幅图才是正确的，123哪幅图才是正确的呀嗯。对呀，这幅图是哪幅图呢？是一号、2号、3号哪幅是正确的呀？一号、2号、3号、几号一号是正确的是吧？好，谢谢你。你在台上呀，你在台上还有什么提示吗？.好可以的啊，太巧了。好，小张，现在到你了啊，我再请一位宝贝告诉我。好，那接下来你再看一个特点好不好？再看一个特点，要不你就看这个很大的城墙吧，这个很大的城墙是靠左边还是靠右边呀？所以他在晋中就应该靠哪边嗯。靠右边，所以是不是还是一号呀？好，谢谢你哦。对，所以宝贝们注意啊，要每。2号不行呀，宝贝2号棋子已经被我们排除了呀，他棋子就已经不对了呀。我们在一开始就已经去掉了，好不好？好，行，耐心。小昭，什么问题？对呀，就是要旗子反过来呀，就是要不一样呀。你自己看看棋子本来朝右在镜中就要朝左，这个蓝色的墙朝右在镜中就要朝左，就是要反过来才对呀。好，对，继续找啊继续找。对，好好观察，好好观察一下。为什么要这样呀？你这样做题可不行。我收回了做不到吗做不到吗？那我收回了。好，来，那你现在就一个一个的找特征啊，一个一个找特征，把你找到符合特征的打圈圈。对，就是你觉得跟竞争应该是对的，你就把哪个打圈圈。不对的，你就打叉叉，一个一个找先找叉子。先找叉子，不要这样去解决问题，这样不好。先找叉子，look卡我看看你的好。Okay.对，叉子本来朝右，我们要找的就是朝左小昭，我不是要找跟他一模一样的图，我要找的是镜子中的样子，所以左右要反过来，我们今天一节课都是在做这个事情。不是要跟他找长得一模一样的东西，是要找左右反过来的。对，叉子本来朝右，我们现在要找朝哪里呀？嗯，对，那你就找到朝左的，把它圈出来。对，哪个是朝左呀？对要找朝左的啊。嗯，然后你还要看看叉子是插在什么东西上面呀，你就找到正确的，你就找到一个正确的图了啊。그.它是插在西红柿和草莓的上面，是不是？对，那不可能换到换到橙子的上面呀。.好，最后做选择，大家要记住我们今天的学习目标哦，我们今天要找的是镜子里面的东西，我们不是要找跟它长得一模一样的东西啊。对，好，做选择。好，我看卢卡小张，对你要思考之后再做决定啊。好，行。来下一次红包雨哦，等一下继续。.好，行，那接下来咱们要继续前进喽。. .好，行，好好观察。对，今天找的就是他们在镜中的样子啊。好，最后最后我会先我再带你复习一下啊，你一定要看你看。你看这个杯子在镜中的样子，你看它的把手本来是在左边，在镜中就跑到哪里去了？右边对，所以咱们都知道啊，就是在镜中的样子是会左右跟原来的这个图左右反过来的，对不对？左右会相反的啊。对，我们是要找这样的图。好，那接下来我们继续看好，四个小朋友就是很明显的特征啦，对不对？好，那接下来老师要问问你啊。好，麋鹿爷爷站在。在最哪边左边还是右边，他站在最右边。哦，那告诉你怎么分左右啊，宝贝靠这个喇叭就是左靠这个灯泡就是右啊，它朝向喇叭，它就是左边，它朝向灯泡，它就是右边，好不好？所以这个麋鹿爷爷是朝向右边，对不对？好，所以他在镜中就应该站在哪边，它在镜子里面就应该站向哪边，。朝向哪边呀？那就要反过来，那就应该跑到最左边去啊。好，那接下来你来看图好不好？一号、2号、3号、4号。几号图这个麋鹿爷爷站在最左边，直接告诉我就好。几号。一号对，一号是站在最左边的，对不对？而且呢他的对你看他的脸是朝向左边，是不是你看啊他的这个麋鹿爷爷的脸是朝右边，然后这个一号麋鹿爷爷的脸朝最左边是不是？所以其实我们直接就定位了啊，直接就找到他了，好不好？好，行，当然了。咱们可以再慢一点点，因为我们还看看其他的条件符不符合。好，那你告诉老师皮皮虎站在哪边，皮皮虎站在哪边？皮皮虎站在灯泡，就是。灯泡就是右喇叭就是左喇叭就是左。你看皮皮虎都站在最左边，它的尾巴也朝向最左边，是不是？那说明我们要找一个怎样的皮皮虎呀？卢卡嗯。皮皮虎站在最左边，他的尾巴也朝向最左边，那说明咱们要找一个怎样的皮皮虎。好，找尾巴朝右的皮皮虎还是站在最右边的皮皮虎，那几号符合呀？一号、2号、3号、4号、几号符合呀？可是2号的皮皮虎是站在最右边吗？他的尾巴虽然朝右了，但是他有没有站在最右边呢？所以2号不行，4号不行，他们是站在左最左边的，不是站在最右边的。所以几号符合。一号对它的尾巴计朝向右边，它也是站在最右边的，所以才符合啊。然后我们就会选择一号。对，好，谢谢你。那大家看的时候不能只看一个人好不好？不能只看麋鹿爷爷啊，你还要把所有的小朋友也跟着看一看，好不好？好行，那我们再来观察观察啊，你来看看咪咪猫是站。在中间的位置吧，是不是咪咪猫的脸朝向哪边呀？咪咪猫的眼睛看着哪边，小昭咪咪猫的眼睛看向哪边。嗯，灯这个喇叭是哪边？喇叭是左边。好，那你看那镜中他的眼睛就看向。右边对呀，好，谢谢你哦。对，没关系，你就算左右有点分不清楚也没关系，你是不是有两只手呀，对不对？你看咪咪猫的原图，如果是往这边伸，那劲中就往这边伸，对不对？你的两只手你可以这样，对不对？一只手往这边伸，那另在镜中就要往另外一边伸啊，你可以伸直你的手来解决问题，好不好？好，也是可以的啊，没关系。好。行，但是你们必须要认真的观察啊，把每个小朋友都看好好不好？那这次我建议你来观察大力熊，还有河马校长，好不好？对，观察大力熊，还有河马校长的拐棍吧，好不好？对你你观察观察啊，想好了，我再给你解锁啊。我没有解锁哟，你先看你先看看啊。.嗯嗯，是的呀。对对你可以选两个人一起看都看看啊。你看看大力熊的位置。我还没解锁呢我还没解锁呢，看看大力熊的位置哈。.对，好，如果觉得有一点点复杂，那咱们就只看大力熊的位置吧，好不好？好，就只看大力熊哦，只看大力熊哦来。就选择喽。 要大难度喽，先把两个小朋友的位置放对吧。看小张小张，你就只看大力熊吧，你看大力熊他站在哪里，上面的大力熊，他站在最左边还是最右边？他站在哪边，你就把你哪只手伸直。哦，这只手是吧？很好，没关系，对他站在哪一边，你就把你哪只手伸直很好，太棒了。那在镜子里面，它就应该在你另外一只手的那边，你现在把你另外一只手伸直。找找看，你把你另外一只手伸直，找找看，看看他站在哪边，看看哪一幅图，它的位置是正确的。只看这个熊嗯，对，就反过来反过来。look卡好，没问题，小张给我什么提示？嗯，嗯，我在呢，你给我什么提示？그.呃，有可能是送给你的哟。好，我收回了，我收回了啊。不错的。来对，就是找小朋友们的站位嘛。你看大力熊站在最左边最靠边边的位置，是吧？那你肯定要找一个最靠边边的位置。对不对？所以就是最右边啊，好，好好看看。来，接下来咱们要继续前进喽，走吧。 .好，行，太有趣了。下节课跟着他们继续闯关啊，来把今天的内容好好看一看来。.嗯，我。但是小张放视频的时候，我不能跟你说话，放完才能跟你说。..嗯，那今天下课之后要跟爸爸妈妈分享你学到的内容，好不好？好来。最后最后我再我再给你们一个挑战题，让你们好好的尝试一下啊。来来。그.对，就是每一个物品它的位置左右哎会换，对不对？好，左右是对称的啊。好，来，比如我举个例子吧，比如这几本书，它本来是在架子上最左边的位置。那在镜中它就会跑到最右边的位置，就这个意思。好，你来试试吧，把这三个物品拉上去啊。嗯，我在呢，小张，你说吧哦，快去快去，快点。对宝贝们要上洗手间的话，就自己赶紧跑啊，你可以先去去了再回来，好不好？对。嗯，就是你看看啊，书如果在最左边的话，在镜子里它就会跑到最右边去。然后咱们再来看笔筒。对，好，那你看看那个书的位置，对不对？不用放不用放四个东西哦，放三个就行了啊。。嗯，对，卢卡，你看你看这个小车车，它在最左边还是在最右边呀？所以你在镜子中就要把它放到最最左边呀。对，所以你要把它放到最左边呀。你刚刚只是放到放错位置了。放到最左边的位置去。嗯，但是你看看这个车头也是朝向最左边的，是不是车头也要换一换哎了，好不错啊。그.是不是好，行，我收回啦我收回啦。对，所以你看看你们今天学的所有的内容就是在这里最关键啊，就是在这里你得知道一个物体跟它镜子中左右是反过来的。但是上下不会变。对，就是我们一直都是在用这个规律解决问题啊。好，行好。下课之后，你可以照照镜子自己去看看好不好？好，行，来，最后老师给大家把星星奖励送一下啊。好，星星奖励补上。对，好。补一点点好来，那大家好好的完成任务好不好？好好认真的做作业啊。对，好来把你们请上台，在小房子这里合影好不好？在小房子这里合影。好，可以啊，行，自己摆个可爱的姿势吧。小张上洗手间去了。对，你们上课以后想上洗手间的话，举一下手就可以直接去了，好不好？嗯，来。32开赶紧过来，宝贝，你过来嘛，一摆好，321好，再拍到你喽。嗯嗯，look卡，你刚刚说啥呢？假拍照没有真的拍照。你你上节课有没有收到你的照片？没有你让妈妈在群里给你看看，我给你拍了一张特别帅的照片，好不好？真的拍照。你让妈妈给你看。对，然后小昭我也拍了很帅的照片啊。好，好好完成任务哈，好好去完成任务，咱们下次见吧，拜拜嗯，拜去，下次见啊。拜e by.', 
                           '哦，这个好看哪些小伙伴没来啊，晨晨是哦时间调整喽。然后我看看小张小明看，还有洋洋来了，小昭没来，是不是好？来，我去我去喊一喊嗯，怎么啦？晨晨，他时间不合适，调整时间喽。小小昭好，然后开今天请假喽，开今天请假喽。对，然后还有什么要问的，跟上课无关的问题，一次问完啊，等一下只解决上课相关的事情了。好，来，那我检查一下大家的预习哈。好，首先预习全部完成，没问题。然后就是大家的作业。上一节课的作业就是。说一下。好，完成了完成了。但是博轩是满分，洋洋是满分。但是小昭呢小明的错题比较多，小昭小明错的很多啊，小昭还好，小张是一个错题。对，行。小明上节课出错挺多的呀，小明嗯。你你上你现在上课，你要多跟老师一起分析问题了，你要多发言。你上节课出错很多最多的一次了。好吧，来预习的星星作业的星星，然后就是洋洋和博轩送满分奖励，小张小明的作业要做的更准确一点，好不好？对，如果课特别难，就像上节课一样，你觉得很难的，有难度的那你下课之后。可以让爸爸妈妈陪你做，爸爸妈妈帮你读题，你自己来做可以吗？好，那我们现在出发喽，来你。这就是爱G灯塔这个灯塔怎么暗暗的呀是。.好，行，那我们一起来看一看，请你移动一根火柴棒，将数字3。嗯，移动一根火柴棒，让它变成其他的数字。谁想试试呀嗯。好，行，小招小试试可以的。小明说声音有一点小喇叭的声音是吧？好，我这音量拉大，你那里也调大啊，把设置的音量调大，到时候让妈妈帮你调。好，小张，你来试一试，来，你来动手试一下。好来好，只能动一根火柴棒，那这一次不可以，因为这不是我们熟悉的数字。这不是数字，好，变回去，右边有个小圈圈。这也不是对，右边有个小圈圈，小招来点好，你自己拖回去也可以再来动，再来试试，再变。好。对，暂时还是不是哦，不是是吗？对你要九下面要有个弯弯嘛，不是好来，那没有关系。小昭，这个不是这个你刚刚已经试过了。小昭对，所以老师给一点提示，就是当你觉得你没有思路的时候，你就从一开始想一想，可不可以？3、我能不能通过动一根火柴棒把它变成一。小昭可不可以。那要不要试试2一不可以的话，要不要试试2，看看动动火柴棒怎么把它变成22是长什么样子的？二和三很接近，对不对？二和三很像二像一个小鸭子。二像一个小鸭子，想想看怎么去动它。对，那我们来想一想有没有什么好的提示，好不好？来，那点亮上面的，我把这个灯泡给点开了，然后你的眼睛看看到没有？这是6，哎，这是六根拼成了一个0，然后123456789这些数发现了吧？来。Yes.这个是火柴棒的根数。对，就是咱们是拿几根火柴棒拼成功的啊，拼成功的。好，对，这个没关系，我们先来想一想，呃，我我的重点是带你看这个上面的你先不看了，好不好？上面的根数先不要看老师的重点是先带你看下面数字长什么样，看到了没有？012345。56789长什么样，你看到了没有？看清楚了没有？看清楚了。好，行，来，那可以把三变成2。对，老师提示可以把三改成2，谁想试着移一移来。那小明来试一试，把三变成2吧，来看到了没有？对不对？好，谢谢小明。对，首先你就要认清楚这些数字的长相。好，然后咱们继续看，然后咱们来继续来看哈。好，为什么三能很快的变成2呢？因为三和二用的火柴棒根数是一样的对，因为三和二用的是一样数量的。火柴棒看向这里哦。三和二都是用5根火柴棒拼成的，看到了吗？还有一个五也是用5根火柴棒拼成的，看到没有？2。先听老师分享，等一下我会给你挑战的。先跟老师一起学习。我们来看一看有没有发现235，你能把老师的话听进去吗？那么先学再做来看一看有没有发觉235用的是同样多的火柴棒呀，对吧？所以你看到三的时候，对。你在下面说啥呢？所以你看到三的时候，你就要想我可不可以把它改成二呢，对不对？我可不可以把它改成5呢？这就是你的想法呀，对吧？然后还有哦还有几和几是同样多的火柴棒呀，快找找看。我轩在又很放松了啊。好，你。还有呢6069看到了没有？069是一样多的火柴棒，对，他们都是6根火柴棒。对，所以069也许可以互相改一改，好不好？那我们就简单的记一下2。Yeah。35069对，235可以互相改，可以尝试着改一改。069可以尝试着改一改，好不好？好，对，这就是一些小技巧。好，那。对，那你就尽量去尝试移动火柴棒，把它变成一个其他的数字哦。再说一遍235，然后呢，还有哪三个数博轩？哪三个数069对，他们是一样多的火柴棒啊。好，来，那接下来我们来试一试吧。0唉可以改成什么呀？快试试吧。对，然后再尝试啊。宝贝235互相改。没寄东西呀。235069看到零的话，想办法把它变成6，或者把它变成9。这个不是数字博削。你放的根本就不是数字，这个现在才是6。好，那跟我再来认认数吧，好不好？这个是零，这是一看清楚。我拿红笔画写给你看，这是一小明认真学，这是然后我把235放在一起，这是2看到了吗？然后呢。3然后呢。5对，一和4放在上面吧，235，然后还有0，这是0，对不对？这是6。H.069还有1个78对不对？1478对你要认这些数长什么样，235互相改069互相改，然后再来个1478，那就是其他的情况了，好不好？要认数哦。再来小昭小昭，还有挑战，5可以变成什么呀？哪五和哪两个数是互相变的呀？069才是互相变的吧，五和什么互相变？小张，你记了吗？洋洋，你记了吗？洋洋好来。那这次谁能一次给成五颗星，我看谁能一次把它找出来。对，那你听题目，你看看题目变了没有。对对你看看题目变了没有？ 小明，你听喇叭了吗？小明小张小张，你开始了吗？小张小明听喇叭了吗？你再听一遍。我觉得你。请你增加一根面包。请你增加一根面包，让数字五变成其他数字吧。对。看到没有？235互相变，然后呢，这个题让咱们增加面包，增加面包来变数字。好，再来好，这次题目又变了，请你点击减少一根香肠，把数字八变成其他数字，请你点击减少一根香肠。对，可以呀，有很多种可能，快去试试吧嗯。好，这次不错，这次都可以送星星奖励，好不好？对，好，所以你看咱们第一关学的什么，我们可以235068互相变，对吧？我们还学会了加火柴棒减火柴棒来发生改变，是不是呀？宝贝好，来，那接下来我们继续出发了哈？来。..好，来，那请你增加一根电线，使等式成立吧，增加一根电线啊，使等式成立。好，电线在这里哦，电线在这里，嗯，那我们先来算一算好不好？4加5等于几啊？小明洋洋，4加5等于几啊，报给老师。可以可以计算还蛮好的，4加5等于9。对，那三可以改成9吗？加一根电线可以改成9吗？可不可以？可以，谁想试来举手谁想试。行，这次小昭两只手都举了。行，我请你来试试吧，好不好？来把。对，加一根电线，让它成立。嗯，我们看看嗯。确实哈4加5等于9，确实没问题。行，谢谢你。来，那接下来咱们继续请你增加一根电线，十等式成立吧。好，你来啦，那你自己来。小明，现在喇叭声音怎么样？可以了是吧？好的，我看看。行呃，可以继续。。嗯，好，我看到了我看到了，没问题。.哇，都成功了哈，来继续。那这次观察可仔细了，来再听听题。减少一根面团，使等式成立。对，减少一根面团。.好的，小明，这都不是树，你为什么要放上去呢？小明，你做题必须要明，你不可以这样做题哦，8减3等于3吗？你错误的答案为什么要往上放？8减3等于6吗？8减3等于几？8对不对？对，然后减3个765。对，原来是刚刚计算出错了。对你要确定你你的做出来检查没问题才能放。对你看你放的数字自己不明白，怎么能当答案呢，对不对？你像这样的这样的。有的你放上去，你自己都看不明白这是什么数这种情况你能把它当答案放吗？不可以8减3等于3吗？也不等于3。那你为什么要把它当做答案？你想试试吗？那是不可以的呀。对吧准确做题哈。好，来给大家下一场红包雨，来拿吧，快拿。212。嗯，好，来给给大家做一个神秘任务哦。那我先陪你听规则，开始游戏，怎么游戏呀？然后听喇叭喇叭说什么？哦，喇叭给提示了是吧？我懂，就是说你看到什么数，你就点什么数，是这个意思吗？这次还是6吗？还是6吗？对，那你来。点开始游戏。对，也就是说你看到什么数就点什么数，对不对？看到什么火柴棒数字就点什么。.嗯，找到火柴棒数字了，再找再找找一找。.好了，可以很好收回喽，真不错。来，那我们来继续下面的挑战。好，出发喽。.B。.好，来，那我们一起来看一看哦。好，来先听喇叭。好，点击聚灯装置移动一根电线使等式成立。好，那我们继续看3加6等于。3加6等于嗯，小明小昭告诉老师了，其他朋友呢？哦，博轩告诉老师了，小张呢小张洋洋9对，3加6等于9。好，行，那你来把九变出来，好不好？你自己变。对，这是你的任务。酒长什么样？酒长什么样？博轩不要瞎点，你这样的话，我就直接收回，重新学了，重新认数了。酒长什么样子，只能移动一根电线。对，小张听喇叭。老是不跟节奏啊，洋洋也是九长什么样子，这是6宝贝。好，来，那有的朋友忘记酒长什么样了，在这儿好，酒长什么样子？酒长这个样子，对不对？好，你看。嗯，你看九上面有个小方块对吧？下面有个小弯钩，这就是9，是不是六是上面一个小弯钩，下面一个小方块，这才是6。没事儿，老师还是要陪你再认认数，好不好？再认认数，咱们再做题，别急，你把数先认全了。来，朋们朋友们好好看，好好看。.这是零对吧？这是一好，那接下来我给你一个任务好不好？我给你一个任务。我现在呢现在所有的小朋友做一件事情，听我说话，现在所有的宝贝把右上角的小灯泡点开，快点。把右上角的小灯泡点开，快所有朋友把右上角的小灯泡点开，马上，不然我就收了。博轩，你还没有点洋洋。听我说话，洋洋把右上角的灯泡点开。我现在所有朋哎呀。听老师的要求，这个题咱们做过了，不是让你做题。所有小朋友把右上角的灯泡点开，听明白了吗？我打开。打开等一会儿，因为还有朋友在拖拉没有打开，马上所有朋友把右上角的灯泡打开，打开了没有？全部打开了没有，没打开，我也不等了。洋洋，我不等你了。好，现在所有的小朋友照着右上角照着这下面的火柴棒，把这9个数写下来，从1到从0到9画写在上面，动手写。看到没有？所有小朋友把火柴棒数字从0到9写下来，我已经把画笔给你了，来吧，从0到9。从0到9开始写，就跟着上面写就好了，不用擦，写错了，换位置写。小昭已经在写012了，还差3。三好像不对哦，数字三写的不对哦，重新写4数字四怎么写，写火柴棒数字。对，写上面的火柴棒数字写的方方正正的五怎么写？对，小赵很不错，有认真在写，我看看小明。小明写到几啦，0234很好，非常好。多认认这些火柴棒数字，小张写还写的不够清晰。好，博轩的等一下拿来做示范，非常完美，我都不需要补充了。对。嗯，小昭也不错，也认真解决了。我宣的，然后我看小明的小明到几啦？五了到八了。好，收回喽。那大家看哦，你看你看博轩。火柴棒数字看了没有？清清楚楚的吧，0123456789，每个数字长什么样，大家一定要知道哦。好，那接下来咱们继续来再来第二个挑战。好，来点喇叭听题，宝贝们。超过了，赶你。好。可以对，六长什么样啊？小明。5加1等于66长什么样？你只能动一根火柴棒，如果你发觉你第一次移错了，你就点右上角的小圈圈重新拼。因为你只能动一根。对，重新改变其。重新来想想动哪根火柴棒，六的上面有个小弯钩，下面有一个小方块，想想怎么办？只能动一根，小明，说明你动的这一根不对，换一根5加1等于0吗？自己都不确定的答案，你为什么总是要填上去呢？重新来，你要。只重新来，小明，因为你只可以动一根火柴棒，这根火柴棒没有成功，说明他不行换换其他的。六长什么样子？上面一个小弯钩，下面一个正方形，所以你的上你的上面多了一根，下面少了一根。现在是6，这样才成功了。好，行，接下来继续。对，还是只能移动一根火柴棒啊，只能移动一根来就是。如果你移动一根之后没有成功，那你就点这个小圈圈取消，重新移，重新换其他的火柴棒去移。.嗯，那你就得想想三到底长什么样子。对，三怎么写。6减36减3，看清楚算式。。对，可以的。好，认认数。来，接下来咱们进入今天的挑战题了啊，给你一个终极难关了。我们去看看还是只可以移动一根火柴棒哦，你听听题。嗯，来。 对，计算还可以。我陪你学过的这个计算，9加4对吧？好，对，小明这次可以的。9加4呀，9加4就是9先加个一再加个3。9加1等于1010加3等于13。洋洋，9加4等于几算出来了没有？9加4是13，对，13的3怎么变出来呢？好，我看到了。对，小昭十三的三怎么变出来？你现在是15，怎么把15改成13？三长什么样？小昭塞下一个耳朵，怎么把五改成3。塞下一个耳朵。好。9加4等于13。对，没问题，就是这样的，就是这样的。好，行，我所以看来大家还是得练一练改数了，对吧？好，行，自己改吧，来给你来个快速的切题，你把所有的都改一改，把每个数字都改一下，改吧。改成其他的数就行了，动动手呀，拖它移动一根火柴棒，移动一根火柴棒把它变成别的。瑶瑶。.看到了看到了，没问题。.可以的，不错嗯。对，5可以加加一根火柴棒，变成9，也可以变成6，对吧？可以变成好多种数字。好，行，没问题。来，咱们现在继续出发喽。.好，下次就去金字塔闯关喽。来快来宝贝。.嗯，好，那下对，下课之后要跟爸爸妈妈一起认真讲解哟，给大家把星心奖励送一下，自己拿哦，自己拿。嗯，好。好，刚好一样。行，我给大家星心再补一点。好，来请上台哦。对，摆好姿势，摆好姿势，等一下我再调我再调整一下。等一还怎么还有小朋友是白白的呀。而是还没有刷新出来。小张好哇，博轩的画好漂亮。哈哈哈好，行，来摆好姿势，我给你们咔嚓，洋洋的小卡牌，小张好，小明小张32一咔。对，今天思考很认真哦，不错的。不错的啊。好，对，行，那好，要不要换个姿势，要换姿势吗？要换姿势吗？小明。洋洋好，来32小明，你可以坐高一点哦。宝贝321咔嚓。对，很帅气啦。好，行，来，等一下下课发给你们啊。好呃，博轩，你有问题问老师吗？没有是吧？哦，这是你的姿势。好，没问题。那好好的去完成任务，咱们就下节课见，拜拜，快去吧。嗯，好的，可以的。',
                           '和成晨梦梦，你们好，可以看到沙木老师了吗？小朋友们可以了呀。好，我们马上就要开始今天的冒险了，需不需要去一下卫生间呀？小朋友们。不要不要的话，我们复习一下上一节课我们一起去哪了，还记得吗？上一节课就去扫地雷了吗？ 不是吧，上一节课我们好像去对应这个形状和颜色去找对应的位置去了，对不对？好，那今天我们要去扫地雷了。我记得我们以前好像玩过扫雷小游戏，唉，你们还记得吗？我们的舅啾也来了。有有小朋友还记得这个游戏规则的吗？可以来跟我们分享一下程程。嗯嗯，没事，我们听成程说一下这个扫雷游戏的游戏规则是什么。嗯，求周，你来说一下我们的游戏规则是什么呀？宝贝。成成，我们的扫雷游戏游戏规则是什么？嗯。嗯，那那里边有数数字，数字代表的是什么意思呀？表周围有几个地。哦，很好，小铁筒啊不波和袁庆言，还有啾啾和俊说，有听到我们晨晨分享的这个扫雷游戏的游戏规则吗？扫雷游戏游里面的数字非常的重要，数字就表示这个数字周围地雷的数量，那周围指的是什么意思啊？小朋友们。我的周围指的就是我的前上边下边、左边右边啊来画一画。来，假如说这个数字指的就是它的上下左右，还有左上右上左下右下可以理解为它的一圈，能理解不？小朋友们。Yeah。好，你这个位置写的是个二，就表示这一圈有两个雷，写的是个三表示的意思就这周围有三个雷。好，那今天你们就是工兵了，又一起去扫雷了，千万不要让地雷爆炸哦，来看看今天的内容。..Yeah..瞎没有皇上，大家都是不懂的。.，哪有什么妖怪，别动雷，快帮帮他。哦，我们一起来看一下来这些电。好，我们要根据这个什么呀，去根据格子来标记地雷啊，用什么颜色的去标记地雷啊？小朋友们。红色的旗子呃红色的旗子啊去标记地雷。好，那我们一起来看一下。嗯，那这里有好多数字呀，102321你们觉得我们可以先从哪个数字去看呢？最上面的数字是吗？你们是说这个从上往下这样子去看是吗？可以的。好，那比方说这里的一一指的意思就是它周围一共要有一个地雷，对不对？那它周围指的是哪些格子呢？谁可以来帮我圈一圈。好啊，不布来一的周围有哪些格子？嗯，继续非常好。Yeah.对，你看第一这个数字在边上，它的上面是没有的，所以是不是就相当于它这一排加上它下面这一排呀，对不对？那其他都是数字哦，数字就是这个地方就是个数，啥也没有。那它的周围要有一个雷，那只有这一个空格了。你们说这个空格是想还是小朋友们。地雷了呀，地雷我们要放什么样子的旗子呀？小朋友们。红旗对不对？哎，好，然后呢，其实你们在这里可以选择这个三，对不对？三的周围，它的周围指的是哪一些格子呢？据硕来帮我圈一下宝贝。单的周围指的是什么？.很好，那这个地方表示的意思是它的周围一共要有几个地雷呀。据说。非常棒，它的周围一共要有3个地雷。那其实刚刚我们这里就能发现它周围除了数字以外，是不刚好有三个空格呀？小朋友们。对不对？哎，那你的这三个空格不就表示的是刚好三个地雷的位置了吗？是不是？所以你们后面在看的时候，可以从比较大一点的数字去观察。那写完之后可以再用其他的数字去检查。比方说这里的这个二哦，这个二的周围指的是这里，它的周围是不是刚好两个雷呀？小朋友们检查一下没问题了，再去点勾勾。好，所以后面在做的时候，大数去开始啊。小朋友们，那像这个就是我们可以先从数字几开始。宝贝儿们四四的周围指的是哪里呢？四在这里，它的周围是好好圆来帮我圈一下。好，那现在我们数一下四个周围一共有几个空格呀，小朋友们。5个空格，那我们只有4个雷，但是我们会发现它怎么样啊？对，多了一个。那我们能确定是哪四个吗？小朋友们。不能不能确定，咱们就不能从四开始去看了。那对，那三能不能确定啊，小朋友们对不对？所以你看从大数开始去比较好，容易确定一些。那你们自己来试着完成一下加油。.三看完之后想想从谁开始啊，小朋友们不要直接吃饭啊，我的天哪，浩源，你这满地了呀。.嗯，举小白旗吗？.举小白棋吗？小朋友们，我的乖哟，来，我收回魔法了。来，你们看看你们的这一个，让我看看看看是谁的来。啊，小甜筒的这个你看。数字二表示的意思是它的周围只有几个地雷，你这周围都几个了，记住了，乖乖。对呀，那据说就更离谱了，宝贝遍地了的嘞，宝贝儿，我随便踩一脚都炸了，乖乖你呢。所以你看你那舅揪的这个也是一样，你二表示的意思是什么呀？舅舅。那你家全安全呢，一个地雷都没有宝贝儿。所以你看啊咱刚刚做的时候就记着一个从大数开始，那所以这个地方就是你们出错的原因了。咱刚刚从三开始的，对不对？三周围刚好三个空格表示，这里刚好就是它的三个地雷。那这里完成之后，我刚刚还提醒你们了，好好想想下一步到底看数字几。你们下一步看的是数字几呀。2下面左边的二还中间的二还是右边的2啊。你要是看左边的这个二的话，你跟他们都不搭杠。二的周围一圈空格，但是里边只有两个雷，你能确定是哪两个吗？对不对？所以你要么看中间，要么看右边的这个二了啊，都行，看哪个都可以。那你看如果看右边的这个的话，它周围就两个雷呀。你这两雷已经找到了呀，你说明你下面两个格子里还有雷吗？没有雷的话，放什么颜色的旗子。绿色绿色是很安全的啊，然后你接下来再找它挨着的数字，你这个二是不是一样的，这个二的周围指的是哪些格子呢？青言帮我圈出来。啊，2这并且这个二还表示它的周围一共几个雷，小朋友们够不够？还不够啊，到底够不够，够了，那说明左边的三个格子里是雷还是安全的呀？安全的呀，对不对？那梦梦他的周围两个雷，现在够不够两个雷，够了，左边三个格子里还放雷呀。这是安全的了啊，放绿色的旗子了，这里能理解不？小朋友们。再往左边去看，看二也行，看四也行。这个二的周围两个地雷，但是现在会发现它的周围有雷吗？一个都没有，那刚好还有两个格子，那说明这两个格子里面是什么？啾啾都是红色旗子了。那最后再来看这个44表示它周围一共要有。四个地雷，可是在现周围才几个地雷够不够？那说明最后一个鸽子是什么？所以你看小朋友们看着小小的棋盘，觉得挺简单的，实际简单不简单。哦，你你按你们的那个填法，把自己都炸飞好几次了。我的宝贝们所以看的时候，从大数据开始，从你能确定的地方去开始，一定仔细去观察它的数字啊。来再来一个，这个想要从哪开始去看？。嗯，还好，匆匆忙忙就丢不去啊。好。据说啊不不我好，去年也是正确的。OK浩源也进去了嗯。这个我们只需要看其中哪个数字就可以确定了。小朋友们。四对的呀，四就在最中间，对不对？而且这个剩下它那个周围指的是不是就是这里所有的格子了，刚好四个空格，四个地雷，那这四个格子全是地雷了。好，这个完成的很不错啊。来，你接着继续看一看。.啊，我们一起来看一下这一次的这一个来仔细听。好，我们要这一次是榴莲地雷了啊，又会爆炸又臭。而且这一次要用什么颜色的旗子去标记，小朋友们。红旗啊红旗地雷，绿旗表示安全。好，那这个游戏就比较像咱们电脑上面的那个扫雷游戏了。它一开始是一个格子里面都没有啊，你随便点一个格子会出现一些嗯空格和数字，对不对？数字就是表示安全的，并且数字表示的是这个周围的地雷数量，像这种白色的空格，看到了吗？小朋友们。这个地方就是安全的啊，就是没有雷，就是这个意思。那剩下盖着的这些格子是我们要去推理的地方，能理解吗？小朋友们。那那我们先在从哪个数字去看一呀，小朋友们三非常好。那这个三好继续说来，我从这个三开始了，那么我能得到什么信息呢？你来放放嗯，它的周围要有几个雷。对，那是哪三个呢？啊，我看的哪个三呀，据硕。对哟，他没到那么边儿啊，这个山的周围来，你还是帮我圈出来吧。这个山的周围指哪几个格子。这对吗？据是说打勾勾的这个三的周围把它包起来的那一圈是哪几个格子？你一个一个圈，它的周围是哪些呀？好，来，军硕，这个格子挨着他吗？他俩挨着吗？不挨着那叫他的周围吗？小朋友。你好好看一看我圈的那个勾勾在哪，你能看得到吗？所以说找准啊它的周围到底在哪里。那你一个一个圈吧，我刚刚说周围指的是他什么位置的格子。它的上下左右，还有左上角、右上角、左下角和右下角，那一个一个圈吧，它的上面在哪？下面呢你不用一笔画了，就是说我让你一个一个去圈它的上面格子在哪里，打勾勾圈出来。他的下面格子在哪里？ 这个山的下面在哪里？据说它的左边在哪里，右边在哪里，左上角在哪里？右上角在哪里？左下角在哪里，右下角在哪里，再把它的一圈圈出来，就说。 所以看清楚了吗？小朋友，它周围的每一个格子跟它都是挨着的啊。你如果找跟它不挨着的格子，那不叫它的周围了。所以如果这个格子它表示的意思是它的周围一共要有三个地雷，它的三个地雷在哪里？看到了吗？小朋友们。嗯。不刚好三个空格，对不对？所以放的时候一定先点住这个数字，找它的周围在哪里，再去看地雷。那同样的，除了这个三以外，我们下面还有三呢？这个三的周围在哪里？静言。你怎么也乱圈呢？它下面这一排是不是他的周围呀？小朋友。把这周围所有的格子都圈出来。对呀，那上面那一排挨着他吗？青岩再重新圈上面的二挨着他吗？好，这个三表示的是什么意思呀？对，那现在是不是已经有一个了，还缺几个小朋友们。两个那是不是就是两空格里面了？好，所以你看大数字非常非常好确定啊，然后放完之后，你可以再看一下旁边这个三去检查，你看它的周围指的是不是就是这一对，对不对？刚好也是三格，是不是？好，那我们接下来看下面的了。看下面就看下面的数字哦，好，靠中间一点，这个一这个一它的周围指的哪一些格子好浩圆。嗯，很好，那这个一表示什么意思呀？就啾这个一表示什么意思？小甜筒，这个一表示什么意思？好，周啾浩源一起来说这个仪表是什么意思？周啾这个仪表是什么意思？地雷够不够够了，那说明剩下三个格子里边还有地雷吗？小朋友们。没有了，那我们要放绿色的棋子了啊，你看一下子一半儿就没了，对不对？再接着往右边去看一这个一的周围来，就是说再来帮我圈一次，它周围指的是哪里。哎，浩浩，那这个一表示的意思是什么意思呀？非常棒，够不够够，那上面这个格子有雷没有啊，那都够了，还要再放个地雷呀。这不已经够一个了吗？那上面下面这里有没有地雷？没有地雷的。好，就这么简单，小朋友们先看数字，然后绕着这个数字周围去画圈儿。看看它周围这个数字是几就表示它周围有几个地雷，然后再去数地雷数量不够了，我们就去补够了，就说明其他位置全是安全的。来，下面的这个交给你们自己来完成了，加油。..嗯。 迅树，你左上角的二周围三个地雷了那，对吗？对呀，你把左上角的三个擦掉，你想想这三个到底怎么去判的。好，好圆，你真的没回去。好啊，这是有点错。今天三秒是什么意思啊？丢丢。 23周围有没有三个地雷啊，那你还还放绿色的旗子。.据说那二的周围现在又只有一个雷了，你说检查一下也不烦啊，就就这也是样，二的周围就一个雷，还放安全呢。来三开始去看啊。三的周围有三个地雷，对不对？那这三个就是三个地雷了，你刚好三个空格。然后接下来再看三，它的周围一共三个地雷，现在够不够，还缺几个啊？两个，那这左右两边刚好是呀，那啾啾这个地方怎么可能还会再去放绿色的地旗子呢？然后接下来再来看2。二的周围一共几个地雷呀？小朋友们两个地雷来庆言，你的左下角能是绿色旗子吗？没。跟着青岩跑，一直挨雷炸，宝贝儿，周围两个雷啊，两个空格，那刚好这都是地雷，一定好好检查我，要不然就会挨炸了。乖乖们好，再往上面去看这个二指的是周围指的是哪里呀？去说帮我圈一下。你又跑那么上面，上面最上面一行挨着这个二吗？小朋友。那他周围要有两个雷，它周围的空格在哪啊，去放一放。 能理解了不？乖关，你看你们的周围都没找清楚，就直接往上放雷了。然后再来看这个2，它的周围是不是这几个格子，小朋友们对不对？两个雷够不够了？那左上角应该放什么？小甜筒结束了，你看。就很多小朋友在完成的时候，这周围格子都还没看清楚呢，你们这个小手就开始摘旗子了，先去点数字看周围好不好？找准周围之后再去放这个炸弹啊，下面的这个我们继续看看。 好，我们一起来看一下下面的这一个。好，这一个来一起来读题啊。小朋友们棕色格子是安全区，就是我们标数字的这些地方就是安全区黄色的地方有几颗地雷。9颗地雷，这里都帮你们记着数呢，请你们标记出来吧，给你们3分钟的时间自己来找一找，好不好？小朋友们来。你就告诉你一共有9颗地雷了啊，看这个数字去找一找。.他想钱从数字几开始去拍。.快去宝贝。。哇塞，我们的up布布5浩元庆言，还有啾啾来送给你们5颗这个认真思考的小星星都有完成啊，你们来跟我讲一讲吧，先从数字几开始去看那小朋友们。 星从数字四开始，就是从大数开始呀，是不是那四最大的呀，那四的周围刚好四个空格，所以这是不就是4个地雷？对不对？好，因为你你你这周围现在还没地雷呢，对不对？刚好四个混合，那都都是炸弹了。好，然后我们再去看三啊，这个山已经没有意义了，因为它周围已经放完了，那看这个山，它的周围要有要有三个地雷，那现在它的周围才只有几个地雷，小朋友们。两个，那说明上面这个地方是什么地雷对不对？好，然后再接下来往上去看2A啊，那这个二周围不对，这个2二的周围有几个地雷，小朋友们。两个地雷，但是他现在只有一个，说明上面这里雷是什么地雷是不是好，那你接下来就可以再排除了。来这个二的周围两个地雷够不够啊，小朋友们。够了呀，对不对？那说明左上角这个地方还有人吗？安全好，然后再接下来看往下看啊，咱们A这个一一的周围有一个地雷了，那说明这一圈还有没有地雷了？小朋友们。那你这缝儿里面是不是都可以去放红绿旗了呀，对不对？包括我们这个一是不是一样的情况，周围一个地雷，那它的上面这里也就是安全的了。好，然后我们接下来你看右半边是不是都完成了呀？咱们接下来往左边去看，数字越多越好推，因为数字。发语格都占着了，那空格是不是就少了呀？小朋友们对不对？你就好确定了。比方说这个啊，它的周围你看全是字儿，它的周围还带有俩雷，现在有雷吗？没有对不对？好，那所以我们的这个这俩空格都是什么呢？小朋友们dlayok好，然后我们接下来再往上面去看。这一个二它的周围是不是也得有俩雷呀，但是它现在才几个雷，宝贝们一个，那上面还缺几个成号，那这个格子是什么了？地雷是的，那我们剩下哎，其实你会发现数字是不是已经找完了，小朋友们你也可以再检查一下，你这个一周围一个雷够不够？小朋友们。够了，那上面三个格子有雷吗？小朋友们。没有，你这就再一次验证，咱们找的9个是正确的了。所以后面你们可以先从啊数字比较多，空格少的地方，或者说数字大的地方先去确定，好不好？好，小星生送给你们啊，你接着继续再来看一看。.好，谢谢你们的帮忙。咱们真是玩了一节课的地雷，他们也被看到原形的都害怕了。今天的扫雷游戏，你们觉得好玩不好玩呀？主要是要找准它的周围在哪里啊，这样子再去看地雷就可以了。好，看到你们上课前进行了课前预习。好，送给你们课前预习的小星星。今天的课后练习，辛苦你们认真真的看清楚数字，再去找。地雷O吗？小朋友们。OK好，然后上一次的课后练习有认真完成吗？嗯，好，我们的青言浩源啊，布布小甜筒传笑梦梦，哎呦，我们的句述非常好啊，就是100分。好，今天下课最后要，记得把上一次的练习给做一下了，好不好？就是我们你上一次应该是那个身体定妆记忆法了啊，你要给足自己时间去记忆一下啊。好，那今天的冒险，我们到这里就结束喽。小朋友们辛苦你们了，下课之后好好休息一下，我们下一次冒险再见喽，小朋友们拜拜辛苦了，下一次见。',
                           '可以听到老师说话吗？可以，是不是？那现在还没到上课时间，有没有同学现在想上一下卫生间的，没有。有没有谁想喝喝水也没有啊，都不用去嘛。好吧，可能大家已经提前准备好了，那老师拿画笔给你们玩着，我去找一找没到的同学。. . .小花笔我收回来啦，我们不玩了哦。我先检查一下大家的预热，还有我们上节课的课后题给你们送星星啦。最喜欢的小星星来了啊，芝麻均安满分，心余满分，白兔今天忘记预热了，怎么回事呀？我们应家团员也是满分，做的非常好？小白兔，等会儿你要是有多余的休息时间自己退出补做一下，好不好？嗯嗯，好，给你先送5颗。尹家宝贝第一次上课就收获了满分星星呀。好啦，我们今天要去玩一个扫雷游戏。哇，大家知道扫雷游戏怎么玩吗？嗯。又有同学知道的是吧，他们要去荒漠世界进行扫雷啦。그.Nice....那我们先来通过测试吧。大家注意听一听，我们要选出什么样的格子呀？哦，对对对，那有同学知道什么叫做周围吗？团原因加白兔和星语这么积极的呀。第一个问题就抢着回答，那么星语先来吧，你说说看啊，什么叫做周围呀？啊，你感觉就是红色格子旁边的格子，是不是啊？好的，那芝麻你来说说看吧。红色周围的这个格子。好的，小谭圆讲讲周围到底是什么意思。嗯，好。那这样吧，我交给你来点，你在那边点，我看不到。大家觉得团圆点的对不对呀，都是正确的吗？嗯，耶好吧，那周围的意思呢就是像团圆点的格子这样啊，要把这个格子围起来的，就不能让它有一点点空的地方。如果我们认为是旁边的格子，那就是回来边边挨着的，你看啊。假如只要这三个边边挨着的那有没有把它完全堵住呀，有吗？嗯，英家可能觉得有你看我从这儿画一条线，哎呦，然后就到这个格子了，然后到这个格子。那这两个地方是不是有大洞洞呀？那就没有包围起来了。你看我们的敌人就可以从这跑出去了。我们要做一个包围圈，把这个格子全部围住，能不能留下空空的位置啊？不可以，所以呢脚对着的地方也叫做它的周围格。大家知道啦。好，那我们来找一下啊。.我们要在空格当中写什么数呀？嗯，印家你说说看，等会要写什么数字啊。周伟达。嗯，对，地雷的数量啊，就地雷有几个，那我们就去填写数字几。有没有同学到我们的小小观察员上台来看一看。哇，好，团员还有白兔同学都想参加，先有请白兔吧，下一个团员，然后心语好不好？排排队，来白兔这个格子哦，你先看看他周围有几个格子。有自家。有5个，那你在这5个周围格当中发现了几个炸弹，发现了两个，那这填数字。嗯，对，写上数字二就可以。等会儿大家做完这一关，嗯，老师退出弄一下我的声音，我这边声音不知道怎么回事，特别小。好，接下来就到我们的小团员啦。来团圆，你说这个位置写几？你你跟同学们说一说，他周围出现了几个地雷呀。哦，所以数字就是。没错，周围有几个地雷，那这个格子的数字就是几了啊。好，下一个星语排队排很久了，来吧，这个格子写几呀，为什么写三？对，他周围有三个炸弹嘣好危险呢，这个格子它周围怎么有这么多炸弹呀？来静安，你瞧瞧啊，这个格子写几。嗯，为什么呢？这边麦克风声音好小。你等我一下。啊，今天你再说一下吧，我okK了，这个格子是假？He.那我们再邀请几位观察员上台，还有谁愿意啊？心宇又想来啦，我给印加一个机会啊，来到我们印家印加这个位置是几啊因为。他周围有对对对，非常好啊，周围有两个炸弹，所好吧，那也到你吧，来再给你一次机会，你来。耶喂，怎么又是一了呀？对对对，周围有一个炸弹。邓。啊，全对对对，你发现了啊，这次很巧，那下一次不一定会这样子。那等会儿大家看呢，就先看周围有哪些格子，再数地雷有几个就好了，好不好？测试通过啦，来题目交给大家。.. .嗯，那很清楚哦。芝麻，你看发光的格子就是在它周围的格子，你在发光的格子当中去数，你能数到几个地雷呢？这个格子就去写几心宇，你看发光的格子就是它周围的，大家可能不太明白周围的意思，你们先做一下，等会儿收回来讲一讲。..孙玉白兔和印佳把这一关做出来了，然后印佳和心宇都做了一道题的，你再等一下他们吧。静安可能不太明白什么叫做周围的鸽子啊。芝麻静安来，老师收回来给你们讲一下，我们再重听一遍吧。静安要看题目，芝麻同学也是你记得露出你的小脸蛋，让我找到你好不好？来，静安芝麻，我先点这个格子哦，你们先告诉我它周围有几个格子。数它周围有几个格子，有6个格子是吧？俊安吗？俊安找到他周围有几个几个呀。三个哈但我有听到不一样答案，有同学认为它周围只有三格，有同学认为5个，有同学认为6个。好，我们来找他。我们刚才讲过边边对着的，还有说它这个角对着的都叫做周围的格子。就是你要把这个格子给围起来，你数一个格子，两个格子，三个格子，四个格子，5个格子，它周围出现了5个格子。在这5个格子中有几个地雷，三个，所以这个位置就写三，明白了吗？芝麻好好看啊，君安你瞧，只要在它周围的格子。都是什么颜色啊？都是黄色都发光了，所以你不会看周围都没事儿，你只需要把黄色的格子数清楚去找炸弹。黄色的格子中我找到一个两个、三个、四个、四个炸弹，那这就是4。明白了吗？然后下一个位置啊，芝麻和君安告诉我这些几。啊，芝麻认为写5均安是写三是吧？芝麻，你先跟我说说，你知道空格当中要写的是什么数字吗？你知道空格要写什么数吗？嗯，写武就是你知道这个格子啊，它是要你写空格子有几个，还是要你数地雷有几个呀？对，那你再看呢。老师刚教过说黄色的格子就是在它周围的那属地雷的话，有一个、2个、3个，你看就没有地雷了。芝麻，你把发着光的黄色格子当中的地雷数一遍，数到几就填几啊。你你是觉得这两个地雷也也是是吗？嗯，对呀，芝麻就是我们在它周围当中去找地雷呀。你看这个地方是数字嘛，然后这个地方是空的嘛，没有，这是空格子，这个是数字格，然后这放了一个地雷，两个地雷，三个地雷。所以我在它周围的格子中就发现了三个地雷了，明白了吗？嗯，那我们做最后一道题，因为这道题呢，我们应佳和新宇同学、团员宝贝他们都做过了啊。 星语发光的格子就是在它周围的，你把这些黄色格子找一遍，你找到几个地雷就写几团员做的非常非常棒。第一环节所有题都做出来了，恭喜你静安，我们能够自己做出一关了，有进步的啊。你佳也是做完了所有题。好吧，来，我收回来白兔芝麻和心语，现在你们觉得比较困难的是什么地方呀？是什么地方不会做呀？是不会看他那个周围有哪些格子，还是不会数地雷。有几个宝宝。嗯，芝么，你可以说说看，你觉得现在是什么地方不会呀。是你会看它周围的格子吗？会，那会不会属地嘞？哎，也会，但是加在一块可能就不会做题。那我们看这个位置啊，我先随便点个位置来，新宇，你告诉老师他周围出现几个地雷。三个地雷对吧？那就选三，这不是很简单的。来be兔看这个位置，它周围有几个地雷。是，所以就是写三呀，让芝麻来看这个位置，它周围有几个地雷。两个那就是写二哇，其实芝麻星语白兔你们是会的耶，只不过自己做题可能不会看哈。来看这个格子周围有几个地雷。三个，那数字就写三了。来，白托这个位置写几写5。孙宇芝吗？看这个位置为什么会写舞啊，因为它周围你看它你们不会看周围，就看黄色。把黄色的格子全部找一遍，12345找到5个地雷，所以这个位置叫填5，明白了没有？来只把这个格子写几。是的，还是有进步的呀。有一点点可惜，我们芝麻今天暂时没有做出题目来，白兔，我给你送上三颗做题的星星。心雨宝贝再给你送两颗吧。芝麻也是啊，给你加三颗辛苦的小星星，等会儿加加油好不好？一定要认真观察周围，好好数地雷。.哦，这下可完蛋了，超多的地雷在旁边的。.那我们等会儿要在有地雷的地方放上静止的标志，在安全的地方放。安全的标志。好，现在你们来想想看可以先从哪个数字开始排了呀。嗯，心宇，你说说从哪个数呀？从一好哪个一呢？因为一太多了，你劝一下吧。嗯，但是心宇，我现在遇到一个小问题，我在你圈的这个格子中，我没找到一哎，我只看到是个空的格子，一应该是个数字。哪个一呀，你圈一下哦，可以可以，这个数字好的，那印佳你来讲讲这个一代表它周围要有几个地雷呀。嗯，想想数字是什么意思来着？人家刚才自己填过数字，你想想你为什么要填一，为什么要填2呀？因为他嗯。英佳，因为他周围有什么呀？好，你家可能是想上台，让老师认识一下，你是不是我们现在已经很眼熟了啊。下次如果想回答问题，我们上台要讲话好不好？嗯，不能像这样，然后我们喜欢上台，在上台中不说话的话，老师邀请你下去啦。君安想想一是什么意思？有一个有一个什么呢？是的，有一个地雷非常好。那这个一现在我给它点一点，周围格子就发光了。你看它周围有几个空的格子啊。一个对不对？哎，数字一就要一个地雷，正好有一个格子，那么这个格子就是什么了？因为就是地雷了。俊安和新宇同学做的非常棒。新宇呢帮我们确认了一个突破口，就是第一个能做的数字。数字代表周围有几颗地雷，像刚刚这个一，周围只有一个空格子，一个空格子是不是正好等于数字一呀？那我们就可以把这些空格子放上炸弹啦。好，再来看这个数字，一团圆说说是什么意思？有一个格子还是有一个地雷？对对对，有一个地雷。那你看到周围有没有一个地雷了？它周围格子就是黄色的，这些有没有地雷啦？对，所以所以是不是够了呀？它周围有一个够了啊，够了，我们就不管它了，我们再换一个吧。哎，星欣，刚才你听讲了一小会儿，那你跟老师说说二代表什么意思啊？周围要出现几个地雷。对，那一代表啊对，周围要出现一个地雷。你看这个一周围现在有没有地雷？嗯，有还是没有啊，有有几个啦。有一个，那一周围要一个地雷，都有一个了，剩下空格子还放不放地雷啦，放吗？不放小嘴巴说出来，大家别光。嗯嗯嗯嗯嗯这样点点头摇摇头，我们说一说啊，你看一的周围有一个地雷，我一个地雷都放好了，剩下空格子肯定是。什么呀？安全的啦，来再看这个二吧，藤岩蛇说啊，二就代表周围要放几个地雷呀。放两个地雷，那现在你看到周围有几个地雷啦哦，只有一个地雷的，所以我们还要再加几个。再加一个D类，对不对？可以啊，好，再放一个D类上来。等会儿大家做题的时候，想想看什么样的数字可以先去做的呢嗯。Yeah.哦，团圆觉得是最小的那我来试试看，其实这个一也是最小的对吧？但是它周围大家看还有几个空格子哈，心雨觉得只要是标一的都能做。那我现在找了一个一也是最小的。我们来看它啊，那周围有几个空的格子。有两个对吧？可是一周围只放一个地雷呀，那到底放哪个格子，其实只看它能确定吗？不能，那我换一个一吧，来，假如换成这个一，现在看周围出现几个空格子。有两个对不对？有两个的话，我只放一个地雷。哎呦，这个地雷到底摆哪儿呀？其实我也不知道呀，所以是不是从最小的数开始想。不是，不是说他标了一就一定能做。那从最大的数字来想呢，二就是周围要放几个地嘞。放两个地雷，你看老师啊，我这样子摆两个也行，让我这样子摆两个也行，分开摆也行，三种答案能确定吗？也不行，所以呀不是从最大数，也不是从最小数，而是从什么样的数字呢？，心宇觉得是下面有数字的，刚才新宇同学找了这个一，为什么他能做？因为他周围只有几个空格子啊，一个一个空格子是不是等于这个数字？你看啊，因为它正好有一个雷，有一个格子就直接放地雷就行。但我还可以换一个一，这个一周围有几个空格子。也是一个，你看一需要一个地雷，正好一个空格子能不能直接放地雷啦？然后团员说不能，但是团员你想呀，他就只有这个位置能放地雷，我就是要放一个地雷，除了放这儿，还有其他办法吗？没有了，所以答案是确定的，可以直接放这两个数字有一个特点哦，就是我们在它周围发现的空格子都正好等于这个数字，看到没有？你看一周围如果正好有一个地雷，我们就能放。如果二周围正好有两个地地雷哦，两个空格我们也能放。三周围正好有三个空格呢耶。也能放5正好有5个空格子呢。也能放，是不是呀？所以就是要去找数字和它周围的空格子是相等的，全部都可以放上地雷，剩下的做排除法就可以。你看这个一周围一个空格，一个空格等于一全部都放上炸弹，再从旁边的数字开始去排除这个一周围一个地雷够了，剩下格子安全。这个二周围现在只有一个地雷，我还要再加一个地雷，只能放在剩下格子中，像这样就完成了。.那我们要来举手啦，宝贝们请大家找找突破口，你们觉得可以先做五还是先做二呢？好，这样吧，选二的宝贝比个二，选五的同学比个5。五是这样子，五个手指头，二就是两根手指头。那，应加俊胺选择二芝麻星语星星选择五汤颜2是吧，选择二啊，白兔选择。那我要给同学加星星了，今天选的什么呀？好吧，恭喜心语芝麻同学获得了小星星，把小手放下吧。白兔，你一会儿二一会儿5，这样子蒙中的，我可不给你选想啊，不能所有答案都有。对呀，不知道那没想好，你可以告诉我不知道，对吧？刚才我们是不是说找周围的空格字要等于这个数字的呀？。我们来看22周围有几个空格子，三个空格子等于2吗？那就做不出来，看5五周围有几个空的格子。12345，你看我们找到了五周围正好5格等于这个数全部放炸弹。剩下的二再来看它周围出现了几个炸弹了。有两个了，剩下格子就安全了。炸弹够了后，剩下格子就是安全的啊。大家别忘记，一定是先去寻找空格子等于这个数字的，全部把空格放上炸弹，剩下的挨着挨着做排除。只要炸弹够了，那么空格子就是安全的。芝麻，你可以信欣宝贝大家做题可以去点这个数字的呀，数字不是会发光吗？它周围你们不会看周围就点数字，他会帮你把周围标出来啊。芝麻让你点数字呢。刚才老师怎么做题，是不是没看到？大家点数字，周围的格子会发光，你就去数空格子。如果空格子等于这个数字全部都可以放炸弹了。好，星星做出来了。白兔虽然不会做题方法，但是你猜对了，运气蛮好。嗯，芝麻我也不确定你是不是会的，但是俊安同学肯定会，他速度很快哦，他到了最后一关去了。我我把车题的按键关掉了，很好，星星所有关卡都通关了啊。啊，因为我把J体的按键关掉了。 那我要收回来啦。好，最后一关我收回来讲吧，我给大家送一些小星星。来，宝贝们看这道题，首先来数一，然后大家看我老师是去点数字的，你们也可以点数字，它周围的空格子就发光了，数一下有几个空的格子。那个三个空格等于一吗？那就不能做它来15啊，这个2二周围有几个空格子，5个等于2吗？你做他哎，芝麻说等于5个格子和二，怎么会相等的啦？不会啊，再看三三周围有几个空格子。三个三个空格子是不是等于3，还有三个地雷呀，所以这三个空格子全部都是地雷了。再看这个二数它周围有几个地雷啦。有3个芝麻，看清楚属黄色的发光的格子，找到几个地雷，找到两个对吧？二周围要放两个地雷，已经有两个了，剩下空格子就是。安全的地雷已经足够，剩下位置就安全。再看一一现在还需要放一个地雷，它周围只有一个空格，那我们就放地雷，会做了吗？白兔看懂没有？看懂了。好，那这一关我们来找一找突破口，邀请大家做我的分析，小能手观察大概半分钟，找找突破口在什么地方，可以先填写哪个数字。好，团圆，你说先做哪个数？3好，我来看看啊3三周围有几个空格子，三个三个空格子等于3，全部都要放。地雷对，全部都放炸弹，只要空格子等于这个数，那全部都是地雷了。好，那下一个数呢看哦，白兔看二啦，星雨看极。嗯，拜托你说为什么要看二呀？哎，你搞错了，其实看二没错，因为二和三挨着最近嘛，我们之前说挨着挨着做排除，看这个二二周围放了几个地雷啦，那还要地雷吗？嗯哼不要了，不要的话，这个空格子就。安全吧安全的啊，来再看挨着的这个一来应加，你数数他他周围出现几个地雷啦。一个说三个地雷的宝贝，看清楚一周围黄色的格子有几个地雷。一个哦，你们老师问的是地雷有几个，不是问空格子啦。所以印佳一周围还要不要放地雷啦，你想想。啊，不需要了，剩下位置就安全安全安全。好，最后这个一啊，心星看一周围要几个地雷。哦，那他有几个空格子，所以这个空格子摆什么？对呀。现在大家明白了吧，那我们做题先观察数字，找出第一个可以做的数字，这就叫做突破口。那静安来说说看什么样的数字可以作为突破口。哦，一定是最大的吗？这样我们刚才不是做过这道题，老师调回去给你看哈。你看这里边最大的不就是这个二嘛，但是这个二周围出现了三个空格子，那能做吗？不能，所以呀不是最大的，也不是最小的，而是要找什么呀？找什么呀？空格子和什么相等？对白兔空格子和数字相等的，把空格子全部放上炸弹，然后再挨着挨着做排除就可以。.Okay..大家进步好大呀。芝麻芝麻这样哈，你先跟我讲一下二是什么意思啊。嗯，那你点一下下面这个2。下面你看他周围你放了几个。那为什么放5个呀？来，芝麻，刚才老师不是教过吗？你先把周围空格子等于这个数字的放上炸弹，哪个数字周围空格子等于它呀？你点数字去数周围的空格子，点一下数字吧。这个二周围有5个空格子能做吗？换个数点一下。对你要学会点格子数周围有几个空格呀，那做不出来这个三周围有几个，那你就全部都要放上么。你不用点宝贝，这个空格子不用你点。对你点数字，它周围就会发光啊，来再点2，这个二周围现在放了几个地雷了，不是你数一下数一下。那二周围要两个地雷，有两个地雷够了呀，剩下的就怎么了怎么啦？好好数一下周围的空格子好不好？没错呀，它周围有两个地雷已经够了，所以剩下的空格子就是安全的。地雷已经放够了，就不需要放地雷了。那周围还有呢，还有的格子呢？宝贝不是来，芝麻，你点一下下面那个2。你看发光的格子，什么叫做发光啊，就是它变成黄色了，看到没？现在黄色的不是还有格子吗？你还没放完呢。是的，然后现在就把所有的格子都做完了呀，你就做完这道题了。老师带芝麻做了一关，刚一回来，我发现呀，小朋友们都通关了呀，这怎么回事，太快了吧。进步这么大呀，老师给大家加了18颗星星哦。对的。芝麻。你你再这样子做题，我真的我要被你气死了。我刚才都带着你做了一关了，你学着去数数它周围有几个空的格子，数数有几个地雷好不好？你数着做题。芝麻老师给你送上8颗星星。你加油。哎，等会儿我亲爱的小白兔，这次你也不会是空格子了呀。来，白托，你看这儿啊，你先做的是这个一，它周围有一个空格子，所以可以放炸弹。这一步老师明白，下一步你看的是这个三，对不对？嗯，那三的话就是说一共要放三个炸弹，现在你看三周围还有几个空格子，那它还需要几个炸弹，还需要两个，那就全部都放什么。炸弹对不对？哎，再看这个三，其实这个三一开始也都能做，因为它能放的就这三个格子，所以这三个格子都是什么？都是是三3。对，你看。它空格子等于这个数，那这些空格子全部都会是炸弹，像这个三也是看到没有？它周围其实就这三个空格子可以放三个空格子等于三，全部都是嘣炸弹。那这个二周围已经有几个了。那剩下的就嗯安全安全，这个一周围已经有几个地雷啦，有两个地雷啦，看黄色的格子找地雷啊。一个对不对？那够了没有啊，够了好，够了，剩下的我们就安全了吧，会了吗？好，我再给你送上三颗小星星。大家做题的时候记得哦，一定要去数周围的空格子，只要空格子等于这个数，那就代表这些空格全部都是嘣什么。对，全部都是地雷可危险了。那地雷如果放够了，剩下空格子就安全啦。.太好了，我们也拯救了小聪聪，裴蕾也成功了。大家现在去完成什么啦？课后题加油，拜拜。记得下节课要做预热啊哦，宝贝们周三放国庆不上课，星期三没课了啊。哎，白兔，你说吧。啊因因为印家周三的时候已经放国庆假期了，老师也放假，你们也放假呀。好啦啊，我们下课啦，再见，拜拜英。送一个爱心。',
                           '好，老师老师去喊一下没到的朋友啊，你们准备好啊。好，看看谁还没有来。小小张还没到呀。好，太来了啊，洋洋唉，是洋洋吗？是博轩天天问你天天说凯怎么还没来上课？你上节课是不是请假了是吧？我现在看来了，来了，你你天天课问他好，行。是的，好像连续两天没来，我去喊一喊晨晨啊，洋洋在的啊。甜倩洋洋的洋洋的网还是不太好，发现了吗？啊，洋洋，你可以喊一下妈妈啊。洋洋，你你今天网络还你这个位置不太适合上课。那位置每节课都有点卡，换个位置。对，换。换个位置哈。对，新来的小朋友，你们做准备，想想喝水，想上洗手间可以去一下好不好？嗯，还有个别小伙伴没来，我提醒一下啊，小明准备好了。嗯，晨晨来了啊，晨晨来了，做好准备哦。太小张了，现在我看一下，还是有一点点卡顿，有一点点卡顿，但是做题应该没问题。 做作业应该没问题。好，我先给你编下去了啊，我给大家送星星奖励，给大家送星星奖励啊。课前预习都完成了。然后就是大家的作业，老师说作业了哈。好，上一节课的作业啊开始满分啊，之前那节课的。然后博轩和小明晨晨也是满分。博轩和小明是一个错题，洋洋洋洋上一节课出错。有点多，洋洋啊，洋洋一定要注意了，作业做准确一点点。好，来，我把星星奖励送一下。我刚刚念到满分的小朋友举手，作业没出错的，满分的举一下手啊，看和晨晨是吧？多5个星星奖励。好，来，那咱们就开始今天的学习了啊，跟老师出发喽，跟我出发喽。小招快加入啊。.. 好，那我们一起来看一看。好行，我们要干嘛呢？嗯，好。그.啊，图形的规律啊，我们来看一看。然后呢，在这四个图形中选择正确的一个啊。对，选择正确的一个。那先看看黄色的图形吧，好不好？黄色的图形呢这里个位置有三个小方块，看没有？对，这这个位置有三个小方块，这个位置有两个小方块，然后它们加在一起就变成了。几个小方块呀。5个方块啊。对，所以我们就是发现了呃右边这个图形，最右边的这个图形就是有两个前面两个图形组合起来的，看到了吗？看发现了吗？嗯，你看你能不能发现啊，你看没？Yeah.是合起来了。对，合起来了。前面两个合成了第三个图案。然后这个也是你看对，就是你要观察前面两个合并在一起就变成了第三个图形，所以你自己看啊，这里的四个小方块合并在一起会变成哪一个图形呢？变成一个十字吗？变成一个绿色的十字吗？这个肯定不是吧，这个太不一样了。会变成四个小三角吗？它它是正方形，会变成三角，不行，那是哪个正方形呢？嗯，上面的还是下面的呢？好，来，那你们自己来选出来啊，是上面的正方形还是下面的正方形呢？你来选。对，选出正确的正方图形嗯。.就是你看就是最右边的图形，是由左边的两个图形拼起来的啊，你就看它能拼成什么形状就好了，你去观察它哇，还有美味的汉堡呢。噔等等等等，你不要着急哈。对，不要着急，看好了再说。.对，你看两个半圆拼成了一个完整的圆啊。好，第三好，有小朋友好了是吧？嗯，不急。对我觉得这个刚刚做的最不准确，那咱们一起来观察好不好？好，你看。就是前面的三个东西，对不对？组合成了一个大汉堡，对不对？组合成了一个大汉堡。你你先安静听我说嘛，它组合成了一个大汉堡，对不对？然后这个是中间的肉饼，是不是？这是中间的肉饼，这是上面的面包还是下面的面包呀？下面的面包，那咱们还缺什么缺什么呢嗯。上面的月面包，咱们缺不缺肉饼呀？咱们要不要肉饼呀？嗯不要对，我们已经有肉饼了呀，对吧？已经有面包了呀，所以肉饼，我们不要，我们要不要下面的面包也不要。下面的面包有已经有了，还要不要不要就缺什么呀，就缺什么呀？对呀。是不是你缺什么你就放什么嘛，好不好？你看就像第一个这个汉堡，上面的面包有了，下面的面包有了，中间的青菜有了，合并起来了吧，是不是这样的，缺啥放啥啊，宝贝缺什么放什么，你看只能选一个啊，只能五选一。来对你要先看再选啊，你先明确你你要干嘛，好不好？这个特别可爱啊，你看他头上的那个小装饰有什么特点？嗯。选好点确定，小明点大力熊右右下角的确定。对，点不了啦。用力点呢，再一下再试重新把汉堡点一下，把汉堡点一下。我刚刚帮你清了一下。对，然后点确定。没关系，我可以帮你切题。对，来，那我现在要请一位小朋友说这个黄色的小怪兽啊。好，看发现了这个黄色的小怪兽它有什么特点呀？你说说呗嗯。.明白了，就是左边一个角，右边一个角合起来就是两个，是不是可以嘛？那谢谢你哦，来紫色的晨晨想说是吧？那你说紫色的紫色的角角有什么特点呢？.哦，先是一个，再是两个，然后就合成了三个，对不对？合成了三个啊。好，行，越来越难了。对，那蓝色的来一位朋友说一说主动一点。好，小明举手了啊，小明说一说吧。蓝色的嗯。两哦，第一个是两个，第二个是两个，合起来是。嗯，第三个是4个。好，谢谢小明啊，非常好。行，那接下来我要问你了，第一个是几个呀？两个第三几个呀，这两个，这是数一数嘛。5个，所以缺几个呀，缺几个角娇。三个对，缺三个啊。咱们看哪个小怪兽上面是三个的，你选好了，你就点确定好不好？对你选还。刚没选完的选一下啊，选完了就已经选了是吧？好，可以可以。对。好，来啊，那接下来呢咱们来来一次星星雨好不好？咱们来领一下星心啊，来准备好，哎，怎么点成随机邀请了，来可以了。Thank you..你真棒啊。行，跟着我继续闯关吧。来宝贝。吃啊。.好，来，那我们一起来看看啊，接下来的挑战来。好，行，我们来观察一下规律啊。哇，好好玩呀。好，这次咱们一起看啊，七彩小球呢，是不是来那这次我们我们一起来看好不好？我们看最多的这个吧，最多的看这个位置，老师用黑线圈出来的，这里出现了，别急，你先报给我，你看到了哪些颜色的球。蓝色。黄色、绿色、粉色。对，看那些小从哪来好不好？你再看看前面的三个位置，看看小球从哪来。红色的小球哪来绿色的。我看看比如比如这个小球在这个位置，对吧？我打个勾勾，在在右下角，哎，我爷爷哎来，然后这是不是有个小球，是不是？看到没有？是不是右下角右下角有个小球，所以你发现了吗？你发现了吗？好，能说出来吗？怎样的规律呢？能不能说小明，你试着说一说，嗯，很好，你说吧。 好的，明白了，谢谢你啊。就是说你的眼睛看到了什么颜色的小球，最后组合起来就是什么颜色的小球，对不对？好，但是重点就是它们的位置啊，它们的位置，比如红小球，在右下角，最后合并起来是不是还是在右下角是吧？比如黄小球在左下角。合并起来，它是不是还在左下角，是不是你发现规律了吧？对。所以就是说它的位置不变是吧？那最后一幅图，红小球应该在什么位置？我要请一位朋友放红小球。好，开举手了。好，晨晨也举手了。然，小明阳阳就四位小伙伴了，好不好？开先来啊，哎，我有四个球吗？我没有没关系，我还有新的题来啊，来开先放红色小球啊。嗯，行，谢谢你啊。我。我再请其他的朋友帮忙，然后是是晨晨，第二位是吗？来，晨晨啊，你来放黄小球吧。看看嗯根据。好，没问题，谢谢你啊。那接下来呢呃洋洋来放蓝小球好不好？洋洋放蓝小球。你发现规律就超简单，是不是说明你很专注，谢谢洋洋。洋洋，你做对了啊，但是还有一个小朋友没完成任务呢。好，来，小明，那你来把绿小球放一放，好不好？绿小球。拿住对行。可以啦，很棒啊。对，所以就是说组合起来是不是组合起来？可以可以来啊，来我们点开我们戳开戳哪里呢？要先听喇叭啊。嗯，一定很好吃。哦，所以你看看啊，你自己把这些坚果拖过去好不好？就是这个例子在什么位置，我觉得可以了，我觉得你应该可以了，你来吧，好不好？.跟刚刚的技巧一样呀，就是你看到了什么干果，你就放什么干果，位置不要变就好。对，博轩小明嗯做的很好，小周洋阳，我看晨晨。对了，晨晨非常好啊，看到了什么坚果就放什么啊，位置不要不要改变就行，很认真的观察了。对。又快又准确啊。还有一个开心果是吧？嗯，博轩做的很好哟，博轩做的很不错啊。来咱们再来嗯这次是什么是什么东西啊？好期待呀，你们来揭幕吧。等一下一起拿来。哇，是天气吗？好漂亮的雪花呀，还有花朵。 嗯。对，不宣快完成啊，上一个题你是做的最快的哟，快听喇叭继续做。对。 所以说我们要观察它的位置啊，观察它的位置。行，很不错啊。来嗯那。等一下嘛，哎，那你刚刚拼的图借我用一下好不好？你们先不许看，先遮住眼睛，先不许看这个屏幕，先不要看，真的没有看吗？被老师遮住的是什么呀？这有看你猜被我遮住的是什么？你现在可以看了，被老师遮住的是什么图形，说出来就好，我都要听。行，我听到了。博轩，你说是什么？好，没问题啊，我来揭晓，果然是太阳。对，所以我们还可以根据组合图形的样子来看看它原本在什么位置，把它找出来啊。好来。Yeah.来这个挑战成功啊，这个挑战成功咱们就下星星雨啊。对你把小球的位置给还原回去吧，好不好？对，红黄蓝绿本来在什么位置呢？自己给放回去啊，一个图放一个。第二幅图要放两个啊，是不是？对嗯。没有关系没有关系，你你耐心一点呀，你不要一失误就着急，你看看你眼睛往上看，你看有什么规律。你眼睛往上看，你的眼睛。你看看中间你看看中间的有什么小特点，中间的两个小球都在下面，发现了吗？对，中间的两个小球在放都在下面。对你掉入小陷阱，你就可以再去观察它了。对，红色放好了。然后晨晨你看你看最中间那一列的小球有什么特点？最中间那一列它的两个小球都在下面。对。 对，好，那大家帮我一起改好不好？你帮我一起改最中间的这个哪里不对呀？嗯，你看。哪里不对呀？你看这有几个小小球呀，这有几个小小彩球呀，这有几个小彩球呀。那这儿咋只有一个呀，对不对？我要请晨晨来帮忙订正。对我要请晨晨来订正啊。那你中间应该放两个小球才对呀，那你给放过去吧来。对，把嗯绿色小球给他放过去，然后别急嗯。虽然很棒啊，然后再看看对最后一列的蓝色小球都对上了吧，是不是右上角一个右上角右上角是不是好，谢谢你啊。对，所以你看你是不是可以先观察一下规律再去放呀，不要很着急的去放它啊。好，来给你一个神秘任务做一做好不好？嗯，对呀，很好玩的。来。.嗯，正方形的每条边必须是一样的，是不是你看看你观察。哦，洋洋在移动哈，我看看小昭有没有问题，小昭，我看看看好哦。这个不行，就换另外一个吧，观察一下再看嘛。没有关系啊，来，那你刚刚可以呀，你刚刚已经试了一次，那你有没有发现一个大正方形是由几个小方块组成的呀？你有没有发现呀，到底是几个呢？你看吧，我给你看。我赶紧数啊，123456中间再穿一下789。对，所以你会发现每一个大方块啊，大正方形必须有9个小方块组成，你不能多也不能少，是不是？那第一个是不是刚好就差三个呀，是吧？那你就移动过去呗，好不好？9个。你确定是八个吗？我来数123。456789相信我了吧，就是9个呀。好，那你再来啊，就是9个，你缺几个找几个好不好？现在有经验了吧，不要一的太过了，嗯，然后降下去。你数一数你缺几个放几个啊嗯。 说明你给多了，快看看到没有？12345切5个给5个啊，哪幅图只缺三个看好好想一想哪幅图只缺3个，而而且。位置要对来，那下课之后可以邀请爸爸妈妈继续，好不好？来跟着老师出发喽。呃，等一下下等一下下场大的。..好，来，那咱们一起来看看。好呃，咱们要把咱们要把这些宝石啊，把宝石放到正确的位置上去，好不好？咱们先来观察规律啊。Yeah。我们要放的是每一行的最右边这一个嘛，对吧？我们要放的就是每一行最右边的这一个啊，那你看一看，你看一看最右边的宝石最右边的宝石它是变多了还是变少了呀？快看看变少了，为什么变少了呢？我们来看看啊，第一组宝石，它在中间。这个位置有左边第二行的左边也有，右边也有是吧？第二个位置的宝石，它在看我层晨左边的第一个格子，有右边的第一个格子有发现什么问题了吗？发现了吗？嗯，这次还是把有宝石的放在相同的位置吗？还是吗？不一样了，反而是怎么样有宝石的，能不能放呀？看看放过宝石的是不是不能放了呀？你看看你看第一行中间的位置有宝石，不要下面有宝石，不要。第二个格子，你看两边有宝石不要，所以是不是只剩一个格子可以放了，看到没？你看懂没？对，那接下来呃谁谁来帮我给第二幅图打叉呢？就是放过宝石的地方都给我打叉。行好，这次因为大家都很主动，那我赚到谁就谁可以吧，嗯，我就随机抽了啊，不好不好，那给气球也行，那你你自己抢谁最先抢到谁来可以吧，自己出啊，3。21，你自己说。对，抽到了啊，K抽到了，请你上台，你的任务就是啊来，你现在的任务就是把前面两格子中放了宝石的位置都给我打上叉叉。对，因为我放了宝石的，我就不能再放了。你帮我在第三个格子中打上叉叉。交给你喽，明白老师的意思吗？这是第三个格子，你要把第一个格子，第二个格子有宝石的打叉来。来来第一个格子有宝石的地方打叉。第二个格子有宝石的位置，你来打。第二个格子有4颗宝石呢，帮老师打上叉叉。对，可以。嗯，就是有宝石的位置都打叉。所以你看所以你看第三个格子里的蓝宝石是不是就放在没打叉的位置呀？发现了吗？真的发现了哈，你要在图上好，对你要在上面好好展示哦。那接下来这一组啊，这一组也是放了宝石的位置，帮老师打叉啊，好不好？好来，那接下来谁可以打叉呢？都可以打叉吗？好，来老师把笔给你了啊，来打叉吧。像刚刚那样把放了宝石的位置打上叉叉来第三行。说明你还不是很第只要放第三行黄宝石就行了。黄黄宝石的格子。对，就是已经放了黄宝石的位置，打上叉叉。对。已经放了黄宝石的格子，都要帮老师打上叉叉啊。对，很好，晨晨认真看。然后我看洋洋哦，洋洋打好了。所以博轩博轩是不是多打了一个就第一行的中间。不小心啊，好看呢小昭呢小昭不好不太好打啊。你又把第一行打了。行，那我可以我看一下晨晨打完了没有，可以非常好啊。那借我用一下吧，好不好？借我用一下，大家都蛮棒的。你看就是有心心的位置都打上叉了，就是有黄宝石的位置都打上叉了，所以我们就在空格地方放放黄宝石，看明白了吗？就是在空格的位置放黄宝石，成功了吧？对不对？Yeah.好，那接下来你也是哦，你要在没有放宝石的位置，没有放颜色的位置啊，点上颜色看准了哈。对，来交给你了。在没有放颜色的格子，点亮，没有放颜放紫颜色的格子。. 对，看看嗯，小昭可以哦。对，那那如果有宝贝你发觉哎我点不准怎么办？刚刚有小朋友是啊，我点不准的时候，我怎么办？我教你一个小技巧好不好？你一定要一列一列的看或者一行一行的看，好不好？我会选择一列一列的两个格，两个格的看好，来，晨晨看屏幕了，来一起这两个格子有颜色吗？有没有有没有。紫色颜色呀，有没有，就是他没涂，所以咱们就要涂，是个这个意思吧？所以你说有是不是是吧？但是哎第二格有没有呀？第一格没有第二格有呀，对不对？所以能不能涂呀？不可以涂吧。好，再来看这里有吗？这里有就是所以所以我们是不是这里不能涂呀，对吧？所以是不是只能涂下面的呀？然后再看到这里，这里有颜色吗？这儿有颜色吗？都没有对，所以你就可以涂了嘛，好不好？好，对你可以把前面每次就两个两个的一起去看它啊。要是有的话，你就不能涂，好不好？好，或者你分开看啊，你分开看是怎么看的呢。And.你是一行一行的看是吧？都可以，但是一定要看准确好不好？好行，哇，这次是让你反过来去看哦，那我陪你好好看一看吧，好不好？好，来啊，那这里有饭团，说明说明。第二格的这个位置能不能有饭团呢？我点亮的位置不能，那这个位置能不能有饭团呢？也不能是吧，这两个位置都不能是吧？好，行，那什么位置可以放饭团呢？嗯，那你就好好观察，再结合第一个好好试一试，好不好？来啊，慢慢看啊。又太简单了，那你要仔细哦。 为什么呢？因为老师刚刚刚刚帮你看的是第三个嘛，那你看第一个，第一个哪里有饭团，你就不能放啊。.小娇吗？看吗？看你还有一个空没填，看到没有？你还有第二行的题没有做呢。绿色的绿色的小赵，你是绿色的，没有甜。 小好啦好啦，看你是绿色的，没放呀，绿色的没放蓝色你已经放好了，你看到没有？你是绿色饭盒没放好。对，因为他。好，行，就是说哎你放了的位置你就不可以放了，你就都排除掉，是不是？好行来，那最后咱们继续前进了啊，走吧。打包食物啦。. 嗯，好的，来，那咱们把今天的内容好好看一看啊，下节课再继续闯关。嗯，小星星最后送我还没加满，对不对？等一下一起发。.B。.嗯，那还是要仔细哦，好不好？一定要认真的去看啊。对，把他们的规律都观察出来。你们在这里合影好不好？在这个位置合影吧，可以吗？可以。哎，我我看一下，我是不是挡着你们拿星星了，我是不是我是不是挡着你们拿星星雨了，能快拿快拿快拿。等一下再上来加满为止啊，还没满是吧？ 满了吧，满了哈，你哎只要有小朋友拿到50颗就已经算满了，就发不了谢星语了。对，已经很多了啊。好，今天作业认真完成好不好？认真分析。好，来，你们摆好姿势，我给你们咔一张咔嚓一张来摆个可爱的姿势。对，来哎。小周，你太逗了，我给你拍了一张很逗的照片，再来再来。好，还要换姿势吗？我再来来32。AK闪现快点，32看在哪里？一好，炸开到你了。行，然后好好完成任务啊，咱们下次见。对，照片拍的很不错，下课可以看一看好不好？嗯，好，那我们下课见，要跟爸爸妈妈认真分析啊，我们下次见喽，拜拜拜拜，嗯，认真玩啊。',
                           '那下午好，哦，白兔那边怎么突然变得黑黑的又差不多了。那老师先拿画笔给大家玩着，我去教星欣和君安他们。又有画笔玩了开不开心？.欢迎心雨。 是的，你可以画画。嗯，在等他们一分钟，他们还没到的话，我们就直接上课了。我先看一下大家的课前预热，还有上节课的课后题有没有做完啊。嗯，芝麻同学星语、白兔团圆做的非常好，都能拿到10颗星星。那我先将我们的任务星星发送过来。好啦，我们孙雨已经将整个画面都涂成黑色的了，老师收回来了啊，宝贝们。你们想看看大家的画面吗？想啊，白兔想看，你看这是团圆的这不是小白兔的。你看尺码的星语的，没有一个画面是干净的。好，静安宝贝，下午好。老师刚看了你的课前预热和课后题，今天也是满分哦，跟老师一起来看看今天投子的奥秘吧。.那我们就一起接受考验吧，看看大家能不能通过神奇投资的考验。我们先一起认识一下头子吧，大家看一看头子这是什么形状呀？哦，同学说是正方形，有宝贝说是正方体，它到底是一个平面扁扁的图形，还是一个立体，可以站高高的图形呀？对对，它是个立体的，叫做正方体。好，那谭圆你知道正方体有几个面吗？是的，没错，而且这6个面是什么形状呀？.嗯，是的，都是正方形的面，而且团员应该是预习过。所以他知道投资上面的点数呢有123456对吧？Yeah.非常好啊，那宝贝们记住啊，桃子的特征它是一个正方体，有6个面，每个面都是正方形的，并且它的点数有哪些呀？我们一起来读一下。点数有12345。6对吧？这就是我们的投资啦。那现在我们来想想第一个问题，他问二的对面是几？哎呦，心宇，你怎么知道的呀？哇，你预热做的这么好呀，表扬你啊，大家知道星宇同学说的这个知识吗？可能不太熟悉，我们先来想一下什么叫做相对面吧。白兔知道吗？什么叫做相对面？哎，你说的不是这个嗯，那你认识相对面吗？不认识呀，心宇认识相对面呀，你讲讲。嗯，对，就是他对面的非常好啊。GN。你认识过正方体的，你来想想看相对面是什么？哦，是的，一个面呢面对着另外一个面非常棒啊，我们可以拿着小手手来跟老师感受一下，每一个小手手放上面。像这样对对对，另外一个手纹摆它对面你来看就放在它的对面，像这样哦，所以上面的相对面就在哪？在下面对吧？你看下面的相对面就在。上面。没错，白兔同学都会举一反三了。我们像这样摆，你看左边的相对面就是右面，右面的相对面就是左面，看到没有？面对面，那像这样挨在一起，还叫做相对面吗？不是了，挨在一块的就不算了啊，那前面的相对面呢，你们知道吗？没错，团圆。嗯，是的，白兔新宇芝麻和俊安知道吗？团员和白兔都想到了，前面的相对面是。后面对以了，嗯不知道的时候可以拿着小手手，像这样一个手手放前面，另外一个手手放在它对面去就会发现啊它对面呢就是后面，那后面的相对面就是。简面非常棒。那现在我们来做这一道题，二的对面是几？我先把二给它找出来吧。哦，二现在在哪个面？在上面对吧？那它的对面就是下面。好，老师翻到下面，你们看下面是几5哈，二的对面是5。那三的对面呢，我们来看现在三在哪个面，C语答案正确啊，在左面对吧？那左面的相对面就是右面。好，来看右面，右面是几。4号最后一个六的对面是几数字6666在哪儿哦，在这在这儿我看到了。它在前面的话，那它的相对面就是后面翻到后面去哦，是几啊？一非常棒。那大家观察一下头子，把两个相对面的两个数加起来有什么规律吗？谁发现了桃子的相对面，这两个点数相加。哎，是的，这吗？你说说看。没错，头瓷的相对面点数相加都是等于7的对，非常好啊。大家看我们第一组二的对面是5，它们相加是不是等于7呀？那六的对面是16加1是不是几三的对面是43加4也是什么？也是7，所以我们的投资呀，它其实点数是有规律的啊，相对的面点数之和一定是7。那我们来玩一个抢答比赛。杨明明老师随便说一个点数，你们要快速的告诉我他对面的数字，所想挑战一下，看看谁速度快。好，心语想试试看。我们团员也想试试。好，芝麻同学。还有谁想参加吗？没有啦，白兔，就是举了没举啊，这个正在想，321想好了吗？好，来吧，那俊安要不要参加？俊安不参加，那就当我的小判官了。等会儿他们说答案，俊安，你要告诉我到底对不对啊，来，我们的判官就是俊安同学。做好准备哦，宝贝们，假如我是4，那我对面是正确吗？君安。今天你想想嗯，正确他给大家打对勾了。那再来一个，假如我是我是我是我是一。正确吗？娟好，再来一个，假如我是无。225加2等于7，太棒了。你们我给所有同学送三颗抢大小星星，你们做的非常好，等会做题就记住头子。投资人两个相对面点数之和，它是7啊。到大家啦。第一个问题，你看这一的对面是几呢？点方框写进去四的对面是几呢？填进去，这个很简单吧嗯。.今安其实不需要分投资的，我刚才不是学过吗？相对面的点数之和是7，那4加几等于7，它对面就是几？白兔，你不需要分投资的，我们就用刚才学习的小结论来做就好啦，4加2才等于6，对不对？要算一下啊，必须相加等于7才可以。 下一道题这道题呢老师先跟大家说一说，我们在方框中填入的是头子看不到的三个面上的点数。你看这条线。这条线指过来是不是问的是四点呀，是吗？嗯，不是，因为他说啦，我们找的是头子看不到的三个面，所以这条线这条线问的到底是左面还是后面呀？后面对后面看不到，那很奇怪了呀，我都看不到，还让我填什么呢？看不到怎么写啊，团员，你知道。心雨芝麻都知道藤园你说。对，2加上几等于7啊，因为我们刚学过相对面的和等于7，那他问后面后面看不到，我找它相对面就行了。我能看到它相对面是2，那就想想2加几能等于7呀。对，那这个位置我就知道它是5点。好，再来一个啊，大家看这条线，这条线问的应该是哪个面？是的，来非常好。对的，没错啊，来芝麻你说一说是哪个面呀？对，右面那右面看不到呀，我又没有透视眼怎么写呀？太棒了，老师相信大家是会做了的，注意看线条，指向的一定是看不到的面，看不到的话就找它的相对面，想一想，它们相加要等于7就可以。 星宇同学，还有芝麻宝贝这么快速的，恭喜萌逮兔。哦，团圆，你看你写武这个地方，是是是，想过来了，棒棒的啊。哇。发送我的小爱心给大家，怎么掌握的这么好呀。是的，我看到你做完了，能等一下俊安好不好？我发现俊安他会做题，他现在都没做错，只是他思考的时候呢，需要慢慢的去想。老师决定送大家一个红包。恭喜大家所有同学都做出来了。耶这么。 藤圆抢到5颗，我再给你送两颗星星，这样你有7颗星星了。芝麻和白兔也有7颗星星。俊安和星宇抢的多一些，抢到8颗星星。等会儿好好表现啊，题目做的好的话，再抢一次，想不想再玩一次啊，是哈，那我们已经进入这个神奇投资工厂啦。 让我们选择什么样的按钮呢？ 那我们先来看一看这个头子吧，头子原来上面是几点呀？5上面宝贝5啊四的话，它是前面，那我都知道上面是我了，我肯定能知道下面下面是几啊。2对好，现在老师呢翻转一次，你们看对，翻转一次上面是几6，下面呢？一、那老师接着翻转两次，上面变成了2，那下面是5。好，大家想一想翻转两次有没有什么发现呀？新宇，你又有什么发现呀？ 嗯，是的，就是得到了这个观察的结果，是不是？让大家看一看这个翻转后的结果有没有什么规律的，团员举手啦，你说。哦，第一次。 是的啊，团员呢他对比了一开始的样子和最终翻转两次的结果，发现了一个小秘密，就是原本呢上面是5，下面是2，翻转两次后呢，上面变成2，下面变成5了，是吧？大家看假如老师把中间翻转第一次的结果擦掉，那么直接观察一开始的样子和翻转两次的结果能看出来结论吗？你看是不是之前在下面的就被翻到上面去了，在上面的被翻到。下面了对不对呀？所以呢翻转两次找上面很好找，怎么找呀？就是原来的哪个面会被翻上去啊？对，原来的下面会被翻上去，原来的下面就朝上了。那现在我们来玩快速翻转小游戏。杨咪咪老师呢给出一个上面的点数，你们要告诉我翻转两次，上面会变成几。好，我看看谁来参加啊，谁有信心，这个有点难了哦，白兔同学新雨同学还有吗？芝麻要不要参加？不想要了呀。好吧，那这样子，刚才呢俊安不想参加，我让俊安当了一次判官，这次芝麻当判官吧。三位同学回答啊，哎，假如我的头子现在上面是三，那我要翻转两次，翻转完了上面会是几？我们让谭员再想一下答案啊。这个三就是我现在上面是三翻转两次了，问上面是几？因为我们刚学的就是说现在的下面会被翻到上面，上面是3，那下面就是它的相对面是4，所以四呢就会翻到上面去了啊。好，再来一次吧。假如老师的头子上面是一，那翻转两次后，上面是对对对对，正确正确。芝麻这一次的小判官都没有派上什么用场。但是的话老师有看到你马上给出了回应，对他们咱点了点头，是不是？然后现在题目交给大家自己做啦，别忘记翻转两次后，原来的下面会朝上哦。那我们选答案怎么选？你们看老师他这有娃娃，看到没有？我把这个娃娃呢放到这些按钮上，就代表你选择的答案。这一次上面是5，翻转两次，上面是几啊？想想上面是5翻转两次，上面是没错，2，因为上面是5，现在下面是2，翻转两次，下面就朝上了。..景安，你一直在做什么呀？镜头太晃了，你找个地方固定坐下来啊，认真做题。 腾云，我们刚才不是学过相对面吗？你现在能看到上面是4，那下面是几？哎，对位你要好好想，一步一步想，先把现在的下面想清楚，翻转两次，下面就会翻上来了。好的，只有我们小团员呢有一点点小失误，大家整体表现都特别好的，还是送一个红包，团员也做的特别棒。三道题只出现了一个小失误。 我们白兔同学加两颗星星有7颗了，团圆也是抢的怎么这么少呀？这三颗呢，我给你再加4颗，有7颗啊。芝麻抢的最多有8颗，俊安和心语是自己抢的，有7颗星星，我可以休息一下了，大家自由活动。休息吧，休息一分钟。没事，汤圆你可以休息啊，先能自己活动一会儿。 是吗？我回来啦。.哇，接下来这个神奇头子游戏可是有点难的了。 那一句话一句话来听啊，他说两个头子的相贴面点数之和是8新宇同学回答正确，速度很快。那第一句话，他说的相贴面是哪两个面呀？谁观察出来了，芝麻同学回答正确，芝麻和心雨自己想出答案了。哦，我们来看啊这个蓝色头子和白色头子是不是挨在一起了呀？看到没？那他们挨在一起的这两个面呢，就叫做相贴面，因为它们贴贴在一块儿了。对，贴在一起了啊。那静安今天上课啊，老师就发现你的小动作也太多了吧，一直在拿东西或者是走动，你认真上课哦，不要再晚了好吗？哎，白兔，你看看题目，告诉我们这两个相贴面的点数之和是几啊？对，这两个面的点数加起来等于8的啊。金宇，他告诉我们蓝色头子上面的点数是2，那它下面是几啊？5没错，二的对面是5，现在我们就要思考啦，既然蓝色头子下面是5，它和白色头子上面贴在一块儿，加起来又得等于8。那白色投子的上面是几呢？正确正确，芝麻生语答案正确啊，嗯白头可以大点声。汤圆想出来了吗？没有想到白兔想到了吗？想不到啊。是几啊？对了团圆哦，是的，白兔没错没错，静安同学有没有想到答案？是的，正确哇。。.是的，宝，这个过程挺完整的啊。因为我们第一环节和第二环节不是学过了吗？相对面的点数和是7。那我知道是蓝色头的上面是2，我们就用我们的7减掉已知的面，然后算出其中一个相贴面。那我们就知道了啊，其中这个面呢就是5点，然后呢再去用我们的相贴面，加上另外一个相贴面，等于相贴面的和来算，你看这两个面加起来，5加上一个不知道的点点必须要等于8。这就知道了啊，所以白色头子上面就是三屏幕交给大家了，你们试试看。.  好，老师收回来先讲一下心仪宝贝，你可以等一下大家啊，我已经送给你9颗小星星了。来，我从这一关开始讲第一句话，两个头子相贴面的点数之和是6，对不对？那我们先看这两个头子，哪些面贴在一起来，我们把它找出来，挨在一块儿的面，这叫做相贴面啊，这两个面贴在一块了，这一步能明白吗？然后这两个贴贴在一起的面点数的和呢加起来等于6。他告诉我们蓝色头子上面是4，那它下面是几3。四的对面是3啊，然后它和白色头子的上面不是贴在一块了吗？这两个相加呢又得等于6，那三加几等于6呀？对3加3等于6对吧？白色头子它这个上面呢就是三啦。大家先用我们刚才学习的相对面去看啊，你已经知道了上面是多少，那它下下面你就知道了呀，相对面是3，然后呢再用题目告诉我们的信息，这两个贴在一起的面点数加起来要等于6，对不对？那它和白色投资上面相加等于6的话，三加几等于6，这样去想一想。再做一道题，大家认真听题目信息。心雨，你可以把答填一下，自己跳到下一关，接着做就行。 心语老师提示你一下，这次题目他没有问你上面哦，你注意他问的是白色头子，下面的点是不是几？所以你要先知道白色头子的上面，对你要注意问题非常好，我就知道肯定是没注意问题是什么过程你全懂了满分了啊，今天。.芝马同学进步特别大，但是这一关你要注意问题，问题问的是白色头子下面的点数是几，人家没有问上面哦。.老师给大家送上10颗星星，我再收回来讲一讲题。表扬一下我们的团员、白兔，还有芝麻同学，其实进步特别特别大。老师看了大家做题，其实你们都掌握了的，只是最后这一关呀，没有注意问题。他问的是白色头子的下面的点数，没有问上面了啊，问的是白色头子的这个下面问这个面呢。嗯，静安老师收回来给你讲一下这一关啊。静安，你看看他告诉我们相贴面的点数之和是8，你拿画笔画一画。相贴面是哪两个面，它们加起来要等于8，你把贴在一起的面找到。对吧，群安其实会观察的呀，那他们相加不是要等于8吗？现在题目告诉你，蓝色投子左面是三了，你知道左面，那就能照它的右面，它右面就是几。你之前学习过相对面，相对面是几呀，俊呀。相对面的和是7，现在你已经知道其中一个面是3，你用总数减部分等于另外一个部分。所以这个蓝色投子的右面这是4。那它和白色头子贴在一块儿，白色头子的左面和它加起来啊，就是4再加上白色头子的左面要等于8。所以白色头子左面是几啊？4、明白了吗君安，你先用已经知道的面求出它的相对面，再用这两呃个相贴面的和去计算出另外一个相贴面。哎，这按这一关你来想想啊，你看他告诉我们相贴面的点数和是几？5、这两个面相加得等于5。然后他告诉你，当蓝色头子左面的点数是6，问你这个白色头子的左面，好问这个位置，君安想想怎么做？君安第一步，你都知道蓝色投子左面是缪了，那它右面就是几？对呀，它是一吧，你都知道这个面是一了，那白色头的左面和它挨在一块，他们相加又得等于5，所以白色头的左面就是几呀？ 知道了总数，也知道部分，求部分用减法5减1等于4。你要是不会想减法，你就去想啊，既样这是一，另外一个面和它贴在一块儿，让后它们相加又等于等于5，一加几等于5呢？你想一下加法算式也可以。嗯，最后一道题最后一道题的话，你们都会做，只不过呀忽略了问题啦。你看白色头子下面的点数，他告诉我们啦。来，这儿相贴面和是8，现在蓝色头子上面是4，那它下面是3。白色头子上面和它挨在一起，3加5等于8。我就知道白色头子的上面是5，那它下面呢就是白兔同学认真听哦。五的对面是几呀？2就算出来啦，看到没？四的对面是3，这两个面相加等于8。所以白色投资上面这就是5问它下面的话，你看五的对面就是二就算出来了。好了，今天的题目结束了。第三个环节有一点点难，尽量要加加油啊。.老师也祝福大家今晚可以做个美梦，我们要下课啦，现在要去做课后题哦，下节课也是记得先预热再进入教室，拜拜，再见，加油。',
                           '没到的朋友啊，现在做准备哦，看看小张开没有来是吧？做好准备。.好，行，来先给大家把心心奖励送一下。好，检查一下大家的预习。进教室的朋友预习都完成了，没问题。。再看一下作业，上一节课的作业，博轩是满分，开始满分，其他的小朋友都有错题，都有错题。请假了，没有来的朋友就是请假了。好，然后小明上一节课的错题还是偏多。小明，你要注意了。你最近几节课的作业出错都是比较多的。对吧对，改了，我知道。但你看上一节课的作业还是有出错，456三个题，2加4怎么会是9呢？2加4等于几啊？2加4等于6，你怎么会写9呢？4加5怎么会是零呢？我觉得你最近做作业要认真一点了，小明，你最近好。看到了小昭下课之前一起分享，拿来拍照。好，我来给大家送星星预习的星星，作业的星星，然后就是满分奖励。看和博轩的满分奖励。好，小呃洋洋做好了，让老师看到你，咱们出发喽。洋洋做好，让老师看到你任务。Yeah..大力熊力气好大呀，那我们一起来看看。 嗯，我们现在要拼出两个正方形，对，而且是尽可能少的火柴棒。好，那首先得把第一个正方形拼出来吧，对不对？你不管第二个怎么拼，你首先得把先把第一个正方形给放好，然后再考虑拼第二个正方形。那你想想看呀，你想要节省火柴棒，你是贴着这个正方形去继续放，还是就在别的地方去放呢嗯。I.贴着它放对吧？就是和它共用一根火柴棒，是不是就像这根火柴棒看宝贝，你看咱们就相当于是两个正方形背靠背嘛，所以咱们就这样贴着它去放，这样是不是就可以节省火柴棒啦，中间这根火柴棒是不是就共用了。对，这样就拼成功了呀。所以我们想要节省火柴棒，我们就得共用一些？斜边好，来继续按照要求来拼。.对，这次咱们要拼5个正方形，那你先拼两个出来好不好？举个手，先来一位朋友给我拼两个出来。行，小明很主动，那请你来试一下你。你先拼两个出来。对，好，你先把第一个拼出来。再顺着把第二个拼出来。来拉住火柴棒放上去，可以的。谢谢小明，小明已经帮我们拼好了两个正方形，那题目中的要求是5个呢，咱们继续拼好不好？行，来，那这次老师请小昭试一试吧，好不好？行，来，小昭也他前一关也一直再举手，没关系啦，都有机会来小昭试试。再拼出第三个正方形。嗯，可以的这是第三个。那你再拼第四个。第4个对，题目要求是拼5个哦，你还差一个你还差一个。嗯，可以的对，所以你拼了5个正方形，谢谢你哦。但是它不是最少的，谢谢小娇啊，很不错，你确实拼出来了5个，但是还可以更少一点。谁想试试呀？对，横着拼的话，好像嗯每一个5个都要拼出来。对我可以再减少一点，看一下试试是吧？来，那你继续修改，看怎样拼的话，能用最少的火柴棒。对，我有一个提示哦，每四个小正方形就可以变成一个大正方形。.呃，这样好行。那你跟他的方法是一样的嘛，只不过你是把上面的正方形改到下面来了呀。小凯，你是一样的方法呀，对不对呀？我觉得你们的方法没什么变化，谢谢你哦。那大家有没有想到每四个小正方形是能合成一个大正方形的呀。所以你可以考虑这样品。看到没？洋洋洋洋有在学习吗？洋洋有在学习吗？博轩有在学习吗？看到了吗？虽然我现在只搭出来了，我用火柴棒只摆了4个，但是其实这里是有5个正方形的。还有一个正方形藏在哪里？哪另外一边另外一边是什么意思，我不懂。你清清楚楚的说什么叫右边，哪里右边还有一个我没看到。对，大的正方形在哪里？在这里？对，因为每四个小的能合并成一个大的，所以这里有一个隐藏的大正方形。对，这样才是清清楚楚的5个正方形哦，明确了吗？明确了吗？这样你可以少拼一个，少搭一个，而且。你想想看，你刚刚如果横着拼的话，你只能共用一条边，对不对？我这样拼的话，我这条边还可以共用呢，对吧？我还可以多共用几条边呢？好，行，来，那接下来你的目标是什么呀？你要拼出，你要用1根火柴棒拼三个正方形哦，来吧，你来动手拼一拼。拼三个正方形。.嗯，看看你是不是十根火柴棒，自己数一数，拼三个就够了。洋洋不要多拼不要多拼呀。瑶瑶拼三个，你要认真，你怎么还继续拼呢？都可以。对，拼三个，你要听要求。好，来下面的要求是什么？认真听。好，交给你了。7根木条拼三个三角形。How.小明，你有三个三角形吗？洋洋，你火柴棒不够了，你只有7根火柴棒。对。我轩你已经用掉6根木条了，现在只剩最后一根木条可以用了。所以你要把其中一根木条改改位置呀，换换位置呀，小明尝试成功喽。看来你你都没有拼出三角形哟，你至少先把第一个三角形拼出来吧，然后呢。为什么嗨为什么你找不到思路呢？因为你没有。看为什么你找不到思路呢？因为你没有节省木条，你没有去共用第一个三角形的木条。杨岩也是，那现在还没有还没有拼出来的小朋友博轩听老师说。 那你要拼三角形，你肯定是先把第一个三角形搭出来，然后你要搭第二个三角形。那因为你要节省木条，你肯定是挨着第一个三角形去搭，对不对？是不是我问你对？是你要用，所以你要选一根木条，贴着它放记。去使用是吧？比如你选了这根木条，那你的脑袋现在就要想我要利用这根木条搭一个三角形，所以我应该怎么放剩下来的两根木条呢？明白了吗？你想继续使用这一根木条搭三角形，那你就要想我另外的两根木条怎么放呢？怎么放呢？好，我另外两根木条，我这样放行不行呢？好，可以，我这样放一根，怎么就不行了呢？我在这里放了一根木条之后，我剩下来一根木条放哪儿呢？嗯，放在上面不就可以了吗？这不就是一个三角形吗？是不是？那就可以了呀。那现在搭了两个三角形，还有一个三角形，那你又要想呀，我要利用已经有了的木条继续去搭三角形。所以我接下来的木棒怎么哎呦，这个不要拿走哈，我接下来的木棒怎么放呢？你继续用两根木棒把它拼好就可以了呀。没有成功的小朋友继续来把这个题订正，成功的小朋友，你可以再试试，好不？好，你可以再换一种方法试试，继续。刚刚没有搭成功的小朋友继续搭。对，然后我再顺着第二个三角形。划一个方向嘛，洋洋，你都没有搭成三角形，你有那么多方向的木棒可以用。 那就用第二根木棒，洋洋。对呀，然后继续搭这个重复了，那就换用用第三根木棒。可以呀，用第三好，用横着的木棒，洋洋。博轩好，这个用不行，重复了，换用第三根木棒。博轩第三根木棒。第三根好，是的，放上去，你还没有尝试，总是在放弃拿走拿走，把第三根木棒拿起来，放到右边。松手挨着那根木棒，挨着那根木棒松手。好，把横着的木棒拿过来。对，放上去这是不是三角形，是不是三个？对不对？一个挨着一个再挨着下一个放，是不是呀？就要大胆的去尝试呀。好，那我们接下来继续出发喽，好了。.好，那我们一起来看一看来听要求。嗯，大家听到了什么信息分享给老师，你看我都请上台啦，听到了就分享，你听到了什么嗯？非常棒，把四个正方形变成两个正方形，那怎么动火柴棒呢？坐好看坐好，小昭也是做好，那怎么动这个火柴棒呢？是增加还是拿走呢？听到了吗？好，行，谢谢你。所以就是拿走两根火柴棒，拿走两根火柴棒，让这里只剩下两个正方形。对，那大家好好想一想拿走哪里的火柴棒呢？可以动手试一试，你看老师拿走外边的两个火柴棒，这里还有几个三角形呀哦几个几个正方形啊，几个正方形呀。Yeah.三个吧，一个两个三个，所以说明老师拿走外边的火柴棒是不可以的对吧？就拿走外边的火柴棒不太好，所以我可以考虑拿走里面的火柴棒，对吧？谁想试试，拿走里面的火柴棒，好，行，来，那这次我就小转盘转起来好不好？都比较主动的话，我就。随机邀请来收抽中谁就是谁了。对，抽中谁就是谁。好，小明同学请上台来那。告诉老师告诉老师，我应该拿走哪里的火柴棒。对你来点一点，我要拿走中间的火柴棒。好，拿走了呃，稍等稍等来，那现在我来看看小明变出来的图形来，谢谢小明哦，大家一起看这是什么图形呀？这是什么图形？长方形，这个也是长方形。对，那是两个正方形吗？不是哦，我们要的是正方形，但现在它是长方形，那没有关系，咱们再调整调整，看来竖着拿走两个不行，直接横着拿走两个也不行。那想想怎么动这个火柴棒呢？怎么动这个火柴棒呢？好哇，这次不错，那行，这次看你举手了是吧？行，你最先举，我请你试试吧嗯。来，那你想拿走哪个火柴棒呢？哦，谢谢看那两个正方形在哪里呀？两个正方。看怎么啦怎么啦？那哎看看你刚刚拿走火柴棒之后，这里有几个正方形，咱们数数好不好？这是什么图形？这是什么图形？小张说这是正方形哦，这是什么图形？洋洋。也是正方形，那咱们成功了吗？博轩咱们成功了吗？博轩博轩博轩，我在喊你三声，没看到你，我就喊爸爸妈妈过来陪你了。好，是不是两个正方形？是的吧。对，上面不是的哟，上面这这是一个不规则的。不规则的形状，咱们不认识的形状，对吧？所以就是两个正方形，对吧？好。所以我们发现啦，就是如果你想把图形变少的话，你尽量就是在这种用这种公共的火柴棒明白吗？就是尽量拿走公用的火柴棒，不要去拿走这种边边上的火柴棒。对，因为我想最快的把它变少。那我们看看下面的要求是怎样的，好不好？好，来。.使图形变成两个三角形。两个三角形。对，就是你现在这里只能剩两个三角形，你看看这里现在有好多三角形呢，对吧？数一数有几个三角形，我看谁数对了，我看谁数对了。这里一个、2个、3个、4个。5个对，这里有5个正方形，所以你想三角形对，5个三角形。所以你想让它只剩两个的话，你一定一定要从中间拿火柴棒，你一定要拿他们公用的火柴棒。对你明不明白什么是公用火柴棒呀？我我给你举个例子吧，比如上面一个三角形。下面一个三角形，你你看它们中间的这样的一条边，就是一个公用火柴棒，发现了吗？对，公共边你说的很好，这样的就是公用火柴棒。所以老师给你的建议就是拿中间的这种公用火柴棒。但是你只能拿走两根，你想想看拿两哪两根好不好？拿走哪两根，你尽量是拿中间的这种公用火柴棒。来，我看看小赵怎么拿。.看到了，没问题。对，拿走公用的火柴棒，只能拿两。只能拿走两根。对，不要全部拿走。行，大家已经知道什么是公用的火柴棒啦，是不是？那接下来咱们再听一次要求，有新任务。只能拿走几根火柴吧。.只能拿走几根火柴吧。请你点击减少一根火柴棒，所以只能拿走一根火柴棒，只可以拿走一根火柴棒哦。来。.洋洋为什么不听规则，一直在瞎视？.博轩，你还是找不到大正方形吗？你到现在还是对大正方形不清楚吗？那你就看我跟你讲，我每一关都在给你画，你到现在还是不清楚吗？这是第一个正方形，这是第二个正方形，这是第三个正方形，不要忘记外圈最大的正方形。对，这才是第三个正方形。好，来，那我们现在要继续闯关了，看这是什么。。嗯。.来，那我们一起来破解。请你移动两根火柴棒，让小狗掉头。那我们来看一看小狗的头和尾巴在哪里，看到了吗？小狗的头是什么形状呀？小狗的头是什么形状？下后。看看对，就是这里的一个三角形，小狗的头是三角形，小狗的尾巴是一个火柴棒，对吧？那我们接下来就是说因为我们要让小狗掉头，所以。先动一下，所以你就是把它的头变成尾巴，把尾巴变成头就可以了。那老师来给你看看尾巴长什么样，你认真看哦，看到尾巴了吗？看到了吗？对，那这个尾巴在右边，那接下来咱们对，咱们要把尾巴换到左边去，所以是不是说明这一根火柴棒要留着，不能拿走呀？。是吧，所以我们已经确定了，这个就是小狗的尾巴，这个就是小狗的尾巴，咱们不能动它。然后这两根火柴棒就是小狗的头，这两根火柴棒就是小狗的头，看到了吧。那我们要好好看看小狗的这个尖尖的头，它是朝哪边的呢？它现在是朝朝哪边的呢？.很棒，小狗的头现在是朝向右边，是不是它是不是朝右边，所以咱们掉头的话，就得把小狗头朝向左边。对，咱们要把小狗头这样朝到左边来，看到了吧？所以有想法了吗？黑色的火柴棒留着不动当尾巴。另外两根火柴棒换位置放到老师。画的这个绿色线条的位置，因为它本来朝右，咱们现在得朝左看到了吗？你可以放吗？你现在可以放了吗？可以。来试一下，一根火柴棒不动当尾巴，另外两根火柴棒掉头。那就很好嘛。行，那博轩来帮一下洋洋吧。你对你来试着你你上台来做一下吧，你来帮帮滴滴。对，尾巴不动，另外两根小木棒不在这里，小狗头就变成功了。好，那接下来咱们还有任务哦，我们一起来看看。是只移动一根火柴棒，让小羊掉头。可以是吧，你知道啦，看到小羊的头和小羊的尾巴了吧，洋洋看到了吗？洋洋。小狗头小狗尾巴把狗头的火柴棒拿到尾巴那里去来试试。那还是挺不错的，可以的。这个做的很好，来接下来继续听要求。嗯，老师先给你看看叉子长什么样，来看到了吗？这个就是叉子，看到没有？对，这个叉子本来是朝左边的对吧？这两根这个是朝左边的那接下来你要动一下，动两根火柴棒，让它朝向右边。对，怎么样才能让他朝右呢？怎么样让他潮右呢？嗯，你知道吗？你这样直接动能不能成功，你这这样算成功了吗？这样算成功了吗？这样没算成功吧，对不对？那你看你看这样的话没算成功吧，因为只能动两根火柴棒，还有个小把手。对，还有个小把手没变出来呢，对不对？那怎么办？你可得好好想一想，你要非常明确的看到它变方向了才算成功哦，好不好？那你看老师刚刚动这两根的话，没成功呢。 那我们可不考以考虑动别的火柴棒呀，行不行呀？我刚刚动的那两根没成功的，你考虑一下，你能不能换别的火柴棒动呀，好不好？这两根不能再动喽，我刚刚都试过了，我没成功，你看到吗？对，所以你应该动剩下来的两根火柴棒来交给你了。洋洋，这个还没有哦，我没想要出来。太了差一点点博轩。它可以变它可以变方向，你拉到位置上去，它会自动转一下的。你是不是想把它竖着呀？对呀，你拉过去呀，你往左边拉，不是的，这根本就不是叉子的形状吧。对你拉到正确的位置上。他会自己转的，看到了吗？对，所以咱们怎么动呢？所以咱们把。把这两根拉到右边来，是不是这样是不是就成功啦，这样是不是就成功了？好，看看。对，一定要先观察嘛。好，行，那我现在给大家一个神秘任务，你来做一做，要听要求哦，点喇叭听要求哦，按要求来。点开始。.看到啦不错哟，洋洋，你做这个做的蛮好的哟，上课也要一起分析呀。老不跟我一起分析，就错过内容啦。哇，这么厉害。好了，老师收回了。所以我们刚刚知道了，我们学了，如果你想要使用最少的火柴棒拼图形，等一下嘛，等我们把这个方法学会好不好？今天咱们自己总结吧，如果你想用最少的火柴棒拼出图形，你就得挨着它拼，明白吗？你就得永远挨着你前面的图形去拼。对吧那如想如果你想最快的让图形变少，你就需要拿走公共边。你的注意力老是不在老师的画上，今天可以拿满分吗？今天可以拿满分吗？上节课只有两位朋友满分哦，对不对？那你就要拿走公共边，这样才能最快的去减少它，是不是？第三关怎么样的方法，观察头和尾巴呀，要好好看它的形状呀。好了，拿星星雨吧。对，认真解决问题，老师肯定会发的。好，宝贝继续前进吧。.好的，来总结一下今天的内容，看看快看。。嗯。 对，下课一定要好好分享哦，也要认真仔细的去做作业，来给你们拍张照吧。可以的，你摆好姿势，我等一下给你加星心。来321咔嚓。好，行，这张拍的不错嗯。等我在呢，你直接说请假了请假了，没有来的宝贝就是请假了。对，大家尽量每节课都按时来。是的，定下去啦，加不了了，因为已经拿满了，好好完成任务，好好完成任务。这样你下节课就可以拿更多的星星，好不好？那下次见喽，拜拜，快去完成任务，拜拜。拜拜宝贝们。']            
            success_count = 0
            skip_count = 0
            results = []
            
            # 遍历每个rank_asc，逐条处理
            for single_rank_asc in rank_asc_list:
                # 跳过已存在的数据
                if single_rank_asc in existing_rank_set:
                    skip_count += 1
                    results.append(f"rank_asc={single_rank_asc}: 已存在数据，跳过")
                    print(f"rank_asc={single_rank_asc} 已存在数据，跳过")
                    continue
                
                # 生成唯一的live_id
                live_id = int(time.time() * 1000000) + int(single_rank_asc)
                
                # 处理各字段：如果未指定则使用默认值或随机生成
                single_user_name = user_name if user_name else f'测试用户{random.randint(1000, 9999)}'
                single_brand_code = brand_code if brand_code else 'VIP_WanDou'
                single_lp_id = lp_id if lp_id else '667508'
                single_lp_name = lp_name if lp_name else random.choice(lp_names)
                single_teacher_id = teacher_id if teacher_id else '11698'
                single_teacher_name = teacher_name if teacher_name else random.choice(teacher_names)
                single_cate_sid = cate_sid if cate_sid else random.randint(1000, 9999)
                single_cate_stage = cate_stage if cate_stage else random.choice(stages)
                single_is_attend = is_attend if is_attend is not None and is_attend != '' else 1
                single_is_late = is_late if is_late is not None and is_late != '' else random.randint(0, 1)
                single_is_prepare = is_prepare if is_prepare is not None and is_prepare != '' else random.randint(0, 1)
                single_frontal_face_rate = frontal_face_rate if frontal_face_rate is not None and frontal_face_rate != '' else round(random.uniform(0.5, 1.0), 4)
                single_is_homework_submit = is_homework_submit if is_homework_submit is not None and is_homework_submit != '' else random.randint(0, 1)
                single_is_homework_correct = is_homework_correct if is_homework_correct is not None and is_homework_correct != '' else random.randint(0, 1)
                single_is_quick_answer = is_quick_answer if is_quick_answer is not None and is_quick_answer != '' else random.randint(0, 1)
                single_quick_answer_cnt = quick_answer_cnt if quick_answer_cnt is not None and quick_answer_cnt != '' else random.randint(0, 10)
                single_smile_rate = smile_rate if smile_rate is not None and smile_rate != '' else round(random.uniform(0, 0.5), 4)
                single_completion_rate = completion_rate if completion_rate is not None and completion_rate != '' else round(random.uniform(0.8, 1.2), 6)
                single_question_unlock_cnt = question_unlock_cnt if question_unlock_cnt is not None and question_unlock_cnt != '' else random.randint(3, 10)
                single_course_evaluate_score = course_evaluate_score if course_evaluate_score is not None and course_evaluate_score != '' else random.randint(3, 5)
                single_first_answer_true_rate = first_answer_true_rate if first_answer_true_rate is not None and first_answer_true_rate != '' else round(random.uniform(0.3, 1.0), 1)
                single_homework_true_rate = homework_true_rate if homework_true_rate is not None and homework_true_rate != '' else round(random.uniform(0.5, 1.0), 1)
                single_is_exit = is_exit if is_exit is not None and is_exit != '' else random.randint(0, 1)
                single_asr_content = asr_content if asr_content else random.choice(asr_contents)
                single_knowledge_point = knowledge_point if knowledge_point else random.choice(knowledge_points)
                
                # 插入SQL语句
                sql = """
                INSERT INTO dm_edu_com_lrn_user_live_f (
                    user_id, user_unification_id, user_name, brand_code, lp_id, lp_name,
                    live_id, start_datetime, teacher_id, teacher_name, cate_sid, cate_stage,
                    is_attend, is_late, is_prepare, frontal_face_rate, is_homework_submit,
                    is_homework_correct, is_quick_answer, quick_answer_cnt, smile_rate,
                    completion_rate, question_unlock_cnt, course_evaluate_score,
                    first_answer_true_rate, homework_true_rate, is_exit, asr_content,
                    knowledge_point, rank_asc, etl_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """
                
                params = (
                    user_id, user_unification_id, single_user_name, single_brand_code, single_lp_id, single_lp_name,
                    live_id, single_teacher_id, single_teacher_name, single_cate_sid, single_cate_stage,
                    single_is_attend, single_is_late, single_is_prepare, single_frontal_face_rate, single_is_homework_submit,
                    single_is_homework_correct, single_is_quick_answer, single_quick_answer_cnt, single_smile_rate,
                    single_completion_rate, single_question_unlock_cnt, single_course_evaluate_score,
                    single_first_answer_true_rate, single_homework_true_rate, single_is_exit, single_asr_content,
                    single_knowledge_point, single_rank_asc
                )
                
                # 执行插入
                row_count = mysql_conn.execute(sql, params)
                success_count += 1
                results.append(f"rank_asc={single_rank_asc}: 成功插入")
                print(f"成功插入数据: user_id={user_id}, user_unification_id={user_unification_id}, rank_asc={single_rank_asc}")
            
            del mysql_conn
            
            # 返回处理结果统计
            msg = f"处理完成: 成功插入{success_count}条, 跳过{skip_count}条已存在数据"
            return True, msg
            
        except Exception as e:
            print(f"插入数据失败: {str(e)}")
            return False, f"插入失败: {str(e)}"

if __name__ == '__main__':
    print("执行开始。。。。")
    choose_url = "test"
    external_user = 601348494
    open_class_time = '2025-09-21'
    # re = Dm_Script().cancel_user_demo_lessons("test", 2095639448)
    # re = Dm_Script().insert_user_live_f(choose_url, 123123,456456,1)
    print(re)
    print("执行结束88,")
