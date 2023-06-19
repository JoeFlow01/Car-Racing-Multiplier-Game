from time import sleep
import tkinter as tk
import pygame
from SurroundingsFile import Surroundings
from PlayerFile import Player
import socket
import pickle
import random
from PIL import ImageTk, Image
from Chat_Client import Client
from tkinter import Tk, font
from tkinter import ttk


class Enemy:
    def __init__(self,x,dist):
        self.x = x
        self.at_dist = dist


class CarRacing:

    def Generate_enemy_list(self):
        self.enemys = []
        for i in range(5000,self.race_distance*100+1000,1000):
            random.seed(i)
            x = random.randint(310, 450)
            self.enemys.append(Enemy(x, i))

    def __init__(self):
        self.race_distance = 500
        self.Generate_enemy_list()
        self.Chat_IP = 'localhost'
        self.Chat_PORT = 9090
        self.max_bg_speed = 20
        self.max_enemy_speed = 20
        self.Loginwindowalive = None
        self.local_player = None
        pygame.init()
        self.clock = pygame.time.Clock()
        self.gameDisplay = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 5050))
        self.players = []

    def display_players(self, players):
        for player in players:
            if player.car_x_coordinate and player.car_y_coordinate:
                local = False
                if player.username == self.local_player.username:
                    local = True
                    self.car(player.car_x_coordinate, player.car_y_coordinate, local)
                    self.displayUsername(player.username, player.car_x_coordinate, player.car_y_coordinate)
                    continue
                relative_y = int(player.dist_covered) - int(self.local_player.dist_covered)
                if (relative_y > 0) and relative_y < 600:
                    self.car(player.car_x_coordinate,self.local_player.car_y_coordinate-relative_y, local)
                    self.displayUsername(player.username, player.car_x_coordinate, self.local_player.car_y_coordinate-relative_y)
                elif relative_y > 600:
                    self.arrow_up(player.car_x_coordinate)
                    self.displayUsername(player.username,player.car_x_coordinate,5)
                elif relative_y < 0:
                    self.arrow_down(player.car_x_coordinate)
                    self.displayUsername(player.username,player.car_x_coordinate,420)
                elif relative_y == 0:
                    self.car(player.car_x_coordinate,self.local_player.car_y_coordinate, local)
                    self.displayUsername(player.username, player.car_x_coordinate, self.local_player.car_y_coordinate)


    def LoginWindow(self):
        # Create the main window

        self.LoginWindow = tk.Tk()
        self.LoginWindow.title("Race Game")
        self.LoginWindow.geometry("955x500+300+200")  # Width x Height + X position + Y position
        self.LoginWindow.configure(bg="#fff")
        self.Loginwindowalive = True
        self.LoginWindow.resizable(False,False)
        font.families()
        image = Image.open("img/loginwindow.png")
        resized_image = image.resize((900, 600), Image.ANTIALIAS)
        background_image = ImageTk.PhotoImage(resized_image)

        # Create a label to display the image
        background_label = tk.Label(self.LoginWindow, image=background_image)
        background_label.grid(row=0, column=1, rowspan=2, sticky="nsew")

        # Create a frame for the UI elements
        frame = tk.Frame(self.LoginWindow, bg='white')
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)  # Increase width of left column
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        frame.rowconfigure(3, weight=1)

        # Create welcome label
        self.welcome_label = tk.Label(frame, text="Join the Game!", font=("Courier", 18, 'bold'), border=0, bg='white')
        self.welcome_label.grid(row=0, column=0, pady=10)


        # Create entry field with a black straight line appearance
        self.entry_username = ttk.Entry(frame, style="Black.TEntry", font=('Poppins bold', 10))
        self.entry_username.insert(0, "Write Your Username")
        self.entry_username.grid(row=1, column=0, pady=10)

        # Configure ttk styles
        style = ttk.Style()
        style.configure("Black.TEntry", foreground="black", fieldbackground="white")

        # Configure style for the username label
        style.configure("Username.TLabel", foreground="black", font=("Courier", 12))

        # Create login button
        self.button_login = ttk.Button(frame, text="Join", command=self.verifyusername, style="Large.TButton")
        self.button_login.grid(row=2, column=0)

        # Create another button
        self.button_another = ttk.Button(frame, text="Rejoin", command=self.rejoin, style="Large.TButton")
        self.button_another.grid(row=4, column=0,)

        # Configure style for the button widget
        style.configure("Large.TButton",
                        foreground="black",
                        background="white",
                        width=10,
                        font=("Courier", 14),
                        padding=10)

        style.configure("Username.TLabel",
                        foreground="black",
                        background="white",
                        font=("Courier", 12))

        # Create a label for displaying the result
        self.label_result = tk.Label(frame, text="", bg='white')
        self.label_result.grid(row=3, column=0, pady=5)

        # Configure grid weights to make the columns resizable
        self.LoginWindow.grid_columnconfigure(1, weight=5)

        # Run the main window loop
        self.LoginWindow.mainloop()

    def rejoin(self):
        print("Rejoin method reached")
        username = self.entry_username.get()
        msgtobesent = "Rejoin," + username
        try:
            self.client_socket.send(msgtobesent.encode())
            return_message = self.client_socket.recv(1024).decode()
        except:
            print("Connetcion errors")
            self.label_result.config(text="Server currently down", fg="red")
            self.client_socket.close()
        if return_message == "No match found":
            self.label_result.config(text="No match found", fg="red")
        if return_message == "Rejoining":
            Client(self.Chat_IP, self.Chat_PORT, username)
            #receive the player stats
            Sterialized = self.client_socket.recv(1024)
            self.local_player = pickle.loads(Sterialized)
            print(vars(self.local_player))
            #Start game
            self.initialize()
            self.label_result.config(text="Rejoining", fg="green")
            self.LoginWindow.after(1500, self.racing_window)

    def verifyusername(self):
        print("verify method reached")
        username = self.entry_username.get()
        msgtobesent = "Verify," + username
        try:
            self.client_socket.send(msgtobesent.encode())
            return_message = self.client_socket.recv(1024).decode()
        except:
            print("Connetcion errors")
            self.label_result.config(text="Server currently down", fg="red")
            self.client_socket.close()
        if return_message == "Too large username":
            self.label_result.config(text="Max 10 digits for username", fg="red")

        if return_message == "Login Successful, Joining the game":
            Client(self.Chat_IP,self.Chat_PORT,username)
            self.local_player = Player()
            self.local_player.username = username
            self.initialize()
            self.label_result.config(text="Login Successful, Joining the game", fg="green")
            self.LoginWindow.after(1500, self.racing_window)

        if return_message == "User name already exists":
            self.label_result.config(text="User name already exists", fg="red")

        if return_message == "Enter a username":
            self.label_result.config(text="Enter a username", fg="red")

    def initialize(self):
        # suuroundings inits
        self.display_width = 800
        self.display_height = 600
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.enemy_car_height = 100
        self.enemy_car_speed = 0
        self.min_enemy_speed = 0
        self.bg_speed = 0
        self.dummy_init = False
        random.seed(self.local_player.dist_covered)

        self.enemy_car_startx = self.enemys[self.local_player.current_enemy].x
        self.enemy_car_starty = self.local_player.dist_covered-self.enemys[self.local_player.current_enemy].at_dist
        self.bg_x1 = (self.display_width / 2) - (360 / 2)
        self.bg_x2 = (self.display_width / 2) - (360 / 2)
        self.bg_y1 = 0
        self.bg_y2 = -600
        self.local_surroundings = Surroundings()
        self.local_player.crashed = False
        self.local_car_img = pygame.image.load('.\\img\\car.png')
        self.opponent_car_img = pygame.image.load('.\\img\\oponent_car.png')
        self.arrowupimg = pygame.image.load('.\\img\\arrow_up.png')
        self.arrowdownimg = pygame.image.load('.\\img\\arrow_down.png')
        self.finish_img = pygame.image.load('.\\img\\finish.png')
        self.local_player.car_x_coordinate = (self.display_width * 0.45)
        self.local_player.car_y_coordinate = (self.display_height * 0.8)
        self.car_width = 49
        # enemy_car
        self.enemy_car = pygame.image.load('.\\img\\enemy_car_1.png')
        self.enemy_car_width = 49
        self.enemy_car_height = 100

        # Background
        self.bgImg = pygame.image.load(".\\img\\back_ground.jpg")

    def receive_data(self):
        sterilized_object = self.client_socket.recv(2048)
        received_object = pickle.loads(sterilized_object)
        print("Receiving done")
        if isinstance(received_object, Surroundings):
            self.local_surroundings = received_object

        elif isinstance(received_object[0], Player):
            self.players = received_object
            for player in self.players:
                if player.username == self.local_player.username:
                    self.local_player.position = player.position
        else:
            print("Not correct data type received by the Client(surroundings,players)")

    def car(self, car_x_coordinate, car_y_coordinate, islocal):
        print("local:",islocal,"x:",car_x_coordinate,"y:",car_y_coordinate)
        if islocal:
            self.gameDisplay.blit(self.local_car_img, (car_x_coordinate, car_y_coordinate))
        else:
            self.gameDisplay.blit(self.opponent_car_img, (car_x_coordinate, car_y_coordinate))

    def arrow_up(self,x_coordinate):
            self.gameDisplay.blit(self.arrowupimg, (x_coordinate, 25))

    def arrow_down(self,x_coordinate):
            self.gameDisplay.blit(self.arrowdownimg, (x_coordinate, 560))

    def racing_window(self):
        if self.Loginwindowalive:
            self.Loginwindowalive = False
            self.LoginWindow.destroy()
        self.gameDisplay = pygame.display.set_mode(
            (self.display_width, self.display_height))
        pygame.display.set_caption('Car Racing Multiplayer Game')

        self.run_car()

    def run_car(self):

        while True:
            print("Enterd run car loop 1")
            if not self.dummy_init and self.local_surroundings.game_started:
                print("localy starting")
                self.display_message("Starting", 2)
                self.dummy_init = True

            print("Enterd run car loop 2")
            if self.local_player.crashed and self.local_surroundings.game_started:
                print("Crashed")
                self.local_player.current_enemy += 1
                self.enemy_car_starty = self.local_player.dist_covered-self.enemys[self.local_player.current_enemy].at_dist # Synchronize enemys
                self.enemy_car_startx = self.enemys[self.local_player.current_enemy].x
                self.enemy_car_speed = 3
                self.bg_speed = 3
                self.local_player.car_x_coordinate = (self.display_width * 0.45)
                self.display_message("Crashed", 2)
                self.local_player.crashed = False

            print("Enterd run car loop 3")

            if self.local_player.outofbound and self.local_surroundings.game_started:
                print("outofbounds")
                self.enemy_car_speed = 3
                self.bg_speed = 3
                self.local_player.car_x_coordinate = (self.display_width * 0.45)
                self.display_message("Out of boundaries", 2)
                self.local_player.outofbound = False
            print("Enterd run car loop 4")
            serialized_data = pickle.dumps(self.local_player)
            # Send the player object to the server
            try:
                self.client_socket.send(serialized_data)
                print("player sent")
                self.receive_data()
                print("Fisrt rec")
                self.receive_data()
                print("Sec rec")
            except OSError as e:
                print(f"Error occurred while transfering data: {e}")
                self.display_message("Server down ;( ", 7)
                print("Server down")
                pygame.QUIT
                pygame.quit()
                self.client_socket.close()
                break
            print("Enterd run car loop 5")
            if (self.local_player.dist_covered / 100) >= self.race_distance:
                self.display_message("Finished", 7)
                self.display_finish()
                self.local_player.finished = True
                serialized_data = pickle.dumps(self.local_player)
                self.client_socket.send(serialized_data)
                print("Race Finished")
                pygame.QUIT
                pygame.quit()
                self.client_socket.close()
                break
            print("Enterd run car loop 6")

            if self.local_surroundings.game_started:
                self.local_player.dist_covered += self.bg_speed * 1.2
                self.enemy_car_starty += self.enemy_car_speed
                self.bg_y1 += self.bg_speed
                self.bg_y2 += self.bg_speed
            print("Enterd run car loop 7")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.local_player.disconnected = True
                    serialized_data = pickle.dumps(self.local_player)
                    self.client_socket.send(serialized_data)
                    self.client_socket.close()
                    pygame.QUIT
                    pygame.quit()
                    print("Game closed")

                if self.local_surroundings.game_started:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            if (self.enemy_car_speed < self.max_enemy_speed) and (self.bg_speed < self.max_bg_speed):
                                self.enemy_car_speed += 1
                                self.bg_speed += 1

                        if event.key == pygame.K_DOWN:
                            if (self.enemy_car_speed > self.min_enemy_speed) and (self.bg_speed > 0):
                                self.enemy_car_speed -= 1
                                self.bg_speed -= 1

                        if event.key == pygame.K_LEFT:
                            self.local_player.car_x_coordinate -= 50

                        if event.key == pygame.K_RIGHT:
                            self.local_player.car_x_coordinate += 50
            if self.bg_y1 >= self.display_height:
                self.bg_y1 = -600

            if self.bg_y2 >= self.display_height:
                self.bg_y2 = -600

            if self.enemy_car_starty > self.display_height:
                self.local_player.current_enemy += 1
                self.enemy_car_starty = self.local_player.dist_covered-self.enemys[self.local_player.current_enemy].at_dist # synchronize enemy
                self.enemy_car_startx = self.enemys[self.local_player.current_enemy].x

            self.gameDisplay.fill(self.black)
            self.back_ground_raod()

            self.run_enemy_car(self.enemy_car_startx, self.enemy_car_starty)

            if self.local_player.car_y_coordinate < self.enemy_car_starty + self.enemy_car_height:
                if self.local_player.car_x_coordinate > self.enemy_car_startx and self.local_player.car_x_coordinate < self.enemy_car_startx + self.enemy_car_width or self.local_player.car_x_coordinate + self.car_width > self.enemy_car_startx and self.local_player.car_x_coordinate + self.car_width < self.enemy_car_startx + self.enemy_car_width:
                    self.local_player.crashed = True

            if self.local_player.car_x_coordinate < 310 or self.local_player.car_x_coordinate > 460:
                self.local_player.outofbound = True
            self.Distance_Coverd(self.local_player.dist_covered)
            self.Position(self.local_player.position)
            self.Speed(self.bg_speed)
            if self.local_player.dist_covered/100 >= self.race_distance-50:
                self.display_finish()
            self.RaceDistance()
            self.DisplayUsernames()
            self.display_players(self.players)
            if not self.local_surroundings.game_started:
                self.wait_for_others()
            pygame.display.update()
            self.clock.tick(60)

    def DisplayUsernames(self):
        font = pygame.font.SysFont("arial", 30)
        text = font.render("Rankings", True, self.white)
        self.gameDisplay.blit(text, (600, 0))
        font = pygame.font.SysFont("arial", 20)
        start = 40
        for i in range(len(self.players)):
            username = self.players[i].username
            position = self.players[i].position
            text = font.render(str(position)+"-"+str(username), True, self.white)
            self.gameDisplay.blit(text, (582, start+i*30))

    def display_message(self, msg,time):
        font = pygame.font.SysFont("comicsansms", 72, True)
        text = font.render(msg, True, (255, 255, 255))
        self.gameDisplay.blit(text, (400 - text.get_width() // 2, 240 - text.get_height() // 2))
        #self.display_credit()
        pygame.display.update()
        self.clock.tick(60)
        sleep(time)
        #pygame.QUIT
        #pygame.quit()
        #self.client_socket.close()

    def back_ground_raod(self):
        self.gameDisplay.blit(self.bgImg, (self.bg_x1, self.bg_y1))
        self.gameDisplay.blit(self.bgImg, (self.bg_x2, self.bg_y2))

    def run_enemy_car(self, thingx, thingy):
        if thingy > -100:
            self.gameDisplay.blit(self.enemy_car, (thingx, thingy))

    def Distance_Coverd(self, distance):
        distance = int(distance/100)
        if distance > 500:
            distance = 500
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Distance covered:" + str(distance), True, self.white)
        self.gameDisplay.blit(text, (0, 0))

    def RaceDistance(self):
        dist = self.race_distance
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Race distance:" + str(dist), True, self.white)
        self.gameDisplay.blit(text, (0, 25))

    def Speed(self, Speed):
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Speed:" + str(Speed), True, self.white)
        self.gameDisplay.blit(text, (0, 50))

    def Position(self,position):
        font = pygame.font.SysFont("arial", 20)
        text = font.render("Position:" + str(position), True, self.white)
        self.gameDisplay.blit(text, (0, 75))

    def wait_for_others(self):
        font = pygame.font.SysFont("arial", 30)
        text = font.render("Waiting ", True, self.white)
        self.gameDisplay.blit(text, (10, 200))
        text = font.render("for ", True, self.white)
        self.gameDisplay.blit(text, (10, 240))
        text = font.render("opponents ", True, self.white)
        self.gameDisplay.blit(text, (10, 280))

    def display_finish(self):
        relative_y = int(self.race_distance*100 - self.local_player.dist_covered)
        if (relative_y > 0) and relative_y < 600:
            print("x,y", (self.display_width / 2) - (360 / 2), self.local_player.car_y_coordinate - relative_y)
            self.gameDisplay.blit(self.finish_img, ((self.display_width / 2) - (360 / 2), self.local_player.car_y_coordinate - relative_y))

    def displayUsername(self, username, x, y):
        font = pygame.font.SysFont("arial", 20)
        text = font.render(username, True, self.red)
        self.gameDisplay.blit(text, (x, y + self.enemy_car_height))

    def display_credit(self):
        font = pygame.font.SysFont("lucidaconsole", 14)
        text = font.render("Thanks for playing!", True, self.white)
        self.gameDisplay.blit(text, (600, 520))


if __name__ == '__main__':
    car_racing = CarRacing()
    car_racing.LoginWindow()
