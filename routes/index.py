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

'''
登陆注册页、用户个人相关页路由
'''

main = Blueprint('index', __name__)


@main.route("/index")
def index():
    u = current_user()
    return render_template("index.html", user=u)


@main.route("/register", methods=['POST'])
def register():
    form = request.form
    # 用类函数来判断注册是否合法
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    # 用类函数来判断注册是否合法
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
        # session 中删除 user_id
        session.pop('user_id')

        return redirect(url_for('topic.index'))


@main.route('/profile/<username>')
def profile(username):
    '''
    个人资料页
    '''
    u = User.find_by(username=username)
    if u is None:
        return redirect(url_for('topic.index'))
    else:
        # 最近创建的 5 条 topic
        topics = Topic.find_all(user_id=u.id, page_size=5)
        replies = Reply.find_all(user_id=u.id, page_size=5)
        # 最近回复的 5 条 topic
        r_topics = [r.topic() for r in replies]
        # 收到的 mail
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
    '''
    用户上传头像
    '''
    u = current_user()

    # file 是一个上传的文件对象
    file = request.files['avatar']
    suffix = file.filename.split('.')[-1]

    if valid_suffix(lower(suffix)):
        # 出于安全自定义图片名
        filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
        file.save(os.path.join('user_image', filename))
        # u.add_avatar(filename)
        u.user_image = '/uploads/' + filename
        u.save()

    return redirect(url_for(".profile", username=u.username))


# nginx 代理直接转发，实际未使用
@main.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory('user_image', filename)


@main.route('/setting')
def set():
    '''
    个人资料更新
    '''
    u = current_user()
    token = conn_var.save_token(u.id)
    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template('setting.html',
                           user=u,
                           token=token,
                           mails=mail_count)


@main.route("/setting/update", methods=['POST'])
def update():
    '''
    个人资料更新
    '''
    u = current_user()
    form = request.form
    token = form.get('_csrf')
    tokens_dict = conn_var.get('token')

    # 验证 token 是否存在并与 id 对应
    if token in tokens_dict and tokens_dict[token] == u.id:
        conn_var.del_token(token, tokens_dict)
        if u is not None:
            if form.get('action') == "change_setting":   # 改用户名和签名
                u.username = form.get('name')
                u.signature = form.get('signature')
            if form.get('action') == "change_password":  # 改密码
                old_pass = form.get('old_pass')
                if u.password == u.salted_password(old_pass):
                    u.password = form.get('new_pass')
                else:
                    abort(403)
            u.save()  # 保存更新
            return redirect(url_for('index.set'))
        else:
            abort(404)
    else:
        abort(403)


@main.route("/search")
def search():
    '''
    搜索页面，返回 topic.title 中包含关键词的指定页码页的结果
    '''
    u = current_user()
    # 需要第几页内容，默认第 1 页
    page_index = int(request.args.get('page', 1))
    text = request.args.get('q', '')
    if text == '':    # 未键入搜索关键词时不进行后台检索，返回空结果
        ms = []
        max_page = 0
    else:
        page_size = 30  # 默认每页 30 条
        ms = Topic.find_all(title={"$regex": text}, page_index=page_index)
        max_page = len(ms) // page_size + 1

    mail_count = Mail.count(receiver_id=u.id, read=False)

    return render_template("topic/search.html",
                           user=u,
                           ms=ms,
                           page_index=page_index,
                           max_page=max_page,
                           mails=mail_count)
