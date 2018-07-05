import psycopg2

# Set these values to those used by your database
dbuser = "postgres"
dbpass = "postgres"
dbname = "ckd"
dbhost = "localhost"

# Attempt to connect to the database
try:
    conn = psycopg2.connect("dbname='{name}' user='{user}' host='{host}' password='{pw}'".format(user = dbuser, pw = dbpass, name = dbname, host = dbhost))
except:
    print("Database connection failed.")
    sys.exit()

# Create a cursor from the database connection
cursor = conn.cursor()