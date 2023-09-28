from bson import ObjectId
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = list(db.tracks.find({"created_by": g.user["user_name"]}))
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            track = {
                "created_by": g.user["user_name"],
                "title": title,
                "description": description
            }
            db = get_db()
            db.tracks.insert_one(track)
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().tracks.find_one({"_id": id})

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['created_by'] != g.user['user_name']:
        abort(403)

    return post

@bp.route('/<string:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    id = ObjectId(id)
    print(type(id))
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db().tracks.update_one(
                {"_id": post["_id"]},
                {"$set":{"title": title, "description": description}}
            )
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    id = ObjectId(id)
    get_post(id)
    db = get_db().tracks.delete_one({"_id": id})
    return redirect(url_for('blog.index'))
