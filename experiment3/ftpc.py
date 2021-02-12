#!/usr/bin/env python

# Student: Ian Weber [weber.595@osu.edu]
# Date: Oct 20, 2015
# Assignment: CSE3461 Lab 3 (client part)

import socket
import socket
import sys
import os
import os.path
import time
import struct

# Step 1 Parse inputs from terminal command
try:
    IpOfEpsilon = sys.argv[1]
except:
    sys.exit("Error: IP address of epsilon not entered on the command line.")
try:
    EpsilonPort = int(sys.argv[2])
except:
    sys.exit("Error: Remote port on epsilon not entered on the command line.")
try:
    TrollPort = int(sys.argv[3])
except:
    sys.exit("Error: Troll's port on gamma not entered on the command line.")
try:
    Filename = sys.argv[4]
except:
    sys.exit("Error: Filename to transfer not entered on the command line.")

# Step 2: Bind client on port 4567.  (Hard coded).

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 4568))

print("Socket bound successfully.  Now trying to send file specified...")
HOST = '127.0.0.1'
PORT = TrollPort

# Step 3: Create the data segments to send, and send. (Important part!)

EpsilonPort = struct.pack("!h",EpsilonPort) # Pack the remote port to 2 bytes.
packedIP = socket.inet_aton(IpOfEpsilon) # Pack the remote IP to a 4 byte string
header = packedIP + EpsilonPort # Build up everything in the header except flag
OriginalFilename = Filename
Filesize = struct.pack("I",os.path.getsize(Filename)) # Pack filesize to 4 bytes
Filename = struct.pack("20s",bytes(Filename,'utf-8')) # Pack the filename to 20 bytes.

counter = 0;
transferfile=open(OriginalFilename, "rb") 
transferbits = transferfile.read(960)
while (transferbits):
    if(counter==0):
        fullheader = header + b'\x00'
        fullsegment = fullheader + Filesize
        s.sendto(fullsegment, (HOST,PORT))
    elif(counter==1):
        fullheader = header + b'\x01'
        fullsegment = fullheader + Filename
        s.sendto(fullsegment, (HOST,PORT))
    elif(counter>1):
        print("Sending...")
        fullheader = header + b'\x02'
        fullsegment = fullheader + transferbits
        s.sendto(fullsegment, (HOST,PORT))
        time.sleep(.5)
        transferbits = transferfile.read(960)
    counter = counter+1

# send done signal
fullheader = header + b'\x03'
s.sendto(fullheader, (HOST,PORT))

print("File sent successfully.")
# Finally: Close all connections used.
s.close()
