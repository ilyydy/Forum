from flask import session

from models.user import User
import datetime
import redis
import pickle
import uuid


def current_user():
    '''
    通过 session 获取当前登陆用户，
    返回 user 实例
    '''
    uid = session.get('user_id', '')
    u = User.find(uid)
    if u is None:        # 展示用，默认用 guest 登陆
        u = User.find_by(username='guest')
    return u


def new_csrf_token():
    '''
    返回 token 字符串
    '''
    token = str(uuid.uuid4())
    return token


class Conn_db():
    '''
    用来连接 Redis 存取 token
    '''
    def __init__(self):
        # 创建对本机数据库的连接对象
        self.conn = redis.Redis(host='localhost', port=6379, db=0)

    def set(self, key, dict_value):
        # 将 dict_value pickle.dumps，转化为二进制 bytes数据
        value_ = pickle.dumps(dict_value)
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
            return {}   # 为 None(值不存在)，返回空字典

    def save_token(self, id, key='token'):
        '''
        生成 token 并存到 Redis，
        返回 token
        '''
        token = new_csrf_token()

        tokens_dict = self.get(key)
        tokens_dict[token] = id
        # 将数据存储到数据库
        self.set(key, tokens_dict)

        return token

    def del_token(self, token, tokens_dict):
        '''
        删除 token 并储存
        '''
        tokens_dict.pop(token)
        self.set('token', tokens_dict)
