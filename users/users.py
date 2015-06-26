# ------------------------------------------------------------------------------
from . import database as db


# ------------------------------------------------------------------------------
def checkUser(username, passwd):
    return db.checkUser(username, passwd)


# ------------------------------------------------------------------------------
def checkIfUserAvailable(username):
    return db.checkIfUserAvailable(username)


# ------------------------------------------------------------------------------
def getUserEmail(username):
    return db.getUserEmail(username)


# ------------------------------------------------------------------------------
def allowPasswordChange(username):
    return True


# ------------------------------------------------------------------------------
def changeUserPassword(username, oldpass, newpass):
    return db.changeUserPassword(username, newpass)


# ------------------------------------------------------------------------------
