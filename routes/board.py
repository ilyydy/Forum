from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import current_user
from models.board import Board

'''
版块路由
'''

main = Blueprint('board', __name__)


@main.route("/admin")
def index():
    return render_template('board/admin_index.html')


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    m = Board.new(form)
    return redirect(url_for('topic.index'))
