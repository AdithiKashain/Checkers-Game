import pickle as pickle
from _thread import *
from socket import *
from sys import argv


def threaded_client(connection, player_id, opponent_id, lobby_id, starting): 
    global connections, lobbies

    if starting:
        connection.send(pickle.dumps(True))
    else:
        connection.send(pickle.dumps(False))

    while True:

        try:
            if lobbies[lobby_id]['client_turn'] == player_id:
                lobbies[lobby_id]['client_turn'] = None

                send_data = pickle.dumps(lobbies[lobby_id]['data'])
                connection.send(send_data)

                data = connection.recv(2048 * 4)
                lobbies[lobby_id]['data'] = pickle.loads(data)

                lobbies[lobby_id]['client_turn'] = opponent_id

        except Exception as e:
            print(e)
            break

    # player disconneted
    try:
        print(f"Connection {id} Close")
        connections -= 1
        connection.close()

    except Exception as e:
        print(e)

if __name__ == '__main__':
    if len(argv) > 1:
        hostIp = argv[1]
    else:
        hostname = gethostname()
        hostIp = gethostbyname(hostname)
    port = 8999

    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    try:
        s.bind((hostIp, port))
    except error as e:
        print(str(e))
        hostname = gethostname()
        hostIp = gethostbyname(hostname)
        s.bind((hostIp, port))
    try:
        s.listen(2)  # max 2 users in queue
    except error as e:
        print(str(e))
    print("Waiting for a connection")

    # Game global variables
    lobbies = list()
    connections = 0
    player_queue = None
    id = 0

    while True:  # continuously looking for new connection
        client, addr = s.accept()
        print(f"Connection from {addr} has been established. ID = {id}.")
        connections += 1
        id += 1  # Next client will recive incremented id value

        if player_queue is not None:
            lobbies.append({'client_turn': id, 'data': []})
            start_new_thread(threaded_client, (client, id, player_queue[1], len(lobbies)-1, True))
            start_new_thread(threaded_client, (*player_queue, id, len(lobbies)-1, False))
            player_queue = None
        else:
            player_queue = (client, id)
    