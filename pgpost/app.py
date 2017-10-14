"""
    app.py
    This file is part of PGPost.

    Copyright (c) 2017 Martijn

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

from PGPostDB import PGPostDB
from flask import Flask
from flask import render_template
from flask import abort
from flask import redirect
from flask import url_for
app = Flask(__name__)

# There's probably a better way to not save the password in the source.
password = ""
with open(".pgpost_pass") as f:
    password = f.read().strip()
db = PGPostDB("localhost", "pgpost", password, "PGPost")

# Utility functions

def format_trustbar(trust):
    trustbar = "trust: [....]"
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

# URL handlers

@app.route("/")
def hello_world():
    return "Hello!"

# This should be possible in a more efficient way,.
@app.route("/id/<int:id_n>")
def show_post_id(id_n):
    """Show post of given id."""

    try:
        raw_post = db.read_by_id_n(id_n)
    except IndexError:
        abort(404)

    header = "{name} ({posttime}) [{fingerprint}] \n".format(name = raw_post["name"], \
            posttime = raw_post["posttime"], fingerprint = raw_post["fingerprint"])
    i = len(header) - 2
    while i > 0:
        header += '-'
        i -= 1
    post_text = strip_signature(raw_post["post"])
    footer = "{trustbar}".format(trustbar = format_trustbar(raw_post["trust"]))

    post = {"header" : header, "post" : post_text, "footer" : footer}

    return render_template("post_id_raw.html", id_n = id_n, post = post)

@app.route("/id/<int:id_n>/raw")
def show_post_id_raw(id_n):
    """Show raw post of given id."""

    try:
        raw_post = db.read_by_id_n(id_n)
    except IndexError:
        abort(404)
    
    header = "{name} ({posttime}) [{fingerprint}] \n".format(name = raw_post["name"], \
            posttime = raw_post["posttime"], fingerprint = raw_post["fingerprint"])
    i = len(header) - 2
    while i > 0:
        header += '-'
        i -= 1
    post_text = raw_post["post"]
    footer = "{trustbar}".format(trustbar = format_trustbar(raw_post["trust"]))

    post = {"header" : header, "post" : post_text, "footer" : footer}

    return render_template("post_id_raw.html", id_n = id_n, post = post)

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

# Error handlers

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
