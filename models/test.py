
from pymongo import MongoClient

import datetime
import time


def timestamp():
    return int(time.time())


def datetime_delta(time):
    '''
    根据传入的时间戳返回距离现在的日常表示时间字符串
    '''
    now = timestamp()
    seconds = now - time
    days = int(seconds / 3600 / 24)
    months = int(days / 30)

    if days < 30:
        if seconds < 60:
            return '几秒前'
        elif seconds < 3600:
            return '{}分钟前'.format(int(seconds/60))
        elif days < 1:
            return '{}小时前'.format(int(seconds/3600))
        else:
            return '{}天前'.format(days)
    else:
        return '{}月前'.format(months)

'''
连接到 Mongo 数据库的基础类
'''

mongo = MongoClient()     # 生成到 Mongo 连接对象


def next_id(name):
    '''
    自增的自建 id
    '''
    query = {
        'name': name,
    }
    update = {
        '$inc': {
            'seq': 1
        }
    }
    kwargs = {
        'query': query,
        'update': update,
        'upsert': True,
        'new': True,
    }
    # 存储数据的 id
    doc = mongo.forum['data_id']

    new_id = doc.find_and_modify(**kwargs).get('seq')
    return new_id


class Mongo(object):
    @classmethod
    def valid_names(cls):
        names = [
            '_id',
            # (字段名, 类型, 值)
            ('id', int, -1),
            ('deleted', bool, False),
            ('created_time', int, 0),
            ('updated_time', int, 0),
            ('active_time', int, 0),
        ]
        return names

    @classmethod
    def new(cls, form=None, **kwargs):
        """
        new 是给外部使用的函数
        """
        name = cls.__name__
        # 创建一个空对象
        m = cls()
        # 把定义的数据写入空对象, 未定义的数据输出错误
        names = cls.valid_names().copy()
        # 去掉 _id 这个特殊的字段
        names.remove('_id')
        if form is None:
            form = {}

        for f in names:
            k, t, v = f
            if k in form:
                setattr(m, k, t(form[k]))
            else:
                # 设置默认值
                setattr(m, k, v)
        # 处理额外的参数 kwargs
        for k, v in kwargs.items():
            if hasattr(m, k):
                setattr(m, k, v)
            else:
                raise KeyError
        # 写入默认数据
        m.id = next_id(name)

        ts = timestamp()
        m.created_time = ts
        m.updated_time = ts
        m.active_time = ts
        m.deleted = False
        m.save()
        return m

    @classmethod
    def _new_with_bson(cls, bson):
        """
        这是给内部 find_all 这种函数使用的函数
        从 mongo 数据中恢复一个 model
        """
        m = cls()
        names = cls.valid_names().copy()
        # 去掉 _id 这个特殊的字段
        names.remove('_id')
        for f in names:
            k, t, v = f
            if k in bson:
                setattr(m, k, bson[k])
            else:
                # 设置默认值
                setattr(m, k, v)
        setattr(m, '_id', bson['_id'])
        return m

    @classmethod
    def _find(cls, **kwargs):
        """
        mongo 数据查询
        """
        name = cls.__name__
        kwargs['deleted'] = False
        # 每页显示的条数
        page_size = kwargs.pop('page_size', 30)
        # 当前页码
        page_index = kwargs.pop('page_index', 1)
        # 需要跳过的记录数
        skips = (page_index - 1) * page_size
        # 排序方式，默认按活动时间从近到远
        sort_flag = kwargs.pop('sort_flag', -1)

        doc = mongo.forum[name]

        ds = (doc.find(kwargs)
              .sort("active_time", sort_flag)
              .skip(skips)
              .limit(page_size)
              )

        result = [cls._new_with_bson(d) for d in ds]
        return result

    @classmethod
    def find_all(cls, **kwargs):
        return cls._find(**kwargs)

    @classmethod
    def find_one(cls, **kwargs):
        kwargs['deleted'] = False
        hold = cls._find(**kwargs)
        # print('find one debug', kwargs, l)
        if len(hold) > 0:
            return hold[0]
        else:
            return None

    @classmethod
    def find_by(cls, **kwargs):
        return cls.find_one(**kwargs)

    @classmethod
    def find(cls, id):
        return cls.find_one(id=id)

    @classmethod
    def count(cls, **kwargs):
        name = cls.__name__
        kwargs['deleted'] = False

        num = mongo.forum[name].find(kwargs).count()
        return num

    def update(self, form):
        name = self.__class__.__name__
        query = {
            'id': self.id,
        }
        ut = timestamp()
        form['updated_time'] = ut
        mongo.forum[name].update_one(query, {'$set': form})

    def update_active_time(self):
        name = self.__class__.__name__
        query = {
            'id': self.id,
        }
        at = timestamp()
        form = {
            'active_time': at,
        }
        mongo.forum[name].update_one(query, {'$set': form})

    def save(self):
        name = self.__class__.__name__
        mongo.forum[name].save(self.__dict__)

    def delete(self):
        name = self.__class__.__name__
        query = {
            'id': self.id,
        }
        form = {
            'deleted': True
        }
        mongo.forum[name].update_one(query, {'$set': form})

    def time_str(self, flag='at'):
        '''
        返回实例的日常使用的时间字符串，默认为 active_time
        '''
        if flag == 'at':
            return datetime_delta(self.active_time)
        elif flag == 'up':
            return datetime_delta(self.updated_time)
        else:
            return datetime_delta(self.created_time)

    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = {1}'.format(k, v)
                      for k, v in self.__dict__.items())
        return '<{0}: \n  {1}\n>'.format(class_name, '\n  '.join(properties))

class Topic(Mongo):
    @classmethod
    def valid_names(cls):
        names = super().valid_names()
        names = names + [
            ('views', int, 0),
            ('title', str, ''),
            ('content', str, ''),
            ('user_id', int, 0),
            ('board_id', int, 0),
        ]
        return names

    @classmethod
    def get(cls, id):
        '''
        取得 topic 并增加浏览次数 1
        '''
        t = cls.find(id)
        t.views += 1
        t.save()
        return t

    def user(self):
        u = User.find(self.user_id)
        return u
if __name__ == '__main__':
    ts = Topic.find_all()
    print(ts)
