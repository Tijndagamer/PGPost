"""
    app.py
    This file is part of PGPost.

    Copyright (c) 2017, 2018 Martijn

    PGPost is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PGPost is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with PGPost.  If not, see <http://www.gnu.org/licenses/>.
"""

from flask import Flask
from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import flash
from werkzeug.utils import secure_filename
from PGPostDB import PGPostDB
import os
import uuid
from random import randint

UPLOAD_FOLDER = "/tmp/pgpostuploads"
ALLOWED_EXTENSIONS= set(["asc", "md", "txt"])

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if os.path.isdir(app.config["UPLOAD_FOLDER"]) == False:
    print("UPLOAD_FOLDER does not exist yet, creating...")
    os.mkdir(app.config["UPLOAD_FOLDER"])

# There's probably a better way to not save the password in the source.
password = ""
with open(".pgpost_pass") as f:
    password = f.read().strip()
db = PGPostDB("localhost", "pgpost", password, "PGPost")

# Utility functions

def format_trustbar(trust):
    trustbar = "[....]"
    if trust == 1:
        trustbar = "[=...]"
    elif trust == 2:
        trustbar = "[==..]"
    elif trust == 3:
        trustbar = "[===.]"
    elif trust == 4:
        trustbar = "[FULL]"
    return trustbar

def strip_signature(post):
    """Strip PGP signature data from post, only keep the user content itself."""

    split_post = post.split('\n')
    text = ""

    i = 0
    while i < len(split_post):
        if i > 2:
            if split_post[i] == "-----BEGIN PGP SIGNATURE-----":
                break
            else:
                text += split_post[i] + '\n'
                i += 1
        else:
            i += 1
    return text

def allowed_file(filename):
    """Checks for allowed file extensions."""

    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# URL handlers

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/latest")
def show_latest():
    """Redirect to latest post."""

    return redirect("/post&latest")

@app.route("/post")
def show_post_id():
    """Show a post.

    Either gives the post of the specified ID or returns the latest post.
    """

    try:
        latest = request.args.get("latest")
        id_n = request.args.get("id")
        raw = request.args.get("raw")
    except:
        print("dafuq")

    print(latest)
    print(id_n)
    print(raw)

    if latest != None:
        raw_post = db.read_latest()

    if id_n == None or latest != None:
        raw_post = db.read_latest()
    else:
        raw_post = db.read_by_id_n(id_n)
    # Abort to 404 page if there's no post for id_n
    if raw_post == False:
        print("Raw post is empty!")
        abort(404)

    header = "{name} ({posttime}) [{fingerprint}] \n".format(name = raw_post["name"], \
            posttime = raw_post["posttime"], fingerprint = raw_post["fingerprint"])
    i = len(header) - 2
    while i > 0:
        header += '-'
        i -= 1

    if raw != None:
        post_text = raw_post["post"]
    else:
        post_text = strip_signature(raw_post["post"])
    footer = "{trustbar}".format(trustbar = format_trustbar(raw_post["trust"]))

    post = {"header" : header, "post" : post_text, "footer" : footer}

    return render_template("post.html", id_n = id_n, post = post)

@app.route("/fp/<fingerprint>")
def show_posts_by_fingerprint(fingerprint):
    """Show all posts by given fingerprint."""

    raw_posts = db.read_by_fingerprint(fingerprint)
    posts = []

    for raw_post in raw_posts:
        header = "{name} ({posttime}) [{fingerprint}] \n".format(name = raw_post["name"], \
                posttime = raw_post["posttime"], fingerprint = fingerprint)
        i = len(header) - 2
        while i > 0:
            header += '-'
            i -= 1
        post = strip_signature(raw_post["post"])
        trustbar = format_trustbar(raw_post["trust"])
        posts.append({"header" : header, "post" : post, "trustbar" : trustbar, \
                "id" : raw_post["id"]})

    return render_template("posts_by_fp.html", fingerprint = fingerprint, posts = posts)

@app.route("/upload", methods=["GET", "POST"])
def upload_new_post():
    """Allows the user to upload a new post."""

    if request.method == "POST":
        if "file" not in request.files:
            return render_template("upload_failed", error = "No file part.")
        f = request.files["file"]
        if f.filename == '':
            return render_template("upload_failed.html", error = "No file selected.")
        if f and allowed_file(f.filename):
            # Create a unique filename
            filename = uuid.uuid4().hex + '-' + secure_filename(f.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            f.save(filepath)
            with open(filepath) as fo:
                success, c = db.post(fo.read())
                os.remove(filepath)
                if success:
                    return render_template("upload_success.html")
                else:
                    return render_template("upload_failed.html", error = "Invalid, wrong or not trusted signature.")
        else:
            return render_template("upload_failed.html", error = "Illegal file.")

    return render_template("upload.html")

@app.route("/random")
def random_post():
   return redirect("/post?id=" + str(randint(1, 10)))

# Error handlers

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
