#!/usr/bin/env python

# Description: This python program looks to copy a file of arbitrary size
#              using a byte buffer, and puts the new copy in a directory.  
# Run command: python3 experiment1.py filename

# Imports:
import sys
import os.path

# Step 1: Look for proper input on the command line.
print("~~~~Welcome to the Python jpg file copier!~~~~ ")
print("Checking for proper input on the command line.")
try:
    EnteredFilename = sys.argv[1]
except:
    sys.exit("Error: Input file not entered on the command line. Usage: python3 lab1.py filename.")

if not (os.path.exists(EnteredFilename) and os.path.isfile(EnteredFilename)):
    sys.exit("Error: Input file was not found on the system.  Usage: python3 lab1.py filename. ")

# Step 2: Check to see if a directory called recv exists, and if not, create one.
if not (os.path.exists("recv")):
    print("Note: File directory recv was not found, so will be created.")
    os.makedirs("recv")

# Step 3: Begin the file copying.  Create a new file with the same name, place it in recv, copy data, etc.
print("Proper input was found to be entered. Beginning file copy.")
NewFilepath = os.path.join("recv", EnteredFilename)
print("New file will be created at: " + NewFilepath)
if (os.path.exists(NewFilepath)):
    sys.exit("Critical Error: An existing file with the same name was found at the location.")
print("...Working...")
with open(EnteredFilename, "rb") as old_file:
    with open(NewFilepath, "wb") as new_file:
        while True:
            bytechunk = old_file.read(960)
            if bytechunk:
                new_file.write(bytechunk)
            else: break

# Step 4: Close the files used, check for accuracy of the newly created file.
print("Copied file has been created and placed in directory recv. Cleaning up.")
old_file.close()
new_file.close()
