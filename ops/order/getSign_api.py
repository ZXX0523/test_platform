import json
from flask import request, json
import flask
from flask import Blueprint, render_template, request
from lib.py.getSign_api import  getSignApi

app_getSign_api = Blueprint('getSign_api',__name__)

@app_getSign_api.route('/getSign')
def getSign_apiHtml(filename=None):
    return render_template('order/getSign_api.html',filename=filename, htmlName="getSign_api.html")

@app_getSign_api.route('/getSignApi',methods=['POST'])
def getSign_api():
    # if flask.request.method == 'POST':
    data = request.get_data()
    json_data = json.loads(data.decode("UTF-8"))
    url_api = json_data.get("url_api")
    data_body = json_data.get("data")
    choose_env = json_data.get("choose_env")
    print("前端POST的chppse_env:", choose_env)
    print("前端POST的json:",json_data)
    print("后端获取前端传值url",url_api)
    print("后端获取前端传值data",data_body)
    # print("打印环境choose_env：",choose_env)
    # 输入校验
    if url_api == "":res = {"msg": "请输入url", "code": 200, "data": None}
    elif data_body== "":res = {"msg": "请输入接口请求体", "code": 200, "data": None}
    else:
        try:
            result = getSignApi().run(choose_env,url_api,data_body)
            if result['message'] == "操作成功":
                res = {"msg": "OK", "code": 200, "data": result}
            else:
                res = {"msg": "ERROR", "code": 200, "data": result}
        except KeyError as e:
            # 异常时，执行该块
             res = {"msg": "ERROR", "code": 200, "data": e}
        pass
        return json.dumps(res, ensure_ascii=False)
    # else:
    #     res = {"msg": "method is not allowed", "code": 500, "data": None}
    #     return json.dumps(res, ensure_ascii=False)



