class SocketWrapper(object):
    """套接字包装类"""

    def __init__(self, sock):
        self.sock = sock

    def recv_data(self):
        try:
            return self.sock.recv(512).decode('utf-8')
        except:
            return ""

    def send_data(self, messages):
        return self.sock.send(messages.encode('utf-8'))

    def close(self):
        self.sock.close()
