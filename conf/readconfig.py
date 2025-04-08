
from configparser import ConfigParser
import os,stat,platform

project_name = "icode_test_platform"
host_window = r"C:\Windows\System32\drivers\etc\\"[:-1]
host_linux = r"/etc/"


def getConfig(sysname,key):
    ini_file = "/config.ini"
    cfg = ConfigParser()
    # 读取文件内容
    cfg.read(os.path.split(os.path.realpath(__file__))[0] + ini_file, encoding="utf-8")
    return eval(cfg.get(sysname,key))

#获取项目根目录
def rootPath():
    curPath = os.path.abspath(os.path.dirname(__file__))
    rootPath = curPath[:curPath.find(project_name)+len(project_name)]
    return rootPath


def filePath():
    # curPath = os.path.abspath(os.path.dirname(__file__))
    # rootPath = curPath[curPath.find(project_name)+len(project_name):]
    curPath = os.path.split(os.path.realpath(__file__))[0]
    return curPath




