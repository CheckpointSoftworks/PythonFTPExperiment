#!/usr/bin/env python

import socket
import socket
import sys
import os
import os.path
import struct
import select
import time

# Step 1: Parse inputs and do preparations
try:
    LocalPortEpsilon = int(sys.argv[1])
except:
    sys.exit("Error: Local port (to receive on) not entered on the command line.")
try:
    TrollPortEpsilon = int(sys.argv[2])
except:
    sys.exit("Error: Troll port not entered on the command line.")

if not (os.path.exists("recv")):
    print("Note: File directory recv was not found, so will be created.")
    os.makedirs("recv")    

# Step 2: Bind to port specified
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', LocalPortEpsilon))

HOST = '127.0.0.1'
PORT = TrollPortEpsilon

# Step 3: Receive data segments from troll (important part)

print ("Bound to port specified.  Now waiting for packets...")
ExpectedSequenceNumber = 0
dummysegment = 0 # Used to keep a copy of the previously received packet
counter = 0 # Used to keep track of what step we are at in the protocol
ACK = b'\x01' # An arbitrary byte used for sending back to the client to ACK.

# First receive metadata: Filesize then filename.
while(True):
    if(counter==0):
        First = s.recvfrom(12)
        FirstSegment=First[0]
        if(FirstSegment[6:7]==b'\x00' and FirstSegment[7:8]==b'\x00'):
            print("Filesize flag found in header of segment.  Now receiving file size:")
            Filesize = FirstSegment[8:]
            Filesize = struct.unpack("I",Filesize)
            print("Request received to transfer a file of size:",Filesize[0],"bytes")
            #time.sleep(.25)
            s.sendto(ACK, (HOST,PORT))
            break
        else:
            print("Error in communication: Received a repeat packet. Sending ACK of repeat. [1].")
            #time.sleep(.25)
            s.sendto(ACK, (HOST,PORT))
counter=counter+1            
while(True):
    if(counter==1):
        Second = s.recvfrom(28)
        SecondSegment=Second[0]
        if(SecondSegment[6:7]==b'\x01' and SecondSegment[7:8]==b'\x01'):
            print("Filename flag found in header of segment.  Now receiving file name:")
            Filename = SecondSegment[8:]
            Filename = struct.unpack("20s",Filename)
            NewFilename = Filename[0].decode('utf-8')
            print("With a name of: " + NewFilename)
            #time.sleep(.25)
            s.sendto(ACK, (HOST,PORT))
            break
        else:
            print("Error in communication.  Received a repeat packet. Sending ACK of repeat. [2].")
            #time.sleep(.25)
            s.sendto(ACK, (HOST,PORT))
counter=counter+1    

# Now transfer file
NewFilepath = (os.path.join("recv", NewFilename)).rstrip('\0')
print("Now beginning file transfer...")
if(os.path.exists(NewFilepath)):
    sys.exit("Critical error: An existing file with the same name was found to already exist at the location.  Now exiting.")
newfile = open(NewFilepath,"wb")

dummysegment = 0
while(True):
    receivedbits,addr = s.recvfrom(958)
    while (receivedbits[6:7]==b'\x02'):
        print("receiving chunk of file data...")
        if(((receivedbits[7:8]==b'\x00' and ExpectedSequenceNumber==0) or (receivedbits[7:8]==b'\x01' and ExpectedSequenceNumber==1))and receivedbits!=dummysegment):
            newfile.write(receivedbits[8:])
            dummysegment = receivedbits
            #time.sleep(.25)
            s.sendto(ACK, (HOST,PORT))
            receivedbits,addr = s.recvfrom(958)
            if(ExpectedSequenceNumber==1):
                ExpectedSequenceNumber=0
            else:
                ExpectedSequenceNumber=1
        else:
            print("Error in communication.  Received a repeat packet. Sending ACK of repeat. [3].")
            #time.sleep(.25)
            s.sendto(ACK, (HOST,PORT))
            receivedbits,addr = s.recvfrom(958)
    break

print("New file created successfully in directory recv.  Check using diff.")
newfile.close()
# Close all sockets used
s.close()
