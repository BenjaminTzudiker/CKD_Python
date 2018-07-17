import psycopg2
import sys
from progress.bar import Bar

# Default sentinel value for function default checking
default = object()

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

def run():
    """
    Attempts to run the export using the inforamtion given in tableInfo.
    """
    print("Starting export...")
    print("Counting entries...")
    query = "select count(*) from {t}"
    if not (tableInfo[0].where == None or tableInfo[0].where == ""):
        query += " where {w}"
    runQuery(query.format(t = tableInfo[0].name, w = tableInfo[0].where))
    entries = cursor.fetchall()[0][0]
    with open("export.csv", "w+") as file:
        print("Writing columns...")
        # Write column names to top of csv
        for table in tableInfo:
            for i in range(table.maxEntries):
                for column in table.columns:
                    if (not column == table.keyColumn) or (table.displayKeyColumn):
                        file.write(column.displayName + (str(i) if table.maxEntries > 1 else "") + ",")
        file.seek(file.tell() - 1)
        file.write("\n")
        print("Writing entries...")
        bar = Bar("Entries Completed", max = entries)
        for primaryKey in tableInfo[0].keyBuffer:
            for table in tableInfo:
                tableData = None
                if table.keyBuffer == None:
                    tableData = entryTableExportNoBufferData(table, primaryKey[0])
                elif len(table.keyBuffer) == 0:
                    tableData = entryTableExportNoBufferData(table, primaryKey[0])
                else:
                    pass
                for entryData in tableData:
                    for data in entryData:
                        file.write(str(data) + ",")
                file.write("," * ((table.maxEntries - len(tableData)) * len(tableData[0])))
            file.seek(file.tell() - 1)
            file.write("\n")
            bar.next()
    bar.finish()

def setupAddPrimaryTable(tableName, columnNames = default, keyColumnName = default, displayKeyColumn = True, where = None):
    """
    Stores the export settings for the primary table.
    
    Keyword arguments:
    tableName -- The name of the table, string
    columnNames -- The names of the columns that should be imported, string[] (default all column names in table)
    keyColumnName -- The name of the column used as the primary key for the table, string (default columnNames[0])
    displayKeyColumn -- If false, this will prevent the export from writing the table's key column, boolean (default True)
    where -- Optionally the statement in a where query used to limit the rows that are expored, string (default None)
    """
    if columnNames == default:
        columnNames = [col[0] for col in getAllColumnNamesFromTableName(tableName)]
    if keyColumnName == default:
        keyColumnName = columnNames[0]
    print("Setting up primary table {t}...".format(t = tableName))
    columns = [Column(col[0], col[0], col[1]) for col in getAllColumnNamesFromTableName(tableName) if col[0] in columnNames]
    keyColumn = getColumnFromName(keyColumnName, columns)
    table = Table(tableName, columns, keyColumn)
    table.displayKeyColumn = displayKeyColumn
    table.where = where
    query = "select {c} from {t}"
    if not (tableInfo[0].where == None or tableInfo[0].where == ""):
        query += " where {w}"
    runQuery(query.format(c = tableInfo[0].keyColumn.name, t = tableInfo[0].name, w = tableInfo[0].where))
    primaryKeys = cursor.fetchall()
    table.keyBuffer = tuple(key[0] for key in primaryKeys)
    if len(tableInfo) == 0:
        tableInfo.append(table)
    else:
        tableInfo[0] = table
    print("Primary table {t} added.".format(t = tableName))
    return table

