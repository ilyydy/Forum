import hashlib
from models.mongoBase import Mongo

'''
用户类
'''


class User(Mongo):
    @classmethod
    def valid_names(cls):
        names = super().valid_names()
        names = names + [
            ('username', str, ''),
            ('password', str, ''),
            ('user_image', str, '/uploads/default.png'),
            ('signature', str, '这家伙很懒，什么个性签名都没有留下。'),
        ]
        return names

    def salted_password(self, password, salt='$!@><?>HUI&DWQa`'):
        '''
        密码加盐，返回散列值
        '''
        def sha256():
            ascii_str = password + salt
            return hashlib.sha256(ascii_str.encode('ascii')).hexdigest()

        hash1 = sha256()
        return hash1

    @classmethod
    def register(cls, form):
        name = form.get('username', '')
        pwd = form.get('password', '')
        if len(name) > 2 and User.find_by(username=name) is None:
            u = User.new(form)
            u.password = u.salted_password(pwd)
            u.save()
            return u
        else:
            return None

    @classmethod
    def validate_login(cls, form):
        '''
        检验是否合法登陆
        '''
        name = form.get('username', '')
        pwd = form.get('password', '')
        user = User.find_by(username=name)
        if user is not None and user.password == user.salted_password(pwd):
            return user
        else:
            return None
