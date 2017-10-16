#!/usr/bin/python3
"""
    PGPostDB.py
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

import gnupg
import MySQLdb as mdb
import sys

GPGHOME = "/home/martijn/Coding/GitHub/PGPost/gpgdb"

class PGPostDB:
    gpg = None
    con = None
    cur = None

    add_post = """INSERT INTO
            posts
                (id, fingerprint, username, trust, post, posttime)
            VALUES
                (NULL, %(fingerprint)s, %(username)s, %(trust)s, %(post)s, NULL)"""

    def __init__(self, server, username, password, db):
        """Class to handle the PGPost backend: content and pubkey databases."""

        self.con = mdb.connect(server, username, password, db)
        self.cur = self.con.cursor()
        self.gpg = gnupg.GPG(gnupghome = GPGHOME)

    # Content database management using MySQL

    def init_db(self):
        """Initialize MySQL database. DESTROYS ALL DATA!!!"""
        self.cur.execute("DROP TABLE IF EXISTS posts")
        self.cur.execute("CREATE TABLE posts(id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, \
            fingerprint TINYTEXT, username TINYTEXT, trust TINYINT, \
            post MEDIUMTEXT, posttime TIMESTAMP)")

    def post(self, post):
        """Add a new post to the database.
        
        Each post is a clearsigned (signed using --clearsign) file read into
        memory: the signature and the content are combined into one.

        Returns false if signature could not be verified.
        """

        ver = self.verify(post)

        if ver.valid:
            data_new_post = { "fingerprint" : ver.fingerprint,
                    "username" : ver.username,
                    "trust" : ver.trust_level,
                    "post" : post,}
            self.cur.execute(self.add_post, data_new_post)
            self.con.commit()
            return True, self.cur.rowcount
        else:
            return False

    def read(self):
        """Returns all posts"""
 
        self.cur.execute("SELECT * FROM posts")
        rows = self.cur.fetchall()
        for row in rows:
            print(row)

    def format_post(self, raw_post):
        """Format post accordingly.

        Returns a dictionary with id, fingerprint, name, trust level, post and
        posttime.
        """

        return {"id" : raw_post[0], "fingerprint" : raw_post[1], "name" : raw_post[2], \
                "trust" : raw_post[3], "post" : raw_post[4], "posttime" : raw_post[5]}

    def read_by_fingerprint(self, fingerprint):
        """Returns all posts in the database by specified fingerprint

        Returns a list with a dictionary for each post. Each dictionary has an
        id, fingerprint, name, trust, post and posttime value.
        """

        self.cur.execute("SELECT * FROM posts WHERE fingerprint = \"{}\"".format(\
                fingerprint))
        rows = self.cur.fetchall()
        posts = []
        for row in rows:
            posts.append(self.format_post(row))
        return posts

    def read_by_id_n(self, id_n):
        """Returns the post in the database with the specified id_n"""

        self.cur.execute("SELECT * FROM posts WHERE id = \"{}\"".format(id_n))
        rows = self.cur.fetchall()

        return self.format_post(rows[0])

    def close(self):
        self.con.close()

    # Public and private key management, verifying, etc. via GPG

    def import_key(self, pubkey):
        """Import pubkey into the pubkey db.
        Only one key per call!

        Returns a list [bool succeeded, import_results]
        """

        import_results = self.gpg.import_keys(pubkey)

        if import_results.results[0]['ok'] != '0':
            return [True, import_results]
        else:
            return [False, import_results]

    def delete_key(self, fingerprint):
        """Delete a key from the database."""

        return self.gpg.delete_keys(fingerprint)

    def verify(self, data):
        """Verify signature and return results"""

        return self.gpg.verify(data)
