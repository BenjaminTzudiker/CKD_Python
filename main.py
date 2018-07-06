import psycopg2
import sys

# Attempts to connect to the database, and exits if a connection can't be established
def connect(dbuser, dbpass, dbname, dbhost):
    try:
        global conn
        conn = psycopg2.connect("dbname='{name}' user='{user}' host='{host}' password='{password}'".format(user = dbuser, password = dbpass, name = dbname, host = dbhost))
        global cursor
        cursor = conn.cursor()
    except:
        print("Database connection failed, check database information specified in run.py python file.")
        print("Exiting...")
        sys.exit()

# Attempts to close the connection to the database
def close():
    try:
        global cursor
        cursor.close()
        global conn
        conn.close()
    except:
        print("Failed to close database connection.")

# Tries to run the query passed to the function
def runQuery(query):
    try:
        cursor.execute("""{q}""".format(q = query))
        return True
    except:
        print("Query execution failed for query:\n" + query)
        return False

# Counts the maximum number of rows that link to the same key in the given column
def countMaxEntriesWithKeyColumn(column, table):
    cursor.fetchall()
    runQuery("select count(*) from {t} group by {c} order by count(*) limit 1".format(t = table, c = column))
    return int(cursor.fetchone()[0])