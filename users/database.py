# ------------------------------------------------------------------------------
import sqlite3
import bcrypt
import os
import htpasswd
import re
from email.utils import parseaddr
from . import config

# ------------------------------------------------------------------------------
BCRYPT_ROUNDS = 5
database = config.DB_DATABASE
passwdfile = config.DB_PASSFILE

EMAIL_REGEX = re.compile(r"[^@ ]+@[^@ ]+\.[^@ ]+")


# ------------------------------------------------------------------------------
def mkEmptyDatabase(dbname):
    if os.path.isfile(dbname):
        os.remove(dbname)

    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("CREATE TABLE user ( "
              "uid INTEGER PRIMARY KEY AUTOINCREMENT, name text, "
              "passwd text, email text, enabled INTEGER NOT NULL DEFAULT 1, "
              "UNIQUE(name), UNIQUE(email))")
    conn.commit()

    conn.close()


# ------------------------------------------------------------------------------
def init():
    mkEmptyDatabase(database)

    if os.path.isfile(passwdfile):
        os.remove(passwdfile)

    open(passwdfile, 'w').close()

    insertUser(config.DB_TEST_USER, config.DB_TEST_PASS, config.DB_TEST_EMAIL)


# ------------------------------------------------------------------------------
def insertUser(name, passwd, email):
    checkedName, checkedEmail = parseaddr(email)
    if len(checkedEmail) == 0 or not EMAIL_REGEX.match(checkedEmail):
        return (False, "Invalid email %s" % email)

    h = bcrypt.hashpw(passwd, bcrypt.gensalt(BCRYPT_ROUNDS))

    conn = sqlite3.connect(database)
    try:
        with conn:
            conn.execute('INSERT INTO user(uid,name,passwd,email) '
                         'VALUES (null,?,?,?)',
                         (name, h, checkedEmail))
    except sqlite3.IntegrityError:
        return (False, "User '%s' Already Exists" % name)

    try:
        with htpasswd.Basic(passwdfile) as userdb:
            userdb.add(name, passwd)
    except htpasswd.basic.UserExists, e:
        return (False, "User '%s' Already Exists [%s]" % (name, str(e)))

    return (True, "")


# ------------------------------------------------------------------------------
def getUserEmail(name):
    conn = sqlite3.connect(database)
    try:
        with conn:
            c = conn.cursor()
            c.execute('SELECT email FROM user WHERE name=?', (name,))
            val = c.fetchone()
            return val[0]
    except:
        pass

    return None


# ------------------------------------------------------------------------------
def getUserName(uid):
    conn = sqlite3.connect(database)
    try:
        with conn:
            c = conn.cursor()
            c.execute('SELECT name FROM user WHERE uid=?', (uid,))
            val = c.fetchone()
            return val[0]
    except:
        pass

    return None


# ------------------------------------------------------------------------------
def checkUser(name, passwd):
    conn = sqlite3.connect(database)
    try:
        with conn:
            c = conn.cursor()
            c.execute('SELECT passwd FROM user '
                      'WHERE name=? AND enabled=1', (name,))
            val = c.fetchone()
            if val is not None:
                return bcrypt.hashpw(passwd, val[0]) == val[0]
    except:
        return False

    return False


# ------------------------------------------------------------------------------
def changeUserPassword(name, newpass):
    try:
        with htpasswd.Basic(passwdfile) as userdb:
            userdb.change_password(name, newpass)
    except htpasswd.basic.UserNotExists, e:
        return False

    h = bcrypt.hashpw(newpass, bcrypt.gensalt(BCRYPT_ROUNDS))

    conn = sqlite3.connect(database)
    try:
        with conn:
            conn.execute('UPDATE user SET passwd=? WHERE name=?', (h, name))
    except:
        return False

    return True


# ------------------------------------------------------------------------------
def checkIfUserAvailable(name):
    conn = sqlite3.connect(database)
    try:
        with conn:
            c = conn.cursor()
            c.execute('SELECT * FROM user WHERE name=?', (name,))
            val = c.fetchone()
            if val is None:
                return True
    except:
        return False

    return False


# ------------------------------------------------------------------------------
def enableUser(name):
    conn = sqlite3.connect(database)
    with conn:
        c = conn.cursor()
        c.execute('SELECT uid FROM user WHERE name=?', (name,))
        uidrow = c.fetchone()
        if uidrow is not None:
            c.execute('UPDATE user SET enabled=1 WHERE uid=?', (uidrow[0],))


# ------------------------------------------------------------------------------
def disableUser(name):
    conn = sqlite3.connect(database)
    with conn:
        c = conn.cursor()
        c.execute('SELECT uid FROM user WHERE name=?', (name,))
        uidrow = c.fetchone()
        if uidrow is not None:
            c.execute('UPDATE user SET enabled=0 WHERE uid=?', (uidrow[0],))


# ------------------------------------------------------------------------------
def deleteUser(name):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute('SELECT uid FROM user WHERE name=?', (name,))
    uidrow = c.fetchone()
    if uidrow is not None:
        uid = uidrow[0]

        c.execute('DELETE FROM user WHERE uid=?', (uid,))

        conn.commit()

    conn.close()

    try:
        with htpasswd.Basic(passwdfile) as userdb:
            userdb.pop(name)
    except htpasswd.basic.UserNotExists, e:
        pass


# ------------------------------------------------------------------------------
