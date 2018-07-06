# CKD Export

* Python
  * Common Problems
* File Descriptions

## Python

### Common Problems

#### Permission denied when trying to run shell script

Run the command `chmod a+x <path_to_shell>` to gain permission to run the script. You can also simply copy and paste the contents of the script into the command line, although you'll need to manually specify paths or cd to correct locations.

## File Descriptions

./main.py
Backend python script that contains functions needed in run.py. Handles database communication and file writing.

./readme.md
Markdown file that contains information on setting up and using the export scripts. It also contains this sentence.

./run.bat
Batch script that runs run.py.

./run.py
Contains the information that describes how the export should take place, and calls the relevant functions in main.py.

./run.dh
Shell script that runs run.py.