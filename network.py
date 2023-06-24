import pickle as pickle  # for faster serialization
import socket


class Network:
    def __init__(self, argv):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       
        if len(argv) > 1:
            self.host = argv[1]
        else:
            hostname = socket.gethostname()
            self.host = socket.gethostbyname(hostname)
        
        self.port = 8999

    def connect(self):
        self.client.settimeout(10)
        try:
            self.client.connect((self.host, self.port))
        except socket.timeout:
            print('Time exceeded')
            quit()
        data = self.client.recv(2048 * 4)
        return pickle.loads(data)

    def disconnect(self):
        self.client.close()

    def send(self, data):

        try:
            self.client.send(pickle.dumps(data))
            return True
        
        except socket.error as e:
            print(e)
            return False

    def recive(self):
        self.client.settimeout(.1)

        try:
            reply = self.client.recv(2048 * 4)
        except socket.timeout:
            return None

        try:
            reply = pickle.loads(reply)
        except Exception as e:
            print(e)

        return reply
