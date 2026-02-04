import json

import flask
from flask import Blueprint
from flask import render_template

from lib.py.dm_script import Dm_Script

dm_gubi = Blueprint('dm_gubi', __name__)


# 导入V2课时包
@dm_gubi.route('/py/dm_gubi')
def UpdateUserOpenclasstimeHtml(filename=None):
    return render_template('dm/dm_gubi.html', filename=filename, htmlName="dm_gubi.html")


@dm_gubi.route('/py/update_user_openclasstime')
def update_user_openclasstime():
    choose_env = flask.request.values.get('choose_env')
    userid = flask.request.values.get('userid')
    opencourseday = flask.request.values.get('opencourseday')

    print("打印环境choose_env：", choose_env, userid, opencourseday)

    # 输入校验
    if userid == "undefined":
        res = {"code": 200, "msg": "请选择进线环境", "data": None}

    if opencourseday == "undefined":
        res = {"code": 200, "msg": "请输入开课日", "data": None}
    else:
        try:
            res = Dm_Script().UpdateUserOpenclasstime(choose_env,userid,opencourseday)
            print(res)
        except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "处理失败", "code": 201, "data": e}
        pass

    return json.dumps(res, ensure_ascii=False)
@dm_gubi.route('/py/delete_conversation')
def delete_conversation():
    seat_wechatid = flask.request.values.get('seat_wechatid')
    user_wechatname = flask.request.values.get('user_wechatname')
    subject_id = flask.request.values.get('subject_id')
    clear_wechat_data = flask.request.values.get('clear_wechat_data')
    # 输入校验
    try:
        res = Dm_Script().dm_wechat_script_all(seat_wechatid, user_wechatname, subject_id, clear_wechat_data)
        # print("123123123")
        print(res)
    except KeyError as e:
        # 异常时，执行该块
        res = {"msg": "处理失败", "code": 201, "data": e}
    pass
    print(json.dumps(res, ensure_ascii=False))
    return json.dumps(res, ensure_ascii=False)
@dm_gubi.route('/py/insert_chat_data')
def insert_chat_data():
    env = flask.request.values.get('env')
    user_id = flask.request.values.get('user_id')
    external_user_id = flask.request.values.get('external_user_id')
    data_str = flask.request.values.get('data_str')
    brand_code = flask.request.values.get('brand_code')
    # 输入校验
    try:
        res = Dm_Script().insert_user_chat_data(env, user_id,external_user_id, data_str, brand_code)
        print(res)
    except KeyError as e:
        # 异常时，执行该块
        res = {"msg": "处理失败", "code": 201, "data": e}
    pass
    print(json.dumps(res, ensure_ascii=False))
    return json.dumps(res, ensure_ascii=False)
@dm_gubi.route('/py/update_course_finished_status')
def update_course_finished_status():
    env = flask.request.values.get('env')
    user_id = flask.request.values.get('user_id')
    finished = flask.request.values.get('finished')
    try:
        res = Dm_Script().update_course_finished_status(env, user_id,finished)
        print(res)
    except KeyError as e:
        # 异常时，执行该块
        res = {"msg": "处理失败", "code": 201, "data": e}
    pass
    print(json.dumps(res, ensure_ascii=False))
    return json.dumps(res, ensure_ascii=False)

@dm_gubi.route('/py/update_go_pk_record')
def update_go_pk_record():
    env = flask.request.values.get('env')
    user_id = flask.request.values.get('user_id')
    win = flask.request.values.get('win')
    lose = flask.request.values.get('lose')
    try:
        res = Dm_Script().update_go_pk_record(env, user_id,win,lose)
        print(res)
    except KeyError as e:
        # 异常时，执行该块
        res = {"msg": "处理失败", "code": 201, "data": e}
    pass
    print(json.dumps(res, ensure_ascii=False))
    return json.dumps(res, ensure_ascii=False)

@dm_gubi.route('/py/delete_review_record')
def delete_review_record():
    env = flask.request.values.get('env')
    user_id = flask.request.values.get('user_id')
    try:
        res = Dm_Script().delete_review_record(env, user_id)
        print(res)
    except KeyError as e:
        # 异常时，执行该块
        res = {"msg": "处理失败", "code": 201, "data": e}
    pass
    print(json.dumps(res, ensure_ascii=False))
    return json.dumps(res, ensure_ascii=False)

@dm_gubi.route('/py/cancel_user_demo_lessons')
def cancel_user_demo_lessons():
    env = flask.request.values.get('env')
    wandou_id = flask.request.values.get('wandou_id')
    try:
        res = Dm_Script().cancel_user_demo_lessons(env, wandou_id)
        print(res)
    except KeyError as e:
        # 异常时，执行该块
        res = {"msg": "处理失败", "code": 201, "data": e}
    pass
    print(json.dumps(res, ensure_ascii=False))
    return json.dumps(res, ensure_ascii=False)

@dm_gubi.route('/py/delete_help_util_userinfo')
def delete_help_util_userinfo():
    env = flask.request.values.get('env')
    user_id = flask.request.values.get('user_id')
    try:
        res = Dm_Script().delete_help_util_userinfo(env, user_id)
        print(res)
    except KeyError as e:
        # 异常时，执行该块
        res = {"msg": "处理失败", "code": 201, "data": e}
    pass
    print(json.dumps(res, ensure_ascii=False))
    return json.dumps(res, ensure_ascii=False)