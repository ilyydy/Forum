from models.mongoBase import Mongo
from models.topic import Topic
from models.user import User

'''
回复类
'''


class Reply(Mongo):
    @classmethod
    def valid_names(cls):
        names = super().valid_names()
        names = names + [
            ('content', str, ''),
            ('topic_id', int, 0),
            ('user_id', int, 0),
        ]
        return names

    def user(self):
        u = User.find(self.user_id)
        return u

    def topic(self):
        t = Topic.find(self.topic_id)
        return t
