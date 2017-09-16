from flask import session

from models.user import User
import datetime
import redis
import pickle
import uuid


def current_user():
    uid = session.get('user_id', '')
    u = User.find_by(id=uid)
    if u is None:
        u = User.find_by(username='guest')
    return u


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    return token


class Conn_db():
    def __init__(self):
        # 创建对本机数据库的连接对象
        self.conn = redis.Redis(host='localhost', port=6379, db=0)

    def set(self, key, vaule):
        # 将数据 pickle.dumps，转化为二进制 bytes数据
        value_ = pickle.dumps(value)
        # 将数据存储到数据库
        self.conn.set(key, value_)

    def get(self, key):
        # 从数据库根据键（key）获取值
        value_ = self.conn.get(key)
        if value_ is not None:
            # 加载 bytes数据，还原为 python对象
            value = pickle.loads(value_)
            return value
        else:
            return {}   # 为 None(值不存在)，返回空列表

    # 生成 token 并储存
    def save_token(self, id, key='token'):
        token = new_csrf_token()
        tokens_dict = self.get(key)

        tokens_dict[token] = id
        # 将数据 pickle.dumps一下，转化为二进制 bytes数据
        tokens_dict_ = pickle.dumps(tokens_dict)
        # 将数据存储到数据库
        self.conn.set(key, tokens_dict_)

        return token

    # 删除 token 并储存
    def del_token(self, token, tokens_dict):
        tokens_dict.pop(token)
        self.set('token', tokens_dict)
