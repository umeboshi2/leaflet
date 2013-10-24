import os
import socket

from bjsonrpc.connection import Connection as BJConnection


def make_socket(filename):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(filename)
    return sock

def make_connection(filename):
    sock = make_socket(filename)
    return BJConnection(sock)

def connection(socket=None):
    if socket is None:
        socket = '/tmp/leaflet-%s.socket' % os.getuid()
    return make_connection(socket)
    
    
if __name__ == '__main__':
    import bjsonrpc
