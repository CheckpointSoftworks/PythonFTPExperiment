#!/usr/bin/env python

import socket
import socket
import sys
import os
import os.path
import time
import struct
import select

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

# Step 2: Bind client on port 4568.  (Hard coded).

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 4568))

print("Socket bound successfully.  Now trying to send file specified...")
HOST = '127.0.0.1'
PORT = TrollPort

# Step 3: Create the data segments to send, and send. 

EpsilonPort = struct.pack("!h",EpsilonPort) # Pack the remote port to 2 bytes.
packedIP = socket.inet_aton(IpOfEpsilon) # Pack the remote IP to a 4 byte string
header = packedIP + EpsilonPort # Build up everything in the header except flag and sequence number
OriginalFilename = Filename
Filesize = struct.pack("I",os.path.getsize(Filename)) # Pack filesize to 4 bytes
Filename = struct.pack("20s",bytes(Filename,'utf-8')) # Pack the filename to 20 bytes.

counter = 0 # Used for seeing whether to send filesize, filename, or file data.
sequencenumber=0
transferfile=open(OriginalFilename, "rb") 
transferbits = transferfile.read(950)
resend = 0 # Whether to resend previous packet or move on to next (0 move on, 1 resend)
dummysegment = 0 # Used to keep track of previous packet, so can be resent when needed.

while (transferbits):
    if(resend==0): # Resend was 0, so move on to the next packet.
        if(counter==0):
            print("Sending filesize...")
            fullheader = header + b'\x00' + b'\x00'
            fullsegment = fullheader + Filesize
        elif(counter==1):
            print("Sending filename...")
            fullheader = header + b'\x01' + b'\x01'
            fullsegment = fullheader + Filename
        elif(counter>1):
            print("Sending data chunk...")
            if(sequencenumber==0):
                fullheader = header + b'\x02' + b'\x00'
            else:
                fullheader = header + b'\x02' + b'\x01'
            fullsegment = fullheader + transferbits
            transferbits = transferfile.read(950)
        dummysegment = fullsegment
        s.sendto(fullsegment, (HOST,PORT))
    else: # Resend was 1, so resend the previously attempted packet before moving on.
        s.sendto(dummysegment, (HOST,PORT))
        
    # Inspect the current state of the socket using select.select:
    read, write, err = select.select([s], [], [], .05)
    if len(read) > 0: # If socket receives ACK, then we know to move on.
        read[0].recvfrom(1)
        print ("Received ACK, moving on to next packet.") 
        resend = 0
        counter = counter+1
        if (sequencenumber==1):
            sequencenumber=0
        else:
            sequencenumber=1
    else: # If timeout, then we know resend previous packet.
        print ("Timed out, resending.")
        resend = 1 

# send done signal
fullheader = header + b'\x03' + b'\x00' 
s.sendto(fullheader, (HOST,PORT))

print("File sent successfully.")
# Finally: Close all connections used.
s.close()
