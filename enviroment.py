import socket
host = socket.gethostbyname_ex(socket.gethostname())[2][0]
port = 8081