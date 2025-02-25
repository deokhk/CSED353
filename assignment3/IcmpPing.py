from socket import *
import os
import sys
import struct
import time
import select
import binascii  

ICMP_ECHO_REQUEST = 8

# NOTE : This code was written by Python 3.7.0
# POSTECH CSE, Kang DeokHyung

def checksum(string): 
	csum = 0
	countTo = (len(string) // 2) * 2  
	count = 0

	while count < countTo:
		thisVal = string[count+1] * 256 + string[count]
		csum = csum + thisVal 
		csum = csum & 0xffffffff  
		count = count + 2
	
	if countTo < len(string):
		csum = csum + string[len(string) - 1]
		csum = csum & 0xffffffff 
	
	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum 
	answer = answer & 0xffff 
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer 
	

def receiveOnePing(mySocket, ID, timeout, destAddr):
	timeLeft = timeout
	
	while 1: 
		startedSelect = time.time()
		whatReady = select.select([mySocket], [], [], timeLeft)
		howLongInSelect = time.time() - startedSelect

		# Return "Request timed out." if socket is timeout.
		if whatReady[0] == []:
			return "Request timed out."
		timeReceived = time.time()

		# Get packet and address
		recPacket, addr = mySocket.recvfrom(1024)
		
		# Fetch the ICMPHeader from the IP
		icmpHeader = recPacket[20: 28]

		rawTTL = struct.unpack("s", bytes([recPacket[8]]))[0]
		
		# binascii -- Convert binary and ASCII  
		TTL = int(binascii.hexlify(rawTTL), 16)
		
		icmpType, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
		
		# Return "Reply from %s: bytes=%d time=%f5ms TTL=%d" if `packetID` matches with `ID`
		if packetID == ID:
			packet_bytes = len(recPacket)
			timeSent = struct.unpack("d", recPacket[28:28 +  struct.calcsize("d")])[0]
			timeElapsed = (timeReceived - timeSent) * 1000
			return "Reply from %s: bytes=%d time=%f5ms TTL=%d" % (destAddr, packet_bytes, timeElapsed, TTL)

		timeLeft = timeLeft - howLongInSelect
		if timeLeft <= 0:
			return "Request timed out."

	
def sendOnePing(mySocket, destAddr, ID):
	# Header is type (8), code (8), checksum (16), id (16), sequence (16)
	myChecksum = 0

	# Make a dummy header with a 0 checksum
	# Use struct -- Interpret strings as packed binary data
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
	data = struct.pack("d", time.time())

	# Calculate the checksum on the data and the dummy header.
	myChecksum = checksum(header + data)
	
	# Get the right checksum, and put in the header
	if sys.platform == 'darwin':
		# Convert 16-bit integers from host to network byte order
		myChecksum = htons(myChecksum) & 0xffff
	else:
		myChecksum = htons(myChecksum)
		
	# Create header
	header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
	packet = header + data
	
	mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
	# Both LISTS and TUPLES consist of a number of objects
	# which can be referenced by their position number within the object.
	

def doOnePing(destAddr, timeout): 
	icmp = getprotobyname("icmp")

	# SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw
	mySocket = socket(AF_INET, SOCK_RAW, icmp)
	
	myID = os.getpid() & 0xFFFF  # Return the current process i
	# Measure a delay
	sendOnePing(mySocket, destAddr, myID)
	delay = receiveOnePing(mySocket, myID, timeout, destAddr)
	
	mySocket.close()
	return delay
	
def ping(host, timeout=1):
	# timeout=1 means: If one second goes by without a reply from the server,
	# the client assumes that either the client's ping or the server's pong is lost
	dest = gethostbyname(host)
	print("Pinging " + dest + " using Python:")
	print("")
	# Send ping requests to a server separated by approximately one second
	while True:  
		delay = doOnePing(dest, timeout)
		print(delay)
		time.sleep(1)# one second
	return delay
	
ping("google.com")

