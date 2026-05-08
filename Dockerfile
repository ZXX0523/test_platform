# 基于的基础镜像
FROM python:3.7-slim

# 维护者信息
MAINTAINER yanling.fang

# 设置code文件夹是工作目录
WORKDIR /icode_test_platform

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
COPY . .

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


CMD ["gunicorn", "app:app", "-c", "./gunicorn.conf.py"]