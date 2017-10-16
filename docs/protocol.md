PGP ID Post
===========

Status
------

This protocol spec. is not yet finished. This is a draft.

Abstract
--------

The PGP ID Post protocol is a protocol which describes the use of PGP to
authenticate user posted content on a website.

1 INTRODUCTION
---------------

A large portion of websites today follow a registration-based model for
content validation, meaning that a user will register with their personal
creds. This allows them to use the service without authenticating
themselves before every action.

Though, they will usually be forced to enter their password when logging
into their account, and other security layers such as 2-factor auth if
they have enabled that.

This protocol however, deviates drastically from this model, and allows
for safer communication with the server.

1.1 Registering a new user
--------------------------

For this protocol, we assume that every user already has an OpenPGP key pair.
When a user wants to register to a new service, they send their public key
to the server. If the server can trust the key, using the OpenPGP trust
network, the user will get an encrypted, using OpenPGP, confirmation. The
new user is now registered with the service.

The server has now added the public key of the new user to its database. In
the future, signed messages from this user will be recognised as trusted.

1.1.1 Optional extra security
-----------------------------

The service may optionally generate an OpenPGP key pair per user, to which
the user may encrypt their messages in order to increase security.

1.1.2 Trust
-----------

If a barrier for registration is impractical for the service's purpose,
the user interface may show the level of trust of each user. This way
everyone may post content and users themselves may evaluate if they trust
the user.

Without a significant barrier of entry, spam might become a problem.

1.1.3 Revocation
----------------

The server will periodically check keyservers to evaluate if trusted keys
have been revoked in order to preserve the integrity of the database's
content.

1.2 Posting content
-------------------

As an example, we suppose that we have a service to which registered users
may post content. This content can be an image, text, an arbitrary file, etc.

To post new content, the user signs the content to be posted using PGP and
optionally encrypts it to the server's public key. Once uploaded, the server
will verify the signature. If the signature is good and trusted, the server
will process the message accordingly.

1.2.1 Duplicates
----------------

If someone attempts to upload a duplicate post, it will be skipped by the
server.

1.2.2 Time sensitivity
----------------------

Content with old signatures may be ignored by the server.

The "date uploaded" as seen on the user interface is the time and date on
which the signature was made.

1.2.3 Uploading content
-----------------------

Content may be uploaded via any secure protocol, e.g. HTTPS, SFTP, SCP or SSH.
If the content is also encrypted to the server's public key, even unencrypted
network protocols may be used, although this is not recommended.

1.2.4 Transparency
------------------

The server will make available the signature files to allow for other users
to verify the content individually. This allows users to confirm the
legitimacy of the server's content.

1.3 Benefits
------------

This protocol allows for most of the cryptographic calculations to be
executed on the client's computer, thanks to the OpenPGP protocol. As a
result, users don't need to trust the server as much as in the model
used by most other websites.
