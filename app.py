#-*_coding:utf8-*-
# @Author  : yanling.fang
# @Time    : 2021-09-20

import flask
from flask import Flask, render_template, send_from_directory
from flask_caching import Cache

from ops.hualala_order.hualala_consume_hours import hualala_consume_hours
from ops.hualala_order.hualala_import_order import hualala_import_order
from ops.hualala_order.hualala_update_userinfo import hualala_update_userinfo
from ops.order.getSign_api import app_getSign_api
from ops.order.refund_order import app_order_refund
from ops.hualala_order.hualala_coming import hualala_coming
from ops.sms.icodeSms import app_icodeSms
from ops.order.orderV2 import app_order_V2
from ops.order.orderV1 import app_order_V1
from conf.readconfig import *
from ops.unbindWechat.unbindWechat import app_wandou_unbindWechat
from ops.wandou.wandou_coming import wandou_coming

app = Flask(__name__,template_folder='templates')
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

UPLOAD_FOLDER = rootPath() + "/docs/import_files"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 设置文件上传的目标文件夹


app.register_blueprint(app_order_V2,url_prefix='/order_V2')
app.register_blueprint(app_order_V1,url_prefix='/order_V1')
app.register_blueprint(app_icodeSms,url_prefix='/icode_sms')
app.register_blueprint(app_order_refund,url_prefix='/order_refund')
app.register_blueprint(hualala_coming,url_prefix='/hualala_coming')
app.register_blueprint(hualala_update_userinfo,url_prefix='/hualala_update_userinfo')
app.register_blueprint(hualala_consume_hours,url_prefix='/hualala_consume_hours')
app.register_blueprint(hualala_import_order,url_prefix='/hualala_import_order')
app.register_blueprint(wandou_coming,url_prefix='/wandou_coming')
app.register_blueprint(app_getSign_api,url_prefix='/getSign_api')
app.register_blueprint(app_wandou_unbindWechat,url_prefix='/wandou_unbindWechat')


@app.route('/favicon.ico')
def favicon(): 
    return send_from_directory(rootPath() + "/static", "favicon.ico")

@app.route('/')
def halloHtml():
    return render_template('index.html')


if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    # app.run(host='127.0.0.1', port=8088, debug=True, threaded=True, processes=1)
    app.run(host='10.200.13.188', port=8088, debug=True, threaded=True, processes=1)
