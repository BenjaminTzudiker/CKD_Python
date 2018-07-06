import psycopg2
import sys

export = []

#
# Main functions
#

def connect(dbuser, dbpass, dbname, dbhost):
    """
    Attempts to connect to the database.
    
    Accepts the username and password along with the host and database name (all as strings). Returns the cursor object if the connection succeeds, or attempts to exit the script (and returns None) if an exception is thrown.
    """
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
        return None

# Attempts to close the connection to the database
def close():
    try:
        global cursor
        cursor.close()
        global conn
        conn.close()
    except:
        print("Failed to close database connection.")

def runQuery(query):
    """
    Tries to run the query passed to the function.
    
    Accepts a string as the sql query (sans semicolon). Returns true if the query execution does not throw an exception, or false if an exception is thrown.
    """
    try:
        cursor.execute("{q}".format(q = query))
        return True
    except:
        print("Query execution failed for query:\n" + query)
        return False

#
# Setup helper functions
#

def countMaxEntriesWithKeyColumn(column, table):
    """
    Counts the maximum number of rows that link to the same key.
    
    Accepts the name of the column and table as strings. Returns the number of lines as an int if the query succeeds, or zero if the query fails.
    """
    cursor.fetchall()
    success = runQuery("select count(*) from {t} group by {c} order by count(*) limit 1".format(t = table, c = column))
    if success:
        return int(cursor.fetchone()[0])
    else:
        return 0

def getAllColumnNamesFromTable(table):
    """
    Returns a tuble containing all the column names in a table.
    
    Accepts the name of the table as a string. Returns a tuple containing the names of all the columns as strings, or an empty tuple if the query fails.
    """
    cursor.fetchall()
    success = runQuery("select column_name from information_schema.columns where table_name = {t}".format(t = table))
    if success:
        return cursor.fetchone()
    else:
        return tuple()