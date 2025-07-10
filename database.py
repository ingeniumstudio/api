import os

from piccolo.engine.sqlite import SQLiteEngine
from piccolo.table import Table, create_db_tables
from piccolo.columns import Varchar

import secret_config

SQLITE_FILE_NAME = secret_config.SQLITE_FILE_NAME

DB_FILE_DELETE_IF_EXISTS = True  # recreate db file

if DB_FILE_DELETE_IF_EXISTS and os.path.isfile(SQLITE_FILE_NAME):
    os.remove(SQLITE_FILE_NAME)

DB = SQLiteEngine(path=SQLITE_FILE_NAME)


class Text(Table, db=DB):
    text = Varchar()

class Post(Table, db=DB):
    text = Varchar()

class User(Table, db=DB):
    username = Varchar()
    password = Varchar()
