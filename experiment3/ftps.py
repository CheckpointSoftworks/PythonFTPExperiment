#!/usr/bin/env python

import socket
import socket
import sys
import os
import os.path
import struct

# Step 1: Parse inputs and do preparations
try:
    LocalPortEpsilon = int(sys.argv[1])
except:
    sys.exit("Error: Local port (to receive on) not entered on the command line.")

if not (os.path.exists("recv")):
    print("Note: File directory recv was not found, so will be created.")
    os.makedirs("recv")    

# Step 2: Bind to port specified
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', LocalPortEpsilon))

# Step 3: Receive data segments from troll (important part)

print ("Bound to port specified.  Now waiting for packets...")

# First receive metadata:
First = s.recvfrom(11)
FirstSegment=First[0]
if(FirstSegment[6:7]==b'\x00'):
    print("Filesize flag found in header of segment.  Now receiving file size:")
    Filesize = FirstSegment[7:]
    Filesize = struct.unpack("I",Filesize)
    print("Request received to transfer a file of size:",Filesize[0],"bytes")
else:
    print("Error in protocol.  Expected filesize flag first and did not receive it")

Second = s.recvfrom(27)
SecondSegment=Second[0]
if(SecondSegment[6:7]==b'\x01'):
    print("Filename flag found in header of segment.  Now receiving file name:")
    Filename = SecondSegment[7:]
    Filename = struct.unpack("20s",Filename)
    NewFilename = Filename[0].decode('utf-8')
    print("With a name of: " + NewFilename)
else:
    print("Error in protocol.  Expected filename flag and did not receive it")

# Now transfer file
NewFilepath = (os.path.join("recv", NewFilename)).rstrip('\0')
print("Now beginning file transer...")
if(os.path.exists(NewFilepath)):
    sys.exit("Critical error: An existing file with the same name was found to already exist at the location.  Now exiting.")
newfile = open(NewFilepath,"wb")
while(True):
    receivedbits,addr = s.recvfrom(967)
    while (receivedbits[6:7]==b'\x02'):
        print("receiving")
        newfile.write(receivedbits[7:])
        receivedbits,addr = s.recvfrom(967)
    break
print("New file created successfully in directory recv.  Check using diff.")
newfile.close()

# Close all sockets used
s.close()
