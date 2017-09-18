from models.mongoBase import Mongo
from models.board import Board
from models.user import User

'''
帖子类
'''


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

    def replies(self):
        from .reply import Reply
        rs = Reply.find_all(topic_id=self.id, sort_flag=1)
        return rs

    def board(self):
        b = Board.find(self.board_id)
        return b

    def user(self):
        u = User.find(self.user_id)
        return u
