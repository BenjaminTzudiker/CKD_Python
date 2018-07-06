from main import *

# Set these values to those used by your database
dbuser = "benjamintzudiker"
dbpass = ""
dbname = "ckd"
dbhost = "localhost"

# Attempts to connect to the database
cursor = connect(dbuser, dbpass, dbname, dbhost)

if runQuery("select * from site_source"):
    for row in cursor.fetchall():
        print(row)

# Closes the database connection
close()