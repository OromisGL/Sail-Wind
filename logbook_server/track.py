import os
from bson import ObjectId
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from logbook_server.auth import login_required
from logbook_server.db import get_db
from logbook_server.map_utils import *

img_path_arrow = './assets/blue-arrow-png.png'
DWD_img = './assets/dwd-logo-png.png'
UPLOAD_FOLDER = 'logbook_server/uploads/'
ALLOWED_EXTENSIONS = {'gpx'}

bp = Blueprint('track', __name__, url_prefix='/track')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS # checking for the right Filename

@bp.route('/')
@login_required
def index():
    
    db = get_db()
    posts = list(db.tracks.find({"created_by": g.user["user_name"]}, {"file": 1, "created_by": 1, "title": 1, "description": 1}))
    maps = {}
    
    for post in posts:
        if "file" in post:
            file_path = os.path.join(UPLOAD_FOLDER, post["file"])
            print(file_path)
            
            if os.path.exists(file_path):
                maps[post["_id"]] =  build_map(file_path)._repr_html_()
            else:
                flash(f"File Not found: {file_path}")
    # print(the_map._repr_html_())
    return render_template('track/index.html',maps=maps, posts=posts)

@bp.route('/map')
@login_required
def map():
    
    if LATITUDE and LONGITUDE:
        
        wind_arrow = encode_image(img_path_arrow)
        DWD_logo = encode_image(DWD_img)
        initial_location_name = "Werbellinsee"
        return render_template(
            'track/map.html', 
            initial_location_name = initial_location_name,
            LATITUDE=LATITUDE,
            LONGITUDE=LONGITUDE,  
            wind_speed = WEATHER_DATA["wind_speed"], 
            wind_direction = WEATHER_DATA["wind_direction"], 
            compass_direction = WEATHER_DATA["compass_direction"], 
            getBeauforScale = WEATHER_DATA["beaufort"], 
            wind_arrow = wind_arrow, 
            DWD_logo = DWD_logo)
    return render_template('track/map.html')


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if 'file' not in request.files:
            error = 'No file part'
            
        file = request.files['file']
        
        if file.filename == '':
            error = 'No selected file'  
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # filename = filename[:-4] # Try to remove a Bug where file extension appeared twice 
            # filename = filename + '.gpx'
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
        else:
            error = 'File extension not allowed'
            
        if error is not None:
            flash(error)
            return render_template('track/create.html')
        else:
            track = {
                "created_by": g.user["user_name"],
                "title": title,
                "description": description,
                "file": filename
            }
            
            db = get_db()
            db.tracks.insert_one(track)
            
            return redirect(url_for('track.index'))
        
    return render_template('track/create.html')

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
        file = request.files['file']
        error = None

        if not title:
            error = 'Title is required.'
        
        old_file = post.get("file", "")
        new_file_name = old_file
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            if old_file:
                old_file_path = os.path.join(UPLOAD_FOLDER, old_file)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                            
            file.save(file_path)
            new_file_name = filename

        if error is not None:
            flash(error)
            return render_template('track/update.html', post=post)
        
        else:
            db = get_db().tracks.update_one(
                {"_id": post["_id"]},
                {"$set":{"title": title, "description": description, "file": new_file_name}}
            )
            flash('Post updated successfully!')
            return redirect(url_for('track.index'))

    return render_template('track/update.html', post=post)

@bp.route('/<string:id>/delete', methods=('POST',))
@login_required
def delete(id):
    id = ObjectId(id)
    db = get_db()
    get_post(id)
    post = db.tracks.find_one({"_id": id},{"title": 1, "file": 1})
    if post and "file" in post:
        title = post["title"]
        file_path = os.path.join(UPLOAD_FOLDER, post["file"])
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f"Deleted Post: {title}")
        else:
            flash(f"File Not Found: {file_path}")
    db.tracks.delete_one({"_id": id})
    return redirect(url_for('track.index'))