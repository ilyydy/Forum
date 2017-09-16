from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    abort,
)
import uuid
from routes import *

from models.mail import Mail
from models.topic import Topic
from models.board import Board
from models.user import User
from utils import log

main = Blueprint('topic', __name__)

# 创建 redis 的连接对象
conn_var = Conn_db()


@main.route("/")
def index():
    u = current_user()
    page_index = int(request.args.get('page', 1))
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.find_all(page_index=page_index)
    else:
        ms = Topic.find_all(board_id=board_id, page_index=page_index)

    max_page = len(ms) // 30 + 1

    bs = Board.find_all(sort_flag=1)
    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template("topic/index.html",
                           user=u,
                           ms=ms,
                           bs=bs,
                           bid=board_id,
                           page_index=page_index,
                           max_page=max_page,
                           mails=mail_count)


@main.route('/topic/<int:id>')
def detail(id):
    m = Topic.get(id)
    u = current_user()
    token = conn_var.save_token(id)
    mail_count = Mail.count(receiver_id=u.id, read=False)
    # 传递 topic 的所有 reply 到 页面中
    return render_template("topic/detail.html",
                           topic=m,
                           user=u,
                           token=token,
                           mails=mail_count)


@main.route("/topic/add", methods=["POST"])
def add():
    u = current_user()
    form = request.form
    token = request.args.get('token')
    tokens_dict = conn.get('token')
    if token in tokens_dict and tokens_dict[token] == u.id:
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            m = Topic.new(form, user_id=u.id)
            return redirect(url_for('.detail', id=m.id))
        else:
            abort(404)
    else:
        abort(403)


@main.route("/topic/delete")
def delete():
    id = int(request.args.get('id'))
    token = request.args.get('token')
    tokens_dict = conn_var.get('token')
    u = current_user()
    if token in tokens_dict and tokens_dict[token] == u.id:
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            print('删除 topic 用户是', u, id)
            topic = Topic.find(id)
            replies = topic.replies()
            topic.delete()
            for i in replies:
                i.delete()
            return redirect(url_for('.index'))
        else:
            abort(404)
    else:
        abort(403)


@main.route("/topic/new")
def new():
    u = current_user()
    board_id = int(request.args.get('board_id', '0'))
    token = conn_var.save_token(id)
    bs = Board.find_all(sort_flag=1)
    mail_count = Mail.count(receiver_id=u.id, read=False)
    return render_template("topic/new.html",
                           bs=bs,
                           token=token,
                           bid=board_id,
                           user=u,
                           mails=mail_count)


@main.route('/topic/edit')
def edit():
    id = int(request.args.get('id'))
    m = Topic.get(id)
    token = conn_var.save_token(id)
    u = current_user()
    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template("topic/topic_edit.html",
                           topic=m,
                           token=token,
                           user=u,
                           mails=mail_count)


@main.route("/topic/update", methods=["POST"])
def update():
    form = request.form
    u = current_user()
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
