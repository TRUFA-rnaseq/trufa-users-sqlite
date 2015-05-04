#!/usr/bin/python

#-------------------------------------------------------------------------------
import sys
import config
import database

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 4:
        name = sys.argv[1]
        passwd = sys.argv[2]
        email = sys.argv[3]
        database.insertUser( name, passwd, email )
    else:
        print "Usage: %s username passwd email" % sys.argv[0]

#-------------------------------------------------------------------------------
