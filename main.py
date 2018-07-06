import psycopg2
import sys

# Contains the Table instances used to store export information. tableInfo[0] contains the primary table.
tableInfo = []

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
    except Exception as e:
        print("Query execution failed for query:\n" + query + "\n" + str(e))
        return False

#
# Run.py setup functions
#

def setupAddPrimaryTable(table, columns = [Column(col[0], col[0], col[1]) for col in getAllColumnNamesFromTable(table)], keyColumn = columns[0], parentTable = tableInfo[0].table, parentKeyColumn = keyColumn):
    pass

def setupAddOneToOneTable(table, columns = [Column(col[0], col[0], col[1]) for col in getAllColumnNamesFromTable(table)], keyColumn = columns[0], parentTable = tableInfo[0].table, parentKeyColumn = keyColumn):
    pass

def setupAddOneToManyTable(table, columns = [Column(col[0], col[0], col[1]) for col in getAllColumnNamesFromTable(table)], keyColumn = columns[0], parentTable = tableInfo[0].table, parentKeyColumn = keyColumn):
    pass

#
# Setup helpers
#

class Column:
    """
    Stores information about a column that is needed to export it.
    """
    def __init__(self, n = "", dispn = n, t = "variable character"):
        self.name = n
        self.displayName = dispn
        self.type = t

class Table:
    """
    Stores information about a table that is needed to export it.
    """
    def __init__(self, n = "", col = [], key = None, ref = None, refKey = None):
        self.name = n
        self.columns = col
        self.keyColumn = key
        self.parentTable = ref
        self.parentKeyColumn = refKey
        self.displayKeyColumn = False
        self.numberColumns = False

class TableCreationException(Exception):
    """
    Custom exception thrown when incorrect table information is supplied to table setup functions.
    """
    pass

def getTableFromName(name, collection = tableInfo):
    """
    Searches the collection for a table with the specified name.
    
    Accepts the name of the table as a string, optionally with a specific collection to search (defaults to tableInfo). Returns the first table object found with that name, or None if a table with that name isn't found.
    """
    return next(table for table in collection if table.name == name)

def getColumnFromName(name, collection):
    """
    Searches the collection for a column with the specified name.
    
    Accepts the name of the column as a string and the collection to search. Returns the first column object found with that name, or None if a column with that name isn't found.
    """
    return next(column for column in collection if column.name == name)

def countMaxEntriesWithKeyColumn(table, column):
    """
    Counts the maximum number of rows that link to the same key.
    
    Accepts the names of the table and column as strings. Returns the number of lines as an int if the query succeeds, or zero if the query fails.
    """
    cursor.fetchall()
    success = runQuery("select count(*) from {t} group by {c} order by count(*) limit 1".format(t = table, c = column))
    if success:
        return int(cursor.fetchone()[0])
    else:
        return 0

def getAllColumnNamesFromTable(table):
    """
    Returns a tuble containing all the column names and data types in a table.
    
    Accepts the name of the table as a string. Returns a tuple with one tuple entry per column (each containing the name and data type as strings), or an empty tuple if the query fails.
    """
    cursor.fetchall()
    success = runQuery("select column_name, data_type from information_schema.columns where table_name = '{t}'".format(t = table))
    if success:
        return cursor.fetchall()
    else:
        return tuple()