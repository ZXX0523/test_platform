from os import error
import flask
from flask import Blueprint
from flask import render_template
import html

from lib.py.icode_script import icodeScript
from lib.py.order_V2_script import *
from lib.py.order_sku_V2_script import *
from lib.py.sku import *

app_order_V2 = Blueprint('order_V2', __name__)


# 导入V2课时包
@app_order_V2.route('/py/order')
def orderV2PackgeHtml(filename=None):
    return render_template('order/orderImportV2Package.html', filename=filename, htmlName="orderImportV2Package.html")

# V2订单导入报名
@app_order_V2.route('/py/orderImportV2Package', methods=['get'])
def orderImportPackageScriptV2():
    errorList = []
    # global res
    nameList = flask.request.values.get('nameList').split(",")
    area_codeList = flask.request.values.get('area_codeList').split(",")
    phoneList = flask.request.values.get('phoneList').split(",")

    choose_url = flask.request.values.get('choose_url')
    sku_id = flask.request.values.get('sku_id')
    sku_price = flask.request.values.get('sku_price')
    channel_id = flask.request.values.get('channel_id')

    # 输入校验
    if phoneList[0] == "":res = {"msg": "需至少添加一行数据导入", "code": 200, "data": None}
    else:
        if choose_url not in ["pro","test","pre"]: choose_url = "test"
        else:choose = choose_url
        result = orderImportPackageV2().run(choose,nameList,area_codeList,phoneList,sku_id,sku_price,channel_id)
        if result[0] is False:res = {"msg":"导入失败","code":200,"data":result[1]}
        elif choose_url == "pro":
            for phone in phoneList:
                change = icodeScript().changeTest(choose,phone)
                if change[0] is False: errorList.append(phone)
            res = {"msg":"导入成功","code":200,"data":{"result":result[1],"toTestFail":errorList}}
        else:
            res = {"msg":"导入成功","code":200,"data":result[1]}

    return json.dumps(res,ensure_ascii=False)

# 查询sku记录
@app_order_V2.route('/py/orderCheckSkuV2', methods=['get'])
def orderCheckeSkuV2():
    env = flask.request.values.get('env')
    type = flask.request.values.get('type')
    if env == 'test':env_condition = " AND env = 1"
    elif env == 'pro'or env == 'gray':env_condition = " AND env = 2"
    elif env == 'pre':env_condition = " AND env =3"
    else:env_condition = ""
    if type == 'undefinde':type_condition = ""
    else:type_condition = " AND course_type = "+str(type)
    sqlconnet = mysqlMain('MySQL-Database')
    sql_search_course = "SELECT env,course_id,course_name,course_type,sku_id,sku_name,sku_price FROM `qa_platform`.`test_sku_info` WHERE 1 = 1 and sku_type=2 {0}{1};".format(env_condition, type_condition)
    sql_data = sqlconnet.fetchall(sql_search_course)
    del sqlconnet
    res = {"msg":"Success","code":200,"data":sql_data}
    return json.dumps(res,ensure_ascii=False)

# 创建sku
@app_order_V2.route('/py/orderCreatSkuV2', methods=['get'])
def orderCreatSkuPackageV2():
    choose = "test"
    course_id = flask.request.values.get('course_id')
    course_name = flask.request.values.get('course_name')
    course_type = flask.request.values.get('course_type')
    sku_name = "icode_auto_test-"+str(course_type)+"-"+str(course_id)
    print(sku_name)
    if course_id == "":res = {"msg": "请输入course_id", "code": 200, "data": None}
    elif course_name == "":res = {"msg": "请输入course_name", "code": 200, "data": None}
    elif course_type == "":res = {"msg": "请输入course_type", "code": 200, "data": None}
    else:
        sku = orderCreatSkuV2().run(choose, None, course_id, course_name, course_type, sku_name)
        if sku[0] is True:res = {"msg":sku[1],"code":200,"data":{"skuId":sku[2],"skuPrice":sku[3]}}
        else:res = {"msg":"套餐创建失败","code":200,"data":sku[1]}
    return json.dumps(res,ensure_ascii=False)

# 导入sku
@app_order_V2.route('/py/orderInstallSku', methods=['post'])
def orderInstallSkuV2():
    course_id = flask.request.values.get('course_id')
    course_name = flask.request.values.get('course_name')
    course_type = flask.request.values.get('course_type')
    sku_id = flask.request.values.get('sku_id')
    sku_name = flask.request.values.get('sku_name')
    env = flask.request.values.get('env')
    sqlconnet = mysqlMain('MySQL-Database')
    sql_sku_info = "INSERT INTO `qa_platform`.`test_sku_info`" \
                      "(`course_id`, `course_name`, `course_type`, `sku_id`, `sku_name`, `sku_price`, `env`, `source`) " \
                      "VALUES (%d, %s, %d, %d, %s, 0.01, %d, 2);"
    value = (course_id,str(course_name),course_type,sku_id,sku_name,env)
    sql_data = sqlconnet.fetchall(sql_sku_info,value)
    del sqlconnet
    res = {"msg":"套餐已导入","code":200,"data":sql_data}
    return json.dumps(res,ensure_ascii=False)

#添加套餐到数据库
@app_order_V2.route('py/create_addSku/V2', methods=['get'])
def addSku_api():
    sku_env = flask.request.values.get('env')
    course_type = flask.request.values.get('course_type')
    sku_type = 2
    sku_id = flask.request.values.get('sku_id')
    sku_name = flask.request.values.get('sku_name')
    sku_price = flask.request.values.get('sku_price')
    print("sku_env:",sku_env)
    print("course_type:",course_type)
    print("sku_id：",sku_id)
    print("sku_type:",sku_type)
    print("sku_name:",sku_name)
    print("sku_price:",sku_price)

    # 输入校验
    if sku_id == "":
        res = {"msg": "请输入套餐id", "code": 200, "data": None}
    elif sku_name == "":
        res = {"msg": "请输入套餐名称", "code": 200, "data": None}
    else:
        try:
            result = addSku_v1(course_type,sku_type,sku_id,sku_name,sku_price,sku_env)
            print("打印添加套餐执行结果：",result)
            if result['msg'] == "添加套餐成功":
                res =  result
            else:
                res = result
        except KeyError as e:
            # 异常时，执行该块
            res = {"msg": "添加套餐失败", "code": 201, "data": e}
        pass
    return json.dumps(res,ensure_ascii=False)

