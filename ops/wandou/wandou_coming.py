from os import error
import flask
from flask import Blueprint
from flask import render_template
import html

from lib.py.wandou_coming_user import WanDouUserComingRun
from lib.py.icode_script import icodeScript
from lib.py.order_V2_script import *
from lib.py.order_sku_V2_script import *
from lib.py.wandou_order_refund import RedundOrder

wandou_coming = Blueprint('wandou_coming', __name__)

# 导入V2课时包
@wandou_coming.route('/py/wandou_coming')
def wandouComingHtml(filename=None):
    return render_template('wandou/wandou_coming.html', filename=filename, htmlName="wandou_coming.html")

@wandou_coming.route('/py/WandouComing')
def UserComing():
    choose_env = flask.request.values.get('choose_env')
    # refundPrice = flask.request.values.get('refundPrice')
    choose_type = flask.request.values.get('choose_type')
    mobile = flask.request.values.get('mobile')
    choose_subject = flask.request.values.get('choose_subject')
    coming_number = flask.request.values.get('coming_number')
    areaCode = flask.request.values.get('areaCode')
    TransferId = flask.request.values.get('transfer_id')

    Authorization = ''
    print("打印环境choose_env：",choose_env,choose_type,mobile)

    #输入校验
    if choose_env == "undefined":res = {"code": 200, "msg": "请选择进线环境", "data": None}
    if choose_type == "undefined":res = {"code": 200, "msg": "请选择进线类型", "data": None}

    else:
        # try:
        #     result = WanDouUserComingRun().UserComingRuning(choose_env,choose_type,mobile,choose_subject,coming_number,areaCode)
        #     if result[1]['data']['res'] == 1:
        #         res = {"msg": "进线成功", "data": result[0]}
        #     else:
        #         res = {"msg": "进线失败", "data": result}
        # except KeyError as e:
        #     # 异常时，执行该块
        #     res = {"msg": "进线失败", "code": 201, "data": e}
        # pass
        try:
            result = WanDouUserComingRun().UserComingRuning(choose_env,choose_type,mobile,choose_subject,coming_number,areaCode,TransferId)
            print(result)
            if result[1] == "查询不到转介绍上级学员的平台id，学员进线失败！":
                res = {"msg": "进线失败", "data": result[1]}
            elif result[1]['data']['res'] == 1:
                res = {"msg": "进线成功", "data": result[0]}
            else:
                res = {"msg": "进线失败", "data": result}
            # print("执行结果：",result)
            # res = {"msg": "订单退款成功", "code": 200, "data": {"订单号：": orderNum, "订单金额：": refundPrice}}
        except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "进线失败", "code": 201, "data": e}
        pass
    # return res
    return json.dumps(res, ensure_ascii=False)

@wandou_coming.route('/py/UpdateChannel')
def WandouUpdateChannel():
    choose_env = flask.request.values.get('choose_env')
    channel_id = flask.request.values.get('channel_id')
    try:
            res = WanDouUserComingRun().listChannels(choose_env,channel_id)

    except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "出错了", "data": e}
    pass
    # re=list(res)
    return json.dumps(res, ensure_ascii=False)