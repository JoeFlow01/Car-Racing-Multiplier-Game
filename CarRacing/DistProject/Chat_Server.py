import socket
import threading

HOST = 'localhost'   # my ip address
PORT = 9090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

clients = []
usernames = []

# broadcast fn, send 1 message to all the connected clients
def broadcast(message):
    for client in clients:   # for every client that is connected, let him send the message
        client.send(message)

# handle fn, handle the individual connections to the client

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(f"{usernames[clients.index(client)]}")
            broadcast(message)
        except:  #if a client crashes, remove him from the clients and usernames list and break (end the thread)
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            usernames.remove(username)
            break

# receive fn, listen and accepts new connections

def receive():
    while True:  # while true we're going to accept new connections, next we use the client socket for communication and to send not the server (server.send) it's just a host that accepts new connections. we use it to request nickname and add it to the players list
        client, address = server.accept()
        print(f"connected with {str(address)}!")


       # username = client.recv(1024)
        usernames.append(client)
        clients.append(client)  # add client to the list of clients

        #print(f"username of the player is {client}")
        #client.send("Welcome to the Chat Room !\n".encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))  # we write the comma so it is treated as a tuple
        thread.start()

print("Chat server is running ...")
receive()
