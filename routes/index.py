from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    make_response,
    send_from_directory,
    abort,
)
import os
import uuid
# from werkzeug.utils import secure_filename
from models.user import User
from models.topic import Topic
from models.reply import Reply
from models.mail import Mail
from routes import current_user
from routes.topic import conn_var
from utils import log

main = Blueprint('index', __name__)


@main.route("/index")
def index():
    u = current_user()
    return render_template("index.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    form = request.form
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    if u is None:
        # 转到 topic.index 页面
        return redirect(url_for('topic.index'))
    else:
        # session 中写入 user_id
        session['user_id'] = u.id
        # 设置 cookie 有效期为 永久
        session.permanent = True
        return redirect(url_for('topic.index'))


@main.route("/logout")
def logout():
    form = request.form
    u = current_user()
    if u is None or 'user_id' not in session:
        # 转到 topic.index 页面
        return redirect(url_for('topic.index'))
    else:
        # session 中写入 user_id
        session.pop('user_id')
        return redirect(url_for('topic.index'))


@main.route('/profile/<username>')
def profile(username):
    u = User.find_by(username=username)
    if u is None:
        return redirect(url_for('.index'))
    else:
        topics = Topic.find_all(user_id=u.id, page_size=5)
        replies = Reply.find_all(user_id=u.id,
                                 page_size=5)
        r_topics = [r.topic() for r in replies]
        mail_count = Mail.count(receiver_id=u.id, read=False)

        return render_template('profile.html',
                               user=u,
                               topics=topics,
                               r_topics=r_topics,
                               mails=mail_count)


def valid_suffix(suffix):
    valid_type = ['jpg', 'png', 'jpeg']
    return suffix in valid_type


@main.route('/image/add', methods=["POST"])
def add_img():
    u = current_user()

    # file 是一个上传的文件对象
    file = request.files['avatar']
    suffix = file.filename.split('.')[-1]
    if valid_suffix(suffix):
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        file.save(os.path.join('user_image', filename))
        # u.add_avatar(filename)
        u.user_image = '/uploads/' + filename
        u.save()

    return redirect(url_for(".profile", username=u.username))


# send_from_directory
# nginx 静态文件
@main.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory('user_image', filename)


@main.route('/setting')
def set():
    u = current_user()
    token = conn_var.save_token(u.id)
    mail_count = Mail.count(receiver_id=u.id, read=False)
    return render_template('setting.html',
                           user=u,
                           token=token,
                           mails=mail_count)


@main.route("/setting/update", methods=['POST'])
def update():
    u = current_user()
    form = request.form
    token = form.get('_csrf')
    tokens_dict = conn_var.get('token')
    if token in tokens_dict and tokens_dict[token] == u.id:
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            if form.get('action') == "change_setting":
                u.username = form.get('name')
                u.signature = form.get('signature')
            if form.get('action') == "change_password":
                old_pass = form.get('old_pass')
                if u.password == u.salted_password(old_pass):
                    u.password = form.get('new_pass')
                else:
                    abort(403)
            u.save()
            return redirect(url_for('index.set'))
        else:
            abort(404)
    else:
        abort(403)


@main.route("/search")
def search():
    u = current_user()
    page_index = int(request.args.get('page', 1))
    text = request.args.get('q', '')
    if text == '':
        ms = []
        max_page = 0
    else:
        ms = Topic.find_all(title={"$regex": text}, page_index=page_index)
        max_page = len(ms) // 30 + 1

    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template("topic/search.html",
                           user=u,
                           ms=ms,
                           page_index=page_index,
                           max_page=max_page,
                           mails=mail_count)
