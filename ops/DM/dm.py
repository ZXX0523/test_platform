import json

import flask
from flask import Blueprint
from flask import render_template
from urllib.parse import unquote

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
    env = flask.request.values.get('env')
    seat_wechatid = flask.request.values.get('seat_wechatid')
    user_wechatname = flask.request.values.get('user_wechatname')
    subject_id = flask.request.values.get('subject_id')
    clear_wechat_data = flask.request.values.get('clear_wechat_data')
    # 输入校验
    try:
        res = Dm_Script().dm_wechat_script_all(env, seat_wechatid, user_wechatname, subject_id, clear_wechat_data)
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
    data_str = unquote(flask.request.args.get('data_str'))

    env = flask.request.values.get('env')
    user_id = flask.request.values.get('user_id')
    external_user_id = flask.request.values.get('external_user_id')
    # data_str = flask.request.values.get('data_str')
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
    finished_2 = flask.request.values.get('finished_2')
    try:
        res = Dm_Script().update_course_finished_status(env, user_id,finished,finished_2)
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

@dm_gubi.route('/py/clear_learning_situation_data')
def clear_learning_situation_data():
    env = flask.request.values.get('env')
    student_id = flask.request.values.get('student_id')
    node_types = flask.request.values.get('node_types')
    try:
        res = Dm_Script().clear_learning_situation_data(env, student_id, node_types)
        print(res)
    except KeyError as e:
        res = {"msg": "处理失败", "code": 201, "data": e}
    pass
    print(json.dumps(res, ensure_ascii=False))
    return json.dumps(res, ensure_ascii=False)

@dm_gubi.route('/py/insert_dm_edu_com_lrn_user_live_f')
def insert_dm_edu_com_lrn_user_live_f():
    user_id = flask.request.values.get('user_id')
    user_unification_id = flask.request.values.get('user_unification_id')
    rank_asc = flask.request.values.get('rank_asc')
    is_delete = flask.request.values.get('is_delete')
    is_update = flask.request.values.get('is_update')
    user_name = flask.request.values.get('user_name')
    brand_code = flask.request.values.get('brand_code')
    lp_id = flask.request.values.get('lp_id')
    lp_name = flask.request.values.get('lp_name')
    teacher_id = flask.request.values.get('teacher_id')
    teacher_name = flask.request.values.get('teacher_name')
    cate_sid = flask.request.values.get('cate_sid')
    cate_stage = flask.request.values.get('cate_stage')
    is_attend = flask.request.values.get('is_attend')
    is_late = flask.request.values.get('is_late')
    is_prepare = flask.request.values.get('is_prepare')
    frontal_face_rate = flask.request.values.get('frontal_face_rate')
    is_homework_submit = flask.request.values.get('is_homework_submit')
    is_homework_correct = flask.request.values.get('is_homework_correct')
    is_quick_answer = flask.request.values.get('is_quick_answer')
    quick_answer_cnt = flask.request.values.get('quick_answer_cnt')
    smile_rate = flask.request.values.get('smile_rate')
    completion_rate = flask.request.values.get('completion_rate')
    question_unlock_cnt = flask.request.values.get('question_unlock_cnt')
    course_evaluate_score = flask.request.values.get('course_evaluate_score')
    first_answer_true_rate = flask.request.values.get('first_answer_true_rate')
    homework_true_rate = flask.request.values.get('homework_true_rate')
    is_exit = flask.request.values.get('is_exit')
    asr_content = flask.request.values.get('asr_content')
    knowledge_point = flask.request.values.get('knowledge_point')
    
    try:
        res = Dm_Script().insert_dm_edu_com_lrn_user_live_f(
            user_id, user_unification_id, rank_asc,
            is_delete=is_delete, is_update=is_update,
            user_name=user_name, brand_code=brand_code, lp_id=lp_id, lp_name=lp_name,
            teacher_id=teacher_id, teacher_name=teacher_name, cate_sid=cate_sid, cate_stage=cate_stage,
            is_attend=is_attend, is_late=is_late, is_prepare=is_prepare, frontal_face_rate=frontal_face_rate,
            is_homework_submit=is_homework_submit, is_homework_correct=is_homework_correct,
            is_quick_answer=is_quick_answer, quick_answer_cnt=quick_answer_cnt, smile_rate=smile_rate,
            completion_rate=completion_rate, question_unlock_cnt=question_unlock_cnt,
            course_evaluate_score=course_evaluate_score, first_answer_true_rate=first_answer_true_rate,
            homework_true_rate=homework_true_rate, is_exit=is_exit, asr_content=asr_content,
            knowledge_point=knowledge_point
        )
        print(res)
    except KeyError as e:
        res = {"msg": "处理失败", "code": 201, "data": str(e)}
    except Exception as e:
        res = {"msg": f"处理失败: {str(e)}", "code": 201, "data": None}
    
    print(json.dumps(res, ensure_ascii=False))
    return json.dumps(res, ensure_ascii=False)