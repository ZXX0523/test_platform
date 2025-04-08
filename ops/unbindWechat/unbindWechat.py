import json

import flask
from flask import render_template
from flask import Blueprint

from lib.py.wandou_unbindWechat import wandou_unbindWechat

app_wandou_unbindWechat = Blueprint('wandou_unbindWechat',__name__)

@app_wandou_unbindWechat.route('/wandou_unbindWechat')
def unbindWechatHtml(filename=None):
    return render_template('unbindWechat/unbindWechat.html',filename=filename,htmlname="unbindWechat.html")

@app_wandou_unbindWechat.route('/unbindWechat')
def unbindWechat():
    choose_env = flask.request.values.get('choose_env')
    openid = flask.request.values.get('openid')
    if openid == "":res = {"msg": "请输入openid", "code": 200, "data": None}
    else:
        try:

            result = wandou_unbindWechat().run(choose_env,openid)
            return json.dumps(result, ensure_ascii=False)
        except KeyError as e:
            # 异常时，执行该块
            result = {"msg": "微信解绑失败", "code": 201, "data": e}
        pass
        return json.dumps(result, ensure_ascii=False)


