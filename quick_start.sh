#!/bin/bash

# Linux快速部署

if ! type git >/dev/null 2>&1; then
    echo 'git 未安装';
    apt-get install git;
    yum install git;
else
    echo 'git 已安装';
fi

if ! type docker >/dev/null 2>&1; then
    echo 'docker 未安装';
    curl -sSL https://get.daocloud.io/docker | sh;
else
    echo 'docker 已安装';
fi

cd ~/;
sudo systemctl start docker;
#git config --system --unset credential.helper;
git config --global credential.helper store;

if [[ -d ~/icode_test_platform ]];then
    echo "pull";
    cd icode_test_platform;
    git pull;
else
    echo "clone";
    git clone https://gz-gitlab.vipthink.cn/xuwei.fan/icode_test_platform.git;

fi

cd ~/icode_test_platform;
flaskID=`sudo docker ps | grep testflask | awk '{print $1}'`;

if [ $flaskID ]; then
  sudo docker stop $flaskID;
fi

sudo docker build -t 'testflask' .;
sudo docker run -d -p 8003:8003 testflask;
sudo echo y | docker system prune;