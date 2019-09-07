#!/usr/bin/python
import sys
import socket

#-----------------------------------
def resolve_host_ip(host):
    try:
        remote_ip = socket.gethostbyname( host )
    except socket_error, msg:
        print "ERROR:resolve_host_ip():caught exception socket.error : %s" % msg
        return None
    return remote_ip

host = sys.argv[1]
#host = "169.254.165.185" #"10.0.0.6"
# TODO: look up our server
#host = resolve_host_ip('fpSean.local')
port = 9876

# get our hostname for putting in msg txt
server = socket.socket()
#mehost = socket.gethostbyname(socket.getfqdn())
#if mehost == "127.0.1.1":
#        import commands
#        mehost = commands.getoutput("hostname")

server.connect((host, port))
server.sendall("%s" % ' '.join(sys.argv[1:]))
#server.sendall("%s:%s" % (mehost,' '.join(sys.argv[1:])))
print(server.recv(1024)) #Normal server response

server.close()
