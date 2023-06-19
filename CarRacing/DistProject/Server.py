import socket
import threading
from SurroundingsFile import Surroundings
import pickle
from PlayerFile import Player
import subprocess
import time

class CarRacingServer:

    def run_file(self):
        subprocess.call(['python', 'Chat_Server.py'])

    def __init__(self):
        #file_thread = threading.Thread(target=self.run_file)
        #file_thread.start()
        self.global_surroundings = Surroundings()
        self.host = "localhost"  # Server IP address
        self.port = 5050  # Server port
        self.server_socket = None
        self.players = []
        self.lock = threading.Lock()

    def sort_players_by_distance(self):
        self.players = sorted(self.players, key=lambda player: player.dist_covered, reverse=True)
        for i in range (0, len(self.players)):
            self.players[i].position = i+1


    def update_player(self, player):
        for i in range(len(self.players)):
            if self.players[i].username == player.username:
                self.players[i] = player
                return

    def CheckFinish(self):
        if len(self.players ) > 1:
            for player in self.players:
                if not player.finished:
                    return False
            return True
        else:
            return False

    def register_player(self, player):
        if len(player.username) > 10:
            return "Too large username"
        if player.username.strip() == "":
            return "Enter a username"

        for i in self.players:
            if i.username == player.username:
                return "User name already exists"
        self.lock.acquire()
        self.players.append(player)
        self.lock.release()
        return "Login Successful, Joining the game"

    def update_map(self):
        while True:
            if self.global_surroundings.game_ended:
                self.global_surroundings = Surroundings()
                print("Game 5les ya ged3aan")
                print(vars(self.global_surroundings))
                self.players = []
            if len(self.players) > 1:
                self.global_surroundings.game_started = True

            self.lock.acquire()
            self.sort_players_by_distance()
            self.lock.release()
            self.global_surroundings.game_ended = self.CheckFinish()
            #time.sleep(0.01)

    def receive_data(self, client_socket):
        while True:
            try:
                sterilized_object = client_socket.recv(2048)
                received_object = pickle.loads(sterilized_object)
                if isinstance(received_object, Player):
                    self.lock.acquire()
                    self.update_player(received_object)
                    self.lock.release()
                    break
            except Exception:
                client_socket.close()
                break
                print("fashel begad")

    def start(self):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print('Server started on {}:{}'.format(self.host, self.port))
        updating_thread = threading.Thread(target=self.update_map)
        updating_thread.start()
        while True:
            client_socket, client_address = self.server_socket.accept()
            print('New connection from {}:{}'.format(client_address[0], client_address[1]))
            connection_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            connection_thread.start()

    def handle_client(self, client_socket):
        running = True
        while running:
            try:
                message = client_socket.recv(1024).decode()
                request = message.split(",")[0]
                print(message,request)
                if request == "Verify":
                    username = message.split(",")[1]
                    player = Player()
                    player.username = username
                    msg = self.register_player(player)
                    client_socket.send(msg.encode())
                    if msg == "Login Successful, Joining the game":
                        running = False
                elif request == "Rejoin":
                    print("Rejoin else reached")
                    username = message.split(",")[1]
                    for player in self.players:
                        if player.username == username and player.disconnected:
                            print("Our player",player.username)
                            player.disconnected = False
                            client_socket.send("Rejoining".encode())
                            print("Sent label")
                            Sterialized = pickle.dumps(player)
                            client_socket.send(Sterialized)
                            print("sent player")
                            running = False
                            break
                    client_socket.send("No match found".encode())
            except socket.error:
                print("Socket is closed")
                try:
                    client_socket.close()
                except:
                    print("yady elnila")
                break

        while True:
            #print("Now handling")
            try:
                if not self.global_surroundings.game_ended:
                    # receive player
                    self.receive_data(client_socket)
                    #print("Player received")

                    # send surroundings
                    serialized_data = pickle.dumps(self.global_surroundings)
                    try:
                        client_socket.send(serialized_data)
                        #print("Surroundings sent")
                    except OSError as e:
                        print(f"Error occurred while sending data: {e}")
                        break

                    # send players
                    self.lock.acquire()
                    serialized_data = pickle.dumps(self.players)
                    self.lock.release()
                    try:
                        client_socket.send(serialized_data)
                        #print("players sent")
                    except OSError as e:
                        print(f"Error occurred while sending data: {e}")
                        break
            except socket.error:
                print("removing client due to errors in sending and receiving data")
                client_socket.close()
                break


if __name__ == '__main__':
    server = CarRacingServer()
    server.start()
