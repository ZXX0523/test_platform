import json

import flask
from flask import Blueprint, jsonify
from flask import render_template
from lib.py.hualala_update_userinfo import UpdateUserInfoRun

hualala_update_userinfo = Blueprint('hualala_update_userinfo', __name__)

# 导入V2课时包
@hualala_update_userinfo.route('/py/hualala_update_userinfo')
def hualalaUpdateUserinfoHtml(filename=None):
    return render_template('hualala_order/hualala_update_userinfo.html', filename=filename, htmlName="hualala_update_userinfo.html")

@hualala_update_userinfo.route('/py/hualalaUpdateUserinfo')
def hualalaUpdateUserinfo():
    choose_env = flask.request.values.get('choose_env')
    # refundPrice = flask.request.values.get('refundPrice')
    userid = flask.request.values.get('mobile')
    print("打印环境choose_env：",choose_env)

    #输入校验
    # elif refundPrice == "": res = {"msg": "请输入订单金额", "code": 200, "data": None}
    if userid == "" :
        res = {"msg": "请输入手机号", "code": 200, "data": None}
    elif choose_env == "undefined" :
        res = {"code": 200, "msg": "请选择查询环境", "data": None}
    else:
        try:
            res = UpdateUserInfoRun().UpdateUserInfo(userid,choose_env)
            # if result[0]:
            #     res = {"修改成功",result}
            # else:
            #     res = {"修改失败",result}
        except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "出错了", "data": e}
        pass
    # re=list(res)
    return json.dumps(res, ensure_ascii=False)