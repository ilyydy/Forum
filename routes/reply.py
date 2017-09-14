from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    abort,
)

from models.mail import Mail
from routes import *
from routes.topic import get_csrf_token, new_csrf_token

from models.reply import Reply
from models.mail import Mail
from utils import log

main = Blueprint('reply', __name__)


def users_from_content(content):
    # 不能解决 @在文本中间 比如 123@name abc
    parts = content.split(' ')
    users = []
    for p in parts:
        if p.startswith('@'):
            username = p[1:]
            u = User.find_by(username=username)
            users.append(u)
    return users


def send_mails(sender, receivers, form):
    for r in receivers:
        form = dict(
            title=form.get('title'),
            content=form.get('content'),
            sender_name=sender.username,
            topic_id=form.get('topic_id'),
            receiver_id=r.id,
            type='回复',
        )

        m = Mail.new(form)


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()
    content = form.get('content')
    token = form.get('token')
    csrf_tokens = get_csrf_token()
    if token in csrf_tokens and csrf_tokens[token] == u.id:
        csrf_tokens.pop(token)
        if u is not None:
            # 发邮件
            users = users_from_content(content)
            m = Reply.new(form, user_id=u.id)
            m.topic().update_active_time()
            send_mails(u, users, form)
            return redirect(url_for('topic.detail', id=m.topic_id))
        else:
            abort(404)
    else:
        abort(403)


@main.route("/delete")
def delete():
    id = int(request.args.get('id'))
    token = request.args.get('token')
    topic_id = request.args.get('t_id')
    u = current_user()
    csrf_tokens = get_csrf_token()
    if token in csrf_tokens and csrf_tokens[token] == u.id:
        csrf_tokens.pop(token)
        if u is not None:
            print('删除 reply 用户是', u, id)
            reply = Reply.find(id)
            reply.delete()
            return redirect(url_for('topic.detail', id=topic_id))
        else:
            abort(404)
    else:
        abort(403)


@main.route("/update", methods=["POST"])
def update():
    form = request.form
    id = int(request.args.get('id'))
    token = request.args.get('token')
    topic_id = int(request.args.get('topic_id'))
    u = current_user()
    csrf_tokens = get_csrf_token()
    if token in csrf_tokens and csrf_tokens[token] == u.id:
        csrf_tokens.pop(token)
        if u is not None:
            reply = Reply.find(id)
            reply.update(form.to_dict())
            return redirect(url_for('topic.detail', id=topic_id))
        else:
            abort(404)
    else:
        abort(403)


@main.route('/edit')
def edit():
    id = int(request.args.get('id'))
    topic_id = int(request.args.get('t_id'))
    r = Reply.get(id)
    csrf_tokens = get_csrf_token()
    token = new_csrf_token()
    u = current_user()
    mail_count = Mail.count(receiver_id=u.id, read=False)
    return render_template("topic/reply_edit.html",
                           reply=r,
                           token=token,
                           user=u,
                           topic_id=topic_id,
                           mails=mail_count)
