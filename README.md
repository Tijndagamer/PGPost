PGPost
======

PGPost is a proof of concept microblogging service which authenticates each individual
post, rather than a login at the start of a session. Although this form of authentication
makes user based personalization impossible, it significantly decreases the amount of trust
a user has to have in the service. Each user can verify each post themselves, and thanks
to the PGP Web of Trust they know who they can trust. For more information on this way
of authentication, see `docs/protocol.md`.

Dependencies
------------

System dependencies:
```
- gpg
- a MySQL server
```

Python dependencies:
```
    python-gnupg
    python-mysqldb
```

License
-------

```
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
```
