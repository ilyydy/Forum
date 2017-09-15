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
import uuid


main = Blueprint('topic', __name__)


csrf_tokens = dict()


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    csrf_tokens[token] = u.id
    return token


def get_csrf_token():
    return csrf_tokens


@main.route("/")
def index():
    board_id = int(request.args.get('board_id', -1))
    page_index = int(request.args.get('page', 1))
    if board_id == -1:
        ms = Topic.find_all(page_index=page_index)
    else:
        ms = Topic.find_all(board_id=board_id, page_index=page_index)
    max_page = len(ms) // 30 + 1
    u = current_user()
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
    token = new_csrf_token()
    mail_count = Mail.count(receiver_id=u.id, read=False)
    # 传递 topic 的所有 reply 到 页面中
    return render_template("topic/detail.html",
                           topic=m,
                           user=u,
                           token=token,
                           mails=mail_count)


@main.route("/topic/add", methods=["POST"])
def add():
    form = request.form
    token = request.args.get('token')
    u = current_user()
    if token in csrf_tokens and csrf_tokens[token] == u.id:
        csrf_tokens.pop(token)
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
    u = current_user()
    if token in csrf_tokens and csrf_tokens[token] == u.id:
        csrf_tokens.pop(token)
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
    token = new_csrf_token()
    bs = Board.find_all(sort_flag=1)
    mail_count = Mail.count(receiver_id=u.id, read=False)
    return render_template("topic/new.html",
                           bs=bs, token=token,
                           bid=board_id,
                           user=u,
                           mails=mail_count)


@main.route('/topic/edit')
def edit():
    id = int(request.args.get('id'))
    m = Topic.get(id)
    token = new_csrf_token()
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
    token = request.args.get('token')
    id = int(request.args.get('id'))
    u = current_user()
    if token in csrf_tokens and csrf_tokens[token] == u.id:
        csrf_tokens.pop(token)
        if u is not None:
            topic = Topic.find(id)
            topic.update(form.to_dict())
            return redirect(url_for('.detail', id=topic.id))
        else:
            abort(404)
    else:
        abort(403)
