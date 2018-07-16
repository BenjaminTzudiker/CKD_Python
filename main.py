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

def setupAddPrimaryTable(tableName, columnNames = [col[0] for col in getAllColumnNamesFromTable(tableName)], keyColumnName = columns[0], where = None):
    """
    Stores the export settings for the primary table.
    
    Keyword arguments:
    tableName -- The name of the table, string
    columnNames -- The names of the columns that should be imported, string[] (default all column names in table)
    keyColumnName -- The name of the column used as the primary key for the table, string (default columnNames[0])
    where -- Optionally the statement in a where query used to limit the rows that are expored, string (default None)
    """
    try:
        table = Table(tableName, columns, keyColumn)
        tableInfo[0] = table
        return table
    except:
        raise TableCreationException()
        return None

def setupAddOneToOneTable(tableName, columnNames = [col[0] for col in getAllColumnNamesFromTable(tableName)], keyColumnName = columns[0], parentTableName = tableInfo[0].table.name, parentKeyColumnName = keyColumnName, where = None):
    """
    Stores the export settings for a table with a one-to-one relationship to the parent table.
    
    Keyword arguments:
    tableName -- The name of the table, string
    columnNames -- The names of the columns that should be imported, string[] (default all column names in table)
    keyColumnName -- The name of the column used as the primary key for the table, string (default columnNames[0])
    parentTableName -- The name of the table that the key links to, string (default primary table name)
    parentKeyColumnName -- The name of the column in the parent table that contains the foreign keys, string (default keyColumnName)
    where -- Optionally the statement in a where query used to limit the rows that are expored, string (default None)
    """
    if not tableInfo[0] == None:
        try:
            columns = [Column(col[0], col[0], col[1]) for col in getAllColumnNamesFromTable(tableName) if col[0] in columnNames]
            keyColumn = getColumnFromName(keyColumnName, columns)
            parentTable = getTableFromName(parentTableName)
            parentKeyColumn = getColumnFromName(parentKeyColumnName, parentTable.columns)
            table = Table(tableName, columns, keyColumn, parentTable, parentKeyColumn)
            table.maxEntries = parentTable.maxEntries
            tableInfo.append(table);
            return table
        except:
            raise TableCreationException()
            return None
    else:
        raise NoPrimaryTableException()
        return None

def setupAddOneToManyTable(tableName, columnNames = [col[0] for col in getAllColumnNamesFromTable(tableName)], keyColumnName = columnNames[0], parentTableName = tableInfo[0].table.name, parentKeyColumnName = keyColumnName, where = None):
    """
    Stores the export settings for a table with a one-to-many relationship to the primary table.
    
    Keyword arguments:
    tableName -- The name of the table, string
    columnNames -- The names of the columns that should be imported, string[] (default all column names in table)
    keyColumnName -- The name of the column used as the primary key for the table, string (default first column name in columnNames)
    parentTableName -- The name of the table that the key links to, string (default primary table name)
    parentKeyColumnName -- The name of the column in the parent table that contains the foreign keys, string (default keyColumnName)
    where -- Optionally the statement in a where query used to limit the rows that are expored, string (default None)
    """
    if not tableInfo[0] == None:
        try:
            columns = [Column(col[0], col[0], col[1]) for col in getAllColumnNamesFromTable(tableName) if col[0] in columnNames]
            keyColumn = getColumnFromName(keyColumnName, columns)
            parentTable = getTableFromName(parentTableName)
            parentKeyColumn = getColumnFromName(parentKeyColumnName, parentTable.columns)
            table = Table(tableName, columns, keyColumn, parentTable, parentKeyColumn)
            table.maxEntries = countMaxEntriesWithKeyColumn(table, keyColumn)
            if parentTable == tableInfo[0].table and parentKeyColumn == tableInfo[0].table.keyColumn:
                pass
            else:
                pass
            tableInfo.append(table);
            return table
        except:
            raise TableCreationException()
            return None
    else:
        raise NoPrimaryTableException()
        return None

def run():
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
        self.maxEntries = 1

class TableCreationException(Exception):
    """
    Custom exception thrown when incorrect table information is supplied to table setup functions.
    """
    pass

class NoPrimaryTableException(Exception):
    """
    Custom exception thrown when secondary tables are added without a primary table.
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

'''def countMaxEntriesWithKeyColumnPrimary(table, column):
    """
    Counts the maximum number of rows that link to the same primary key.
    
    Accepts the table and column as table and column objects. Returns the number of lines as an int if the query succeeds, or zero if the query fails.
    """
    cursor.fetchall()
    success = runQuery("select count(*) from {t} group by {c} order by count(*) limit 1".format(t = table.name, c = column.name))
    if success:
        return int(cursor.fetchone()[0])
    else:
        return 0'''

def countMaxEntriesWithKeyColumn(table, keyColumn):
    """
    Counts the maximum number of rows that link to the same key in the primary table.
    
    Accepts the table and column as table and column objects. Returns the number of lines as an int if the query succeeds, or zero if the query fails.
    """
    cursor.fetchall()
    nextTable = table
    query = "select count(*) from {t}".format(t = table.name, c = column.name)
    while not (nextTable == None or nextTable == tableInfo[0]):
        query = query + "()".format()
        nextTable = nextTable.parentTable
    query = query + " group by {c} order by count(*) limit 1"
    success = runQuery("")
    if success:
        return int(cursor.fetchone()[0])
    else:
        return 0

def countMaxEntriesWithKeyColumnHelper(table, keyColumn):
    if (table.parentTable == tableInfo[0] or table == tableInfo[0] or table.parentTable == None):
        return ""
    else:
        return " where ()"

def getAllColumnNamesFromTable(tableName):
    """
    Returns a tuble containing all the column names and data types in a table.
    
    Accepts the table name as a string. Returns a tuple with one tuple entry per column (each containing the name and data type as strings), or an empty tuple if the query fails.
    """
    cursor.fetchall()
    success = runQuery("select column_name, data_type from information_schema.columns where table_name = '{t}'".format(t = tableName))
    if success:
        return cursor.fetchall()
    else:
        return tuple()