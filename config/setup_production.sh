#!/usr/bin/env bash

# 换成 root 用户运行
sudo su
# 装依赖
apt-get update
apt-get install -y supervisor git zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
apt-get install -y python3-pip nginx mongodb ufw
pip3 install -U pip setuptools wheel
pip3 install flask pymongo gunicorn

# ufw
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 8388
ufw default deny incoming
ufw default allow outgoing
ufw status verbose
ufw enable

# 删掉 nginx default 设置
rm -f /etc/nginx/sites-enabled/*
rm -f /etc/nginx/sites-available/*

# 建立一个软连接
ln -s -f /root/Forum/config/Forum.conf /etc/supervisor/conf.d/Forum.conf
# 不在 sites-available 里面放任何东西
ln -s -f /root/Forum/config/Forum.nginx /etc/nginx/sites-enabled/Forum
chmod o+rx /root
chmod -R o+rx /root/Forum

service supervisor restart
service nginx restart

echo 'setup_production success'