def setupAddOneToOneTable(tableName, columnNames = default, keyColumnName = default, parentTableName = default, parentKeyColumnName = default, displayKeyColumn = True, keyBuffer = True):
    """
    Stores the export settings for a table with a one-to-one relationship to the parent table.
    
    Keyword arguments:
    tableName -- The name of the table, string
    columnNames -- The names of the columns that should be imported, string[] (default all column names in table)
    keyColumnName -- The name of the column used as the primary key for the table, string (default columnNames[0])
    parentTableName -- The name of the table that the key links to, string (default primary table name)
    parentKeyColumnName -- The name of the column in the parent table that contains the foreign keys, string (default keyColumnName)
    displayKeyColumn -- If false, this will prevent the export from writing the table's key column, boolean (default True)
    keyBuffer -- Toggles storing key values in memory which may speed up the export process, boolean (default True)
    """
    if columnNames == default:
        columnNames = [col[0] for col in getAllColumnNamesFromTableName(tableName)]
    if keyColumnName == default:
        keyColumnName = columnNames[0]
    if parentTableName == default:
        parentTableName = tableInfo[0].table.name
    if parentKeyColumnName == default:
        parentKeyColumnName = keyColumnName
    print("Setting up table {t}...".format(t = tableName))
    if not tableInfo[0] == None:
        columns = [Column(col[0], col[0], col[1]) for col in getAllColumnNamesFromTableName(tableName) if col[0] in columnNames]
        keyColumn = getColumnFromName(keyColumnName, columns)
        parentTable = getTableFromName(parentTableName)
        parentKeyColumn = getColumnFromName(parentKeyColumnName, parentTable.columns)
        table = Table(tableName, columns, keyColumn, parentTable, parentKeyColumn)
        table.maxEntries = parentTable.maxEntries
        print("Maximum entries under table: {e}".format(e = table.maxEntries))
        table.displayKeyColumn = displayKeyColumn
        if keyBuffer:
            print("Creating key buffer...")
            createKeyBuffer(table)
        tableInfo.append(table)
        print("Table {t} added.".format(t = tableName))
        return table
    else:
        raise NoPrimaryTableException()
        return None

def setupAddOneToManyTable(tableName, columnNames = default, keyColumnName = default, parentTableName = default, parentKeyColumnName = default, displayKeyColumn = True, keyBuffer = True):
    """
    Stores the export settings for a table with a one-to-many relationship to the primary table.
    
    Keyword arguments:
    tableName -- The name of the table, string
    columnNames -- The names of the columns that should be imported, string[] (default all column names in table)
    keyColumnName -- The name of the column used as the primary key for the table, string (default first column name in columnNames)
    parentTableName -- The name of the table that the key links to, string (default primary table name)
    parentKeyColumnName -- The name of the column in the parent table that contains the foreign keys, string (default keyColumnName)
    displayKeyColumn -- If false, this will prevent the export from writing the table's key column, boolean (default True)
    keyBuffer -- Toggles storing key values in memory which may speed up the export process, boolean (default True)
    """
    if columnNames == default:
        columnNames = [col[0] for col in getAllColumnNamesFromTableName(tableName)]
    if keyColumnName == default:
        keyColumnName = columnNames[0]
    if parentTableName == default:
        parentTableName = tableInfo[0].table.name
    if parentKeyColumnName == default:
        parentKeyColumnName = keyColumnName
    print("Setting up table {t}...".format(t = tableName))
    if not tableInfo[0] == None:
        columns = [Column(col[0], col[0], col[1]) for col in getAllColumnNamesFromTableName(tableName) if col[0] in columnNames]
        keyColumn = getColumnFromName(keyColumnName, columns)
        parentTable = getTableFromName(parentTableName)
        parentKeyColumn = getColumnFromName(parentKeyColumnName, parentTable.columns)
        table = Table(tableName, columns, keyColumn, parentTable, parentKeyColumn)
        table.maxEntries = countMaxEntriesWithKeyColumn(table)
        print("Maximum entries under table: {e}".format(e = table.maxEntries))
        table.displayKeyColumn = displayKeyColumn
        if keyBuffer:
            print("Creating key buffer...")
            createKeyBuffer(table)
        tableInfo.append(table)
        print("Table {t} added.".format(t = tableName))
        return table
    else:
        raise NoPrimaryTableException()
        return None

#
# Setup helpers
#

class Column:
    """
    Stores information about a column that is needed to export it.
    """
    def __init__(self, n = "", dispn = default, t = "variable character"):
        if dispn == default:
            dispn = n
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
        self.displayKeyColumn = True
        self.maxEntries = 1
        self.where = None
        self.keyBuffer = tuple()

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
    for table in collection:
        if table.name == name:
            return table
    else:
        print("No table with name " + name + " found.")
        return None

def getColumnFromName(name, collection):
    """
    Searches the collection for a column with the specified name.
    
    Accepts the name of the column as a string and the collection to search. Returns the first column object found with that name, or None if a column with that name isn't found.
    """
    for column in collection:
        if column.name == name:
            return column
    else:
        print("No column with name " + name + " found.")
        return None

def createKeyBuffer(table):
    pass

