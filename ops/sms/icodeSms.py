import json

import flask
from flask import render_template
from flask import Blueprint

from lib.py.icode_sms import Get_sms

app_icodeSms = Blueprint('icode_sms',__name__)

#查询验证码
@app_icodeSms.route('/icode/sms')
def icodeSms(filename=None):
    return render_template('sms/icodesms.html',filename=filename,htmlname="icodesms.html")

@app_icodeSms.route('/icode/getsms')
def get_icode_sms():
    choose_env = flask.request.values.get('choose_env')
    phone = flask.request.values.get('phone')
    Authorization = ''

    if phone == '': res = {"code":200,"msg":"请输入手机号","data":None}
    elif phone == 'undefined': res = {"code":200,"msg":"请选择查询环境","data":None}
    elif choose_env == '': res = {"code":200,"msg":"请选择查询环境","data":None}
    elif choose_env == 'undefined': res = {"code":200,"msg":"请选择查询环境","data":None}
    else:
        try:
            sms = Get_sms().run(choose_env,phone,Authorization)
            res = {"msg":"已获得验证码","code":200,"data":{"手机号：":phone,"发送内容：":sms[0]}}
        except KeyError as e:
            # 异常时，执行该块
         res = {"msg": "获取images失败", "code": 200, "data": e}
        pass
        return json.dumps(res, ensure_ascii=False)




