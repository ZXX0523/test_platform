import json

import flask
from flask import Blueprint, jsonify
from flask import render_template

from lib.py.hualala_applystandardcourser import ApplyStandardCourserRun
from lib.py.hualala_update_userinfo import UpdateUserInfoRun

hualala_import_order = Blueprint('hualala_import_order', __name__)

# 导入V2课时包
@hualala_import_order.route('/py/refund')
def hualalaImportOrderHtml(filename=None):
    return render_template('hualala_order/hualala_import_order.html', filename=filename, htmlName="hualala_import_order.html")

@hualala_import_order.route('/py/hualalaImportOrder')
def hualalaImportOrder():
    choose_env = flask.request.values.get('choose_env')
    mobile = flask.request.values.get('mobile')
    sku_id = flask.request.values.get('sku_id')
    marketing_id = flask.request.values.get('marketing_id')
    coupon_id = flask.request.values.get('coupon_id')
    package_type = flask.request.values.get('package_type')
    print("打印环境choose_env：",choose_env)

    #输入校验
    # elif refundPrice == "": res = {"msg": "请输入订单金额", "code": 200, "data": None}
    if mobile == "" :
        res = "请输入手机号"
    elif sku_id == "" :
        res = "请输入套餐id"
    elif marketing_id == "" :
        res ="请输入活动id"
    elif choose_env == "undefined" :
        res ="请选择查询环境"
    else:
        try:
            if package_type == "apply":
                res = ApplyStandardCourserRun().run(choose_env,mobile,sku_id,marketing_id)
            else:
                res = ApplyStandardCourserRun().submit_renewal(choose_env,mobile,sku_id,marketing_id,coupon_id)
                print("续费结果")
                print(res)
        except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "出错了", "data": e}
        pass
    # re=list(res)
    return json.dumps(res, ensure_ascii=False)

@hualala_import_order.route('/py/hualalaSelectApplyStandardCourse')
def SelectApplyStandardCourse():
    choose_env = flask.request.values.get('choose_env')
    choose_sku_id = flask.request.values.get('choose_sku_id')
    choose_tools = flask.request.values.get('choose_tools')
    try:
            res = ApplyStandardCourserRun().select_applystandercourse(choose_env,choose_sku_id,choose_tools)

    except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "出错了", "data": e}
    pass
    # re=list(res)
    return json.dumps(res, ensure_ascii=False)