def createKeyBufferQueryConstructor(table):
    pass

def entryTableExportData(table, primaryKey):
    pass

def entryTableExportNoBufferData(table, primaryKey):
    """
    Returns a list containing the entries for a table to be written to the exported csv file.
    
    Accepts the exported table as a table object and the primary key in the primary table. Returns a list of tuples (one tuple for each matching entry) if the query succeeds, or None if the query fails.
    """
    success = runQuery(entryTableExportDataNoBufferQueryConstructor(table, primaryKey))
    if success:
        return cursor.fetchall()
    else:
        return None

def entryTableExportDataNoBufferQueryConstructor(table, primaryKey, count = 0):
    """
    Recursive helper function used to construct the query for entryTableExportData.
    """
    if count == 0:
        columns = table.columns
        if not table.displayKeyColumn:
            try:
                columns.remove(table.keyColumn)
            except:
                print("Key column {c} not found in table {t}.".format(c = table.keyColumn.name, t = table.name))
        return "select {c} from {t} as {ta} where {q}".format(t = table.name, c = ", ".join(countKeyColumnAlias() + "." + column.name for column in columns), ta = countKeyColumnAlias(), q = entryTableExportDataQueryConstructor(table, primaryKey, count + 1))
    elif (table == tableInfo[0] or table.parentTable == None):
        return "{ta}.{c} = {value}".format(ta = countKeyColumnAlias(count - 1), c = table.keyColumn.name, value = "{quotes}{v}{quotes}".format(v = primaryKey, quotes = "," if table.keyColumn.type == "variable character" else ""))
    else:
        return "exists(select 1 from {ref} as {refa} where {ta}.{c} = {refa}.{refc} and {q})".format(ref = table.parentTable.name, refa = countKeyColumnAlias(count), ta = countKeyColumnAlias(count - 1), c = table.keyColumn.name, refc = table.parentKeyColumn.name, q = entryTableExportDataQueryConstructor(table.parentTable, primaryKey, count + 1))

def countMaxEntriesWithKeyColumn(table):
    """
    Counts the maximum number of rows that link to the same key in the primary table.
    
    Accepts the table as a table object. Returns the number of lines as an int if the query succeeds, or zero if the query fails.
    """
    success = runQuery(countMaxEntriesWithKeyColumnQueryConstructor(table))
    if success:
        return int(cursor.fetchone()[0])
    else:
        return 0

def countMaxEntriesWithKeyColumnQueryConstructor(table, originalTable = default, count = 0):
    """
    Helper function used to construct the query for countMaxEntriesWithKeyColumn.
    """
    if originalTable == default:
        originalTable = table
    if count == 0:
        return "select count({ta}.{c}) from {t} as {ta}".format(t = table.name, c = table.keyColumn.name, ta = countKeyColumnAlias()) + countMaxEntriesWithKeyColumnQueryConstructor(table, originalTable, count + 1)
    elif (table == tableInfo[0] or table.parentTable == None):
        return " group by {ta}.{c} order by count({origta}.{origc}) desc limit 1".format(ta = countKeyColumnAlias(count - 1), c = table.keyColumn.name, origta = countKeyColumnAlias(), origc = originalTable.keyColumn.name)
    else:
        return "{w} inner join {ref} as {refa} on {ta}.{c} = {refa}.{refc}".format(w = " where {q}".format(q = table.where) if not (table.where == "" or table.where == None) else "", ref = table.parentTable.name, c = table.keyColumn.name, refc = table.parentKeyColumn.name, refa = countKeyColumnAlias(count), ta = countKeyColumnAlias(count - 1)) + countMaxEntriesWithKeyColumnQueryConstructor(table.parentTable, originalTable, count + 1)

def countKeyColumnAlias(count = 0):
    """
    Recursive helper function used to get alias names for countMaxEntriesWithKeyColumnQueryConstructor.
    """
    return "z" * (count + 1)

def getAllColumnNamesFromTableName(tableName):
    """
    Returns a tuble containing all the column names and data types in a table.
    
    Accepts the table name as a string. Returns a tuple with one tuple entry per column (each containing the name and data type as strings), or an empty tuple if the query fails.
    """
    success = runQuery("select column_name, data_type from information_schema.columns where table_name = '{t}'".format(t = tableName))
    if success:
        return cursor.fetchall()
    else:
        return tuple()
