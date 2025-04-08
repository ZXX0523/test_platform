from os import error
import flask
from flask import Blueprint
from flask import render_template
import html

from lib.py.hualala_coming_user import UserComingRun
from lib.py.icode_script import icodeScript
from lib.py.order_V2_script import *
from lib.py.order_sku_V2_script import *
from lib.py.wandou_order_refund import RedundOrder

hualala_coming = Blueprint('hualala_coming', __name__)

# 导入V2课时包
@hualala_coming.route('/py/hualala_coming')
def hualalComingHtml(filename=None):
    return render_template('hualala_order/hualala_coming.html', filename=filename, htmlName="hualala_coming.html")

@hualala_coming.route('/py/UserComing')
def UserComing():
    choose_env = flask.request.values.get('choose_env')
    choose_type = flask.request.values.get('choose_type')
    mobile = flask.request.values.get('mobile')
    coming_number = flask.request.values.get('coming_number')
    areaCode = flask.request.values.get('areaCode')
    TransferId = flask.request.values.get('transfer_id')

    Authorization = ''
    print("打印环境choose_env：",choose_env,choose_type,mobile)

    #输入校验
    if choose_env == "undefined":res = {"code": 200, "msg": "请选择进线环境", "data": None}
    if choose_type == "undefined":res = {"code": 200, "msg": "请选择进线类型", "data": None}

    else:
        try:
            result = UserComingRun().UserComingRuning(choose_env,choose_type,mobile,coming_number,areaCode,TransferId)
            print(result)
            if result[1]=="查询不到转介绍上级学员的平台id，进线失败":
                res ={"msg": "进线失败", "data": result[1]}
            elif result[1]['data']['res'] == 1:
                res = {"msg": "进线成功", "data": result[0]}
            else:
                res = {"msg": "进线失败", "data": result}
        except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "进线失败", "code": 201, "data": e}
        pass
    return json.dumps(res, ensure_ascii=False)