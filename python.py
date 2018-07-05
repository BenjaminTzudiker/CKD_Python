import psycopg2
import sys

# Set these values to those used by your database
dbuser = "benjamintzudiker"
dbpass = ""
dbname = "ckd"
dbhost = "localhost"

# Attempt to connect to the database
try:
    conn = psycopg2.connect("dbname='{name}' user='{user}' host='{host}' password='{pw}'".format(user = dbuser, pw = dbpass, name = dbname, host = dbhost))
except:
    print("Database connection failed, check database information specified in main python file.")
    print("Exiting...")
    sys.exit()

# Create a cursor from the database connection
cursor = conn.cursor()

# Tries to run the query passed to the function
def runQuery(query):
    try:
        cursor.execute("""{q}""".format(q = query))
        return True
    except:
        print("Query execution failed for query:\n" + query)
        return False

runQuery("select * from site_source;")
for row in cursor.fetchall():
    print(row)