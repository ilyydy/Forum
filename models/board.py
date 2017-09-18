from models.mongoBase import Mongo


'''
版块类
'''


class Board(Mongo):
    @classmethod
    def valid_names(cls):
        names = super().valid_names()
        names = names + [
            ('title', str, ''),
        ]
        return names
