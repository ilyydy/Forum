from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *
from models.mail import Mail

main = Blueprint('mail', __name__)


# @main.route("/add", methods=["POST"])
# def add():
#     form = request.form
#     u = current_user()
#     Mail.new(form, sender_name=u.username)
#     return redirect(url_for(".index"))


@main.route("/", methods=["GET"])
def index():
    u = current_user()
    # send_mail = Mail.find_all(sender_id=u.id)
    new_mail = Mail.find_all(receiver_id=u.id, read=False)
    old_mail = Mail.find_all(receiver_id=u.id, read=True)
    for m in new_mail:
        m.mark_read()
    mail_count = Mail.count(receiver_id=u.id, read=False)
    t = render_template(
        "mail/index.html",
        # sends=send_mail,
        new_mails=new_mail,
        old_mails=old_mail,
        user=u,
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
