#!/usr/bin/python
""" Command tool to insert a new user in the database.
"""

# -----------------------------------------------------------------------------
import sys
from users import database as db


# -----------------------------------------------------------------------------
def main():
    if len(sys.argv) == 4:
        name = sys.argv[1]
        passwd = sys.argv[2]
        email = sys.argv[3]
        db.insertUser(name, passwd, email)
    else:
        print "Usage: %s username passwd email" % sys.argv[0]


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

# ------------------------------------------------------------------------------
