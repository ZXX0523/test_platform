#!/usr/bin/env python
#-*_coding:utf8-*-

import mysql.connector
from mysql.connector import errorcode
from conf.readconfig import getConfig

class mysqlMain(object):
    def __init__(self,DB):
        # DB = "MySQL-Database"
        # DB = "MySQL-MeterSphere"
        config = {
            'host':getConfig(DB,"host"),
            'port':getConfig(DB,"port"),
            'database':getConfig(DB,"db"),
            'user':getConfig(DB,"user"),
            'password':getConfig(DB,"password"),
            'charset':getConfig(DB,"charset"),
            'auth_plugin':getConfig(DB,"auth_plugin"),
            'buffered': True
        }
        self.connection = mysql.connector.connect(**config)
        self.cursor = self.connection.cursor(dictionary=True)

    def __del__(self):
        for obj in ("cursor", "connection"):
            if hasattr(self, obj):
                try:
                    getattr(self, obj).close()
                except:
                    pass

    def execute(self, query, binds=(), get_last_row_id=False):
        self.cursor.execute(query, binds)
        self.connection.commit()
        if get_last_row_id:
            return self.cursor.lastrowid
        else:
            return self.cursor.rowcount

    def fetchall(self, query, binds=()):
        self.cursor.execute(query, binds)
        return self.cursor.fetchall()

    def fetchone(self, query, binds=()):
        self.cursor.execute(query, binds)
        return self.cursor.fetchone()