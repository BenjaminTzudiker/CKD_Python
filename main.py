import psycopg2
import sys

#
# Main functions
#

# Attempts to connect to the database and return the cursor object, and exits if a connection can't be established
def connect(dbuser, dbpass, dbname, dbhost):
    try:
        global conn
        conn = psycopg2.connect("dbname='{name}' user='{user}' host='{host}' password='{password}'".format(user = dbuser, password = dbpass, name = dbname, host = dbhost))
        global cursor
        cursor = conn.cursor()
        return cursor
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

# Tries to run the query passed to the function, returning true if no exception was thrown
def runQuery(query):
    try:
        cursor.execute("{q}".format(q = query))
        return True
    except:
        print("Query execution failed for query:\n" + query)
        return False

#
# Setup helper functions
#

# Counts the maximum number of rows that link to the same key in the given column
def countMaxEntriesWithKeyColumn(column, table):
    cursor.fetchall()
    success = runQuery("select count(*) from {t} group by {c} order by count(*) limit 1".format(t = table, c = column))
    if success:
        return int(cursor.fetchone()[0])
    else:
        return 0

# Returns a tuble containing all the column names in a table
def getAllColumnNamesFromTable(table):
    cursor.fetchall()
    success = runQuery("select column_name from information_schema.columns where table_name = {t}".format(t = table))
    if success:
        return cursor.fetchone()
    else:
        return tuple()