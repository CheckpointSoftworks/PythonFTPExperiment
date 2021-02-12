#!/usr/bin/env python

# Imports
import socket
import sys
import os.path
import struct

# Step 1: Run the server on the port specified by the user.
print("Now trying to begin server...")
try:
    EnteredPort = int(sys.argv[1])
except:
    sys.exit("Error: Port number not entered on the command line.")
HOST = 'gamma'
PORT = EnteredPort
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
print("Server started succesfully on gamma on port",EnteredPort,". Now waiting for client...")
# Step 1.5: Wait for a connection.
s.listen(1)
conn, addr = s.accept()
print ("Server successfully connected to by", addr)

# Step 2: Deal with receiving the file name and size first (metadata)
Filesize = struct.unpack("I",conn.recv(4))
print("Request received to transfer a file of size:",Filesize[0],"bytes")
Filename = conn.recv(20)
Filename = struct.unpack("20s",Filename)
NewFilename = Filename[0].decode('utf-8')
print("with a name of",Filename[0].decode('utf-8'))
print("Now beginning file transfer...")

# Step 3: Now deal with receiving the actual file itself. Description...
# Create the directory recv if it does not exist, and open a new file there
# with the name specified, checking that one does not already exist. Then,
# transfer the data from the client to the server in chunks.
if not (os.path.exists("recv")):
    print("Note: File directory recv was not found, so will be created.")
    os.makedirs("recv")
NewFilepath = (os.path.join("recv", NewFilename)).rstrip('\0')
print("New file will be created at: " + NewFilepath)
if(os.path.exists(NewFilepath)):
    sys.exit("Critical error: An existing file with the same name was found to already exist at the location.  Now exiting.")
newfile = open(NewFilepath,"wb")
while(True):
    receivedbits = conn.recv(960)
    while (receivedbits):
        newfile.write(receivedbits)
        receivedbits = conn.recv(960)
    break
print("New file created successfully in directory recv.  Check using diff.")
newfile.close()
conn.close()
