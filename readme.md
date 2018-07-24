# CKD Export

* Python
  * Run.py
    * Connecting to the Database
    * Setting up the Primary Table
    * Setting up the Secondary Tables
  * Common Problems
* File Descriptions

## Python

### Run.py

#### Connecting to the Database

To start, you will need to connect to the database. The top of the run file should contain something akin to the following:

```python
dbuser = "benjamintzudiker"
dbpass = ""
dbname = "ckd"
dbhost = "localhost"

cursor = connect(dbuser, dbpass, dbname, dbhost)
```

This will connect to the specified postgres database using the information you provide. If it can't connect to the database, it will exit - if this happens, double check that the information supplied is correct and that postgres is running.

The dbuser and dbpass are the username and password for the database user you want to connect as - some export options require (temporary) table creation priveleges, so if you'd like to use them make sure you connect as a user that can perform those operations. The dbname is the name of the database you'd like to connect to. The dbhost will probably be localhost unless you're connecting to a database on a different computer.

#### Setting up the Primary Table

You now need to specify which tables you want to export. To begin, you will need a primary table, which should contain at least one unique identifier column. This is the table that all other tables are referenced based on, directly or indirectly. For the CKD database, this will often end up being the patient table, using the patient_id column as the unique identifier. Use the code below to set up a basic primary table:

```python
setupAddPrimaryTable("patient", keyColumnName = "patient_id")
```

This tells the export script to look for a table in the database called "patient", and to use the "patient_id" column as the unique identifier. There are, however, more possible settings. Say we wanted to only take the patient_id and country columns. We could specify that using the columnNames argument:

```python
setupAddPrimaryTable("patient", keyColumnName = "patient_id", columnNames = ["patient_id", "country"])
```

Without specifying the column names, the script will default to exporting all the columns in the table.

We can also tell the export script to filter which rows in the primary table get exported using the whereInclude argument. The argument should be a string containing the body of a where statement. Only rows from the primary table that match that where statement are included. Say we only want patient IDs under a certain value. We can do that like so:

```python
setupAddPrimaryTable("patient", keyColumnName = "patient_id", whereInclude = "{alias}patient_id < 3350000")
```

Note the use of {alias}. This will automatically get replaced with an alias (including the period separator) for the primary table to prevent any confusion with overlapping column names.

If instead of excluding rows based on a where clause you'd rather just mark them, you can use the whereMarkers argument. Using this argument, you can tell the export script to make a whole new column and mark it with true or false. To use it, you need to pass in a list of tuples, with each tuple corresponding to one marker. The first value in the marker is what you'd like to call the column in the exported file, and the second value is the where clause much like in the example above. Rows that meet the where clause will have 1 in the created column, while those that don't will have 0. For example, if you wanted to instead mark all patients with an ID under 3350000:

```python
setupAddPrimaryTable("patient", keyColumnName = "patient_id", whereMarkers = [("is_under_id_max","{alias}patient_id < 3350000")])
```

#### Setting up the Secondary Tables

Next you'll need to add all the secondary tables. Each of these tables has a "parent" table that informs the export script which row in the export to place each entry under. This parent table doesn't have to be the primary table, but every secondary table should be related to the primary table eventually. Every secondary table has a key column much like the primary table, but this key column is just used to join the table to its parent and doesn't have to be unique. For example, if you have the primary table patient and secondary table encounter where each encounter has a foreign key patient_id, the patient_id column would be the key column. A basic secondary table can be added like so:

```python
setupAddSecondaryTable("encounter", keyColumnName = "patient_id", parentTableName = "patient", parentKeyColumnName = "patient_id")
```

The table name and key column are defined like before. The name of the parent table and the column in the parent table that our key column references are then also defined. Columns can also be chosen in the same manner as with primary tables:

```python
setupAddSecondaryTable("encounter", keyColumnName = "patient_id", columnNames = ["encounter_id", "encounter_date", "department_id"] parentTableName = "patient", parentKeyColumnName = "patient_id")
```

If order matters, you can tell the export script to order the entries in an exported row using the orderBy argument. This takes a list of tuples, each tuple containing the column name as a string and a boolean value (True means ascending, False means descending). You can specify as many columns as you want by adding multiple tuples to the list, and tuples that come earlier in the list take priority over tuples that come later. We can use the following line of code if we want earlier encounters to be written further to the left in the export:

```python
setupAddSecondaryTable("encounter", keyColumnName = "patient_id", parentTableName = "patient", parentKeyColumnName = "patient_id", orderBy = [("encounter_date", True)])
```

Call the setAddSecondaryTable function once for each secondary table you'd like to add, making sure to add child tables after their parents (and by extension, the primary table before the secondary tables).

### Common Problems

#### Permission denied when trying to run shell script

Run the command `chmod a+x <path_to_shell>` to gain permission to run the script. You can also simply copy and paste the contents of the script into the command line, although you may need to manually specify paths/cd to correct locations.

#### Query execution failed while running script

This could be caused by lots of things, but it most likely has to do with 

## File Descriptions

./install.bat 
Batch script that attempts to install python dependencies.

./install.sh 
Shell script that attempts to install python dependencies.

./main.py 
Backend python script that contains functions needed in run.py. Handles database communication and file writing among other things.

./readme.md 
Markdown file that contains information on setting up and using the export scripts. It also contains this sentence.

./run.bat 
Batch script that runs run.py.

./run.py 
Contains the information that describes how the export should take place, and calls the relevant functions in main.py.

./run.sh 
Shell script that runs run.py.