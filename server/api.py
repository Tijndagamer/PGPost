"""
    api.py
    This file is part of PGPost.

    Copyright (c) 2018 Martijn

    Partially inspired by PietPtr's cputhief-backend, licensed under the GPLv3.
    https://github.com/PietPtr/cputhief-backend

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

from flask import g
from flask import request
from flask import Response
from flask import json

def ok(json_data):
    res = Response(json_data, status=200, mimetype="application/json")
    return res

def success():
    res = Response("{\"success\":true}", status=200, mimetype="application/json")
    return res

def error(reason, errno):
    res = Response("{\"reason\":\"" + reason + "\"}", status=errno, mimetype="application/json")
    return res

def format_post(raw_post, post_text):
    """Format post in json."""

    raw_post["post"] = post_text
    return json.dumps(raw_post)
