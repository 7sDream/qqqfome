import os
import sqlite3
import json
import logging
import datetime

from zhihu import Author, ZhihuClient

from . import common as c
from . import strings as s

L = logging.getLogger('qqqufome-db')


def set_logger_level(level):
    c.check_type(level, 'level', logging.NOTSET)
    global L
    L.setLevel(level)


def set_logger_handle(handle):
    L.addHandler(handle)


def author_to_db_filename(author):
    c.check_type(author, 'author', Author)

    return author.id + '.sqlite3'


def create_db(author):
    c.check_type(author, 'author', Author)

    filename = author_to_db_filename(author)

    L.info(s.log_get_user_id.format(filename))

    if os.path.isfile(filename):
        e = FileExistsError()
        e.filename = filename
        raise e

    L.info(s.log_db_not_exist_create.format(filename))

    db = sqlite3.connect(author_to_db_filename(author))

    L.info(s.log_connected_to_db.format(filename))

    return db


def connect_db(database):
    c.check_type(database, 'database', str)

    if not os.path.isfile(database):
        e = FileNotFoundError()
        e.filename = database
        raise e

    return sqlite3.connect(database)


def create_table(db: sqlite3.Connection):
    c.check_type(db, 'db', sqlite3.Connection)

    L.info(s.log_create_table_in_db)
    with db:
        db.execute(
            '''
           CREATE TABLE followers
           (
           id       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           name     TEXT            NOT NULL,
           in_name  TEXT            NOT NULL
           );
           '''
        )

        db.execute(
            """
           CREATE TABLE meta
           (
           id       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           name     TEXT            NOT NULL,
           in_name  TEXT            NOT NULL,
           cookies  TEXT            NOT NULL
           );
            """
        )

        db.execute(
            """
           CREATE TABLE log
           (
           id               INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
           time             DATETIME        NOT NULL,
           follower_number  INT             NOT NULL,
           increase         INT             NOT NULL,
           message          TEXT            NOT NULL
           );
            """
        )
    L.info(s.success)


def add_user_to_db(db, author):
    c.check_type(db, 'db', sqlite3.Connection)
    c.check_type(author, 'author', Author)

    with db:
        L.debug(s.log_add_user_to_db.format(author.name))
        db.execute(
            """
            INSERT INTO followers
            (name, in_name) VALUES
            ( ?,      ?   );
            """,
            (author.name, author.id)
        )


def dump_init_data_to_db(db, author):
    c.check_type(db, 'db', sqlite3.Connection)
    c.check_type(author, 'author', Author)

    # meta data
    with db:
        name = author.name
        in_name = author.id
        cookies = json.dumps(author._session.cookies.get_dict())

        db.execute(
            """
            INSERT INTO meta
            (name,    in_name,   cookies) VALUES
            (  ?,        ?,         ?   );
            """,
            (name, in_name, cookies)
        )

    # followers
    L.info(s.log_start_get_followers.format(author.name))
    with db:
        for _, follower in zip(range(100), author.followers):
            add_user_to_db(db, follower)

    # log
    with db:
        log_to_db(db, author.follower_num, s.log_db_init)


def is_db_closed(db):
    c.check_type(db, 'db', sqlite3.Connection)

    try:
        with db:
            db.execute(
                """
                SELECT name from sqlite_master where type = 'table';
                """
            )
        return False
    except sqlite3.ProgrammingError:
        return True


def close_db(db):
    c.check_type(db, 'db', sqlite3.Connection)

    if not is_db_closed(db):
        db.close()
        L.info(s.log_close_db)


def get_cookies(db):
    c.check_type(db, 'db', sqlite3.Connection)

    cursor = db.execute('SELECT cookies from meta')

    row = cursor.fetchone()

    if row is None:
        return None

    return row[0]


def log_to_db(db, follower_num, message):
    c.check_type(db, 'db', sqlite3.Connection)
    c.check_type(follower_num, 'follower_num', int)
    c.check_type(message, 'message', str)

    cursor = db.execute(
        """
        SELECT follower_number FROM log ORDER BY id DESC;
        """
    )

    row = cursor.fetchone()

    if row:
        increase = follower_num - row[0]
    else:
        # first log
        increase = 0

    with db:
        db.execute(
            """
            INSERT INTO log
            (time, follower_number, increase, message) VALUES
            ( ?,           ?,           ?,       ?   );
            """,
            (datetime.datetime.now(), follower_num, increase, message)
        )


def is_in_db(db, in_name):
    c.check_type(db, 'db', sqlite3.Connection)
    c.check_type(in_name, 'in_name', str)

    with db:
        cursor = db.execute(
            """
            SELECT * FROM followers WHERE in_name = ?;
            """,
            (in_name,)
        )

        row = cursor.fetchone()

        return row is not None
