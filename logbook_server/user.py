import os
from bson import ObjectId
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from logbook_server.auth import login_required
from logbook_server.db import get_db

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    return render_template('user/profile.html')

@bp.route('/friends', methods=('GET', 'POST'))
@login_required
def friends():
    return render_template('user/friends.html')

@bp.route('/posts', methods=('GET', 'POST'))
@login_required
def posts():
    return render_template('user/posts.html')