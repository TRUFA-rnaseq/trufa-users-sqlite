#-------------------------------------------------------------------------------
import sqlite3
import bcrypt
import os
import htpasswd
import re
from email.utils import parseaddr
import config

#-------------------------------------------------------------------------------
BCRYPT_ROUNDS = 5
database = config.DB_DATABASE
passwdfile = config.DB_PASSFILE

EMAIL_REGEX = re.compile(r"[^@ ]+@[^@ ]+\.[^@ ]+")

#-------------------------------------------------------------------------------
def mkEmptyDatabase( dbname ):
    if os.path.isfile( dbname ):
        os.remove( dbname )

    conn = sqlite3.connect( dbname )
    c = conn.cursor()
    c.execute( "CREATE TABLE user (uid INTEGER PRIMARY KEY AUTOINCREMENT, name text, passwd text, email text, enabled INTEGER NOT NULL DEFAULT 1, UNIQUE(name), UNIQUE(email))" )
    conn.commit()

    conn.close()

#-------------------------------------------------------------------------------
def init():
    mkEmptyDatabase( database )

    if os.path.isfile( passwdfile ):
        os.remove( passwdfile )

    open( passwdfile, 'w' ).close()

    insertUser( config.DB_TEST_USER, config.DB_TEST_PASS, config.DB_TEST_EMAIL )

#-------------------------------------------------------------------------------
def insertUser( name, passwd, email ):
    checkedName, checkedEmail = parseaddr( email )
    if len( checkedEmail ) == 0 or not EMAIL_REGEX.match( checkedEmail):
        return (False, "Invalid email %s" % email )

    h = bcrypt.hashpw( passwd, bcrypt.gensalt(BCRYPT_ROUNDS) )

    conn = sqlite3.connect( database )
    try:
        with conn:
            conn.execute( 'INSERT INTO user(uid,name,passwd,email) VALUES (null,?,?,?)',
                          (name,h,checkedEmail) )
    except sqlite3.IntegrityError:
        return (False, "User '%s' Already Exists" % name )

    try:
        with htpasswd.Basic( passwdfile ) as userdb:
            userdb.add( name, passwd )
    except htpasswd.basic.UserExists, e:
        return (False, "User '%s' Already Exists [%s]" % (name, str(e)) )

    return (True,"")

#-------------------------------------------------------------------------------
