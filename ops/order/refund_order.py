from os import error
import flask
from flask import Blueprint
from flask import render_template
import html

from lib.py.icode_script import icodeScript
from lib.py.order_V2_script import *
from lib.py.order_sku_V2_script import *
from lib.py.wandou_order_refund import RedundOrder

app_order_refund = Blueprint('order_refund', __name__)

# 导入V2课时包
@app_order_refund.route('/py/refund')
def refundOrderHtml(filename=None):
    return render_template('order/refundOrder.html', filename=filename, htmlName="refundOrder.html")

@app_order_refund.route('/py/refundOrder')
def refundOrder():
    choose_env = flask.request.values.get('choose_env')
    refundPrice = flask.request.values.get('refundPrice')
    orderNum = flask.request.values.get('orderNum')
    Authorization = ''
    print("打印环境choose_env：",choose_env)

    #输入校验
    if orderNum == "": res = {"msg": "请输入订单号", "code": 200, "data": None}
    elif refundPrice == "": res = {"msg": "请输入订单金额", "code": 200, "data": None}
    elif choose_env == "undefined":res = {"code": 200, "msg": "请选择查询环境", "data": None}
    else:
        try:
            result = RedundOrder().refun(orderNum, refundPrice,choose_env)
            if result['message'] == "操作成功":res = {"msg": "订单退款成功待审核", "code": 200, "data": result}
            else:
                res = {"msg": "订单退款失败", "code": 201, "data": result}
            # print("执行结果：",result)
            # res = {"msg": "订单退款成功", "code": 200, "data": {"订单号：": orderNum, "订单金额：": refundPrice}}
        except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "订单退款失败", "code": 201, "data": e}
        pass
    return json.dumps(res, ensure_ascii=False)