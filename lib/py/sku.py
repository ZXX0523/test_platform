from bin.runMySQL import mysqlMain

#添加套餐至数据库
def addSku_v1(course_type,sku_type,sku_id,sku_name,sku_price,env):
    #链接数据库
    sqlconnet = mysqlMain('MySQL-Database')
    sql = "INSERT INTO test_sku_info(course_type,sku_type,sku_id,sku_name,sku_price,env,status,source)VALUES(%s,%s,%s,%s,%s,%s,1,0)"
    rows = sqlconnet.execute(sql,(course_type,sku_type,sku_id,sku_name,sku_price,env))
    del sqlconnet
    if rows == "" or rows == 0:
        return {"msg": "添加套餐失败", "code": 201, "data": rows}
    else:
        return {"msg": "添加套餐成功", "code": 200, "data": rows}

#删除数据库套餐
def delSku_v1(sku_id):
    #链接数据库
    sqlconnet = mysqlMain('MySQL-Database')
    sql = "DELETE FROM test_sku_info WHERE sku_id=%s" % sku_id
    rows = sqlconnet.execute(sql,sku_id)
    del sqlconnet
    if rows == "" or rows == 0:
        return {"msg": "删除套餐失败", "code": 201, "data": rows}
    else:
        return {"msg": "删除套餐成功", "code": 200, "data": rows}


#
#
# if __name__ == '__main__':
#     # res = addSku_v1('2','2','31825221','口才自动化套餐1','0','1')
#     res = delSku_v1('234')
#     print("打印返回return内容：",res)

