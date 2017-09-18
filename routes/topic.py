from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    abort,
)

from routes import *

from models.mail import Mail
from models.topic import Topic
from models.board import Board
from models.user import User
from utils import log

'''
帖子路由
'''

main = Blueprint('topic', __name__)

# 创建 redis 的连接对象
conn_var = Conn_db()


@main.route("/")
def index():
    '''
    主页
    '''
    u = current_user()
    page_index = int(request.args.get('page', 1))
    # 选择显示哪个版块的帖子
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:    # 默认显示所有版块的帖子
        ts = Topic.find_all(page_index=page_index)
    else:
        ts = Topic.find_all(board_id=board_id, page_index=page_index)

    max_page = len(ts) // 30 + 1

    bs = Board.find_all(sort_flag=1)
    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template("topic/index.html",
                           user=u,
                           ts=ts,
                           bs=bs,
                           bid=board_id,
                           page_index=page_index,
                           max_page=max_page,
                           mails=mail_count)


@main.route('/topic/<int:id>')
def detail(id):
    '''
    帖子详情页
    '''
    u = current_user()
    t = Topic.get(id)
    token = conn_var.save_token(u.id)
    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template("topic/detail.html",
                           topic=t,
                           user=u,
                           token=token,
                           mails=mail_count)


@main.route("/topic/new")
def new():
    '''
    新增帖子
    '''
    u = current_user()
    board_id = int(request.args.get('board_id', '0'))
    token = conn_var.save_token(u.id)
    bs = Board.find_all(sort_flag=1)
    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template("topic/new.html",
                           bs=bs,
                           token=token,
                           bid=board_id,
                           user=u,
                           mails=mail_count)


@main.route("/topic/add", methods=["POST"])
def add():
    '''
    新增帖子
    '''
    u = current_user()
    form = request.form
    token = request.args.get('token')
    tokens_dict = conn_var.get('token')

    if token in tokens_dict and tokens_dict[token] == u.id:
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            t = Topic.new(form, user_id=u.id)
            return redirect(url_for('.detail', id=t.id))
        else:
            abort(404)
    else:
        abort(403)


@main.route("/topic/delete")
def delete():
    '''
    删除帖子
    '''
    u = current_user()
    id = int(request.args.get('id'))
    token = request.args.get('token')
    tokens_dict = conn_var.get('token')

    if token in tokens_dict and tokens_dict[token] == u.id:
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            topic = Topic.find(id)
            # 同时删除相关的回复
            replies = topic.replies()
            [r.delete() for r in replies]
            topic.delete()

            return redirect(url_for('.index'))
        else:
            abort(404)
    else:
        abort(403)


@main.route('/topic/edit')
def edit():
    '''
    编辑帖子
    '''
    u = current_user()
    id = int(request.args.get('id'))
    t = Topic.find(id)
    token = conn_var.save_token(u.id)
    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template("topic/topic_edit.html",
                           topic=t,
                           token=token,
                           user=u,
                           mails=mail_count)


@main.route("/topic/update", methods=["POST"])
def update():
    '''
    编辑帖子
    '''
    u = current_user()
    form = request.form
    id = int(request.args.get('id'))
    token = request.args.get('token')
    tokens_dict = conn_var.get('token')

    if token in tokens_dict and tokens_dict[token] == u.id:
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            topic = Topic.find(id)
            topic.update(form.to_dict())

            return redirect(url_for('.detail', id=topic.id))
        else:
            abort(404)
    else:
        abort(403)
