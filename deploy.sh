# 代码更新
git pull

# 删掉 nginx default 设置
rm -f /etc/nginx/sites-enabled/*
rm -f /etc/nginx/sites-available/*

# 建立一个软连接
ln -s -f /root/forum/config/forum.conf /etc/supervisor/conf.d/forum.conf
# 不在 sites-available 里面放任何东西
ln -s -f /root/forum/config/forum.nginx /etc/nginx/sites-enabled/forum
chmod o+rx /root
chmod -R o+rx /root/forum
# 重启服务器
service supervisor restart
service nginx restart

echo 'deploy success'
