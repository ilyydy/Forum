from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    abort,
)

from routes import current_user
from routes.topic import conn_var

from models.mail import Mail
from models.reply import Reply
from models.mail import Mail
from utils import log

'''
回复路由
'''

main = Blueprint('reply', __name__)


def users_from_content(content):
    '''
    解析回复内容，返回要 @ 用户的列表
    不能解决 @ 在文本中间的情况，比如 123@name abc
    '''
    parts = content.split(' ')
    users = []
    for p in parts:
        if p.startswith('@'):
            username = p[1:]
            u = User.find_by(username=username)
            users.append(u)
    return users


def send_mails(sender, receivers, form):
    '''
    给用户列表发送消息提醒
    参数：发送者，接收者列表，回复所在帖子
    '''
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
    '''
    新增回复
    '''
    form = request.form
    u = current_user()
    content = form.get('content')         # 回复内容
    token = form.get('token')             # 回复验证 token
    tokens_dict = conn_var.get('token')   # 存有 token:u.id 的字典

    # 验证 token
    if token in tokens_dict and tokens_dict[token] == u.id:
        # 删除 token
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            # 新增回复
            m = Reply.new(form, user_id=u.id)
            m.topic().update_active_time()
            # 发邮件
            users = users_from_content(content)
            LZ = m.topic().user()
            if LZ.id not in [u.id for u in users]:
                users.append(LZ)
            send_mails(u, users, form)

            return redirect(url_for('topic.detail', id=m.topic_id))
        else:
            abort(404)
    else:
        abort(403)


@main.route("/delete")
def delete():
    '''
    删除回复
    '''
    u = current_user()
    id = int(request.args.get('id'))
    token = request.args.get('token')
    topic_id = request.args.get('t_id')
    tokens_dict = conn_var.get('token')

    if token in tokens_dict and tokens_dict[token] == u.id:
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            reply = Reply.find(id)
            reply.delete()
            return redirect(url_for('topic.detail', id=topic_id))
        else:
            abort(404)
    else:
        abort(403)


@main.route('/edit')
def edit():
    '''
    编辑回复
    '''
    u = current_user()
    id = int(request.args.get('id'))
    topic_id = int(request.args.get('t_id'))
    r = Reply.find(id)

    token = conn_var.save_token(u.id)
    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template("topic/reply_edit.html",
                           reply=r,
                           token=token,
                           user=u,
                           topic_id=topic_id,
                           mails=mail_count)


@main.route("/update", methods=["POST"])
def update():
    '''
    更新回复
    '''
    u = current_user()
    form = request.form
    id = int(request.args.get('id'))
    token = request.args.get('token')
    topic_id = int(request.args.get('topic_id'))
    tokens_dict = conn_var.get('token')

    if token in tokens_dict and tokens_dict[token] == u.id:
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            reply = Reply.find(id)
            reply.update(form.to_dict())
            return redirect(url_for('topic.detail', id=topic_id))
        else:
            abort(404)
    else:
        abort(403)
