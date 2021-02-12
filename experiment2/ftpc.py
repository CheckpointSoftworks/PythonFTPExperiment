#!/usr/bin/env python

# Student: Ian Weber [weber.595@osu.edu]
# Date: September 17, 2015
# Assignment: CSE3461 Lab 2 (client part)


# Echo client program
import socket
import sys
import os
import os.path
import struct

# Step 1: Try to conect to host at port specified.
try:
    RemoteIP = sys.argv[1]
except:
    sys.exit("Error: Remote IP not entered on the command line. (Try 164.107.113.20 for gamma.)")
try:
    PortNumber = int(sys.argv[2])
except:
    sys.exit("Error: Port number not entered on the command line.")
try:
    Filename = sys.argv[3]
except:
    sys.exit("Error: Filename not entered on the command line.")
print("Now trying to connect to host on port specified...")
HOST = RemoteIP   
PORT = PortNumber      
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Successfully connected to host on port specified!")

# Step 2: Start the data tranfer. First, transfer the name and size of the file
print("Now attempting metadata transfer of file specified...")
if not (os.path.exists(Filename) and os.path.isfile(Filename)):
    sys.exit("Error: Input file was not found on the system.")
Filesize = struct.pack("I",os.path.getsize(Filename))
OriginalFilename = Filename
s.send(Filesize)
Filename = struct.pack("20s",bytes(Filename,'utf-8'))
s.send(Filename)
print("Metadata sent to server.  Now beginning data transfer...")

# Step 3: Continue data transfer. Now, transfer the file itself.
transferfile=open(OriginalFilename, "rb") 
transferbits = transferfile.read(960)
while (transferbits):
    print("sent")
    s.send(transferbits)
    sleep(.5)
    transferbits = transferfile.read(960)
print("File successfully transferred to server.  Check using diff.")
transferfile.close()
s.close()
