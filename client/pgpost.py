#!/usr/bin/python3
"""
	pgpost.py
        Python-based terminal client for PGPost

    Usage:
        ./pgpost.py host [-p post] [-k keyid]

	This file is part of PGPost.

    Copyright (c) 2018 Martijn

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

import argparse
import requests
import os
import uuid

parser = argparse.ArgumentParser(description="A Python-based terminal client for PGPost.")
parser.add_argument("-s", "--server", help="PGPost server")
parser.add_argument("-f", "--file", metavar="[FILE]", help="File to post")
parser.add_argument("-p", "--post", metavar="[STRING]", help="Text to post")
parser.add_argument("-k", "--keyid", metavar="[KEYID]", help="GPG Keyid to use")
args = parser.parse_args()
print(args)

if args.server == None:
    args.server = input("Server = ")

if args.file == None and args.post == None:
    args.post = input("Post = ")

if args.file == None and args.post != None:
    filepath = "/tmp/pgpost-tmp-" + uuid.uuid4().hex
    print(filepath)
    with open(filepath, "w+") as f:
        f.write(args.post)
else:
    filepath = args.file

if args.keyid == None:
    os.popen("gpg --clearsign " + filepath)
else:
    os.popen("gpg --default-key " + args.keyid + " --clearsign " + filepath)

with open(filepath + ".asc") as f:
    payload = {"post" : f.read() }
    r = requests.post("http://" + args.server + "/api/upload", data=payload)
    print(r)
    print(r.text)
