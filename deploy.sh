# 代码更新
git pull

# 删掉 nginx default 设置
rm -f /etc/nginx/sites-enabled/*
rm -f /etc/nginx/sites-available/*

# 建立软连接，supervisor 配置文件
ln -s -f /root/Forum/config/forum.conf /etc/supervisor/conf.d/forum.conf
# nginx 配置文件, 不在 sites-available 里面放任何东西
ln -s -f /root/Forum/config/forum.nginx /etc/nginx/sites-enabled/forum

# nginx 对静态文件权限
chmod o+rx /root
chmod -R o+rx /root/Forum

# 重启服务器
service supervisor restart
service nginx restart

echo 'deploy success'
