from models.mongoBase import Mongo

'''
消息类
'''


class Mail(Mongo):
    @classmethod
    def valid_names(cls):
        names = super().valid_names()
        names = names + [
            ('title', str, ''),
            ('content', str, ''),
            ('sender_name', str, ''),
            ('receiver_id', int, 0),
            ('topic_id', int, 0),
            ('read', bool, False),
            ('type', str, '消息'),
        ]
        return names

    def mark_read(self):
        '''
        标为已读
        '''
        self.read = True
        self.save()
