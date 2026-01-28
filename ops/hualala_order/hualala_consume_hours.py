import json

import flask
from flask import Blueprint, jsonify
from flask import render_template
from lib.py.hualala_consume_hours_all import UserConsumeHoursRun

hualala_consume_hours = Blueprint('hualala_consume_hours', __name__)

# 导入V2课时包
@hualala_consume_hours.route('/py/hualala_consume_hours_all')
def hualalaConsumeHoursHtml(filename=None):
    return render_template('hualala_order/hualala_consume_hours.html', filename=filename, htmlName="hualala_consume_hours.html")

@hualala_consume_hours.route('/py/hualalaConsumeHoursAll')
def hualalaConsumeHours():
    choose_env = flask.request.values.get('choose_env')
    userid = flask.request.values.get('user_id')
    course_type = flask.request.values.get('course_type')
    print("打印环境choose_env：",choose_env)

    #输入校验
    if userid == "" :
        res = {"msg": "请输入学员id", "code": 200, "data": None}
    elif choose_env == "undefined" :
        res = {"code": 200, "msg": "请选择查询环境", "data": None}
    elif course_type == "undefined" :
        res = {"code": 200, "msg": "请选择课程类型", "data": None}
    else:
        try:
            res = UserConsumeHoursRun().run(choose_env,userid,course_type)
        except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "出错了", "data": e}
        pass
    # re=list(res)
    return json.dumps(res, ensure_ascii=False)