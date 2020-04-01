# Import socket module
from socket import * 
import sys # In order to terminate the program

# Create a TCP server socket
#(AF_INET is used for IPv4 protocols)
#(SOCK_STREAM is used for TCP)

serverSocket = ### Write your code

# Assign a port number
serverPort = 6789

# Bind the socket to server address and server port
### Write your code

# Listen to at most 1 connection at a time
### Write your code

# Server should be up and running and listening to the incoming connections

while True:
	print('The server is ready to receive')

	# Set up a new connection from the client
	connectionSocket, addr = ### Write your code

	# If an exception occurs during the execution of try clause
	# the rest of the clause is skipped
	# If the exception type matches the word after except
	# the except clause is executed
	try:
		# Receives the request message from the client
		message = ### Write your code
		# Extract the path of the requested object from the message
		# The path is the second part of HTTP header, identified by [1]
		filename = ### Write your code
		# Because the extracted path of the HTTP request includes 
		# a character '\', we read the path from the second character 
		f = open(filename[1:])
		# Store the entire content of the requested file in a temporary buffer
		outputdata = f.read()
		# Send the HTTP response header line to the connection socket
		### Write your code
 
		# Send the content of the requested file to the connection socket
		for i in range(0, len(outputdata)):  
			### Write your code
		# Send “\r\n” to the connection socket.
		### Write your code
		
		# Close the client connection socket
		### Write your code

	except IOError:
			# Send HTTP response message for file not found
			### Write your code
			### Write your code
			# Close the client connection socket
			### Write your code

# Close the server socket
### Write your code  
sys.exit() #Terminate the program after sending the corresponding data
