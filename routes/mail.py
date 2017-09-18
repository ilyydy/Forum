from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import current_user
from models.mail import Mail

'''
消息路由
'''

main = Blueprint('mail', __name__)


# @main.route("/add", methods=["POST"])
# def add():
#     form = request.form
#     u = current_user()
#     Mail.new(form, sender_name=u.username)
#     return redirect(url_for(".index"))


@main.route("/")
def index():
    '''
    个人消息页面
    '''
    u = current_user()
    # 未读消息
    new_mail = Mail.find_all(receiver_id=u.id, read=False)
    # 已读消息
    old_mail = Mail.find_all(receiver_id=u.id, read=True)
    # 打开消息页面后将所有未读消息设为已读
    [m.mark_read() for m in new_mail]
    mail_count = Mail.count(receiver_id=u.id, read=False)

    t = render_template(
        "mail/index.html",
        user=u,
        new_mails=new_mail,
        old_mails=old_mail,
        mails=mail_count,
    )

    return t


# @main.route("/view/<int:id>")
# def view(id):
#     mail = Mail.find(id)
#     if current_user().id == mail.receiver_id:
#         mail.mark_read()
#     if current_user().id in [mail.receiver_id, mail.sender_id]:
#         return render_template("mail/detail.html", mail=mail)
#     else:
#         return redirect(url_for(".index"))
