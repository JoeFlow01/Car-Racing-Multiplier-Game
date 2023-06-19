import random


class Enemy:
    def __init__(self):
        self.at_dist = None
        self.x_coordinates = None
        self.y_coordinates = None


class Surroundings:
    def __init__(self):
        self.game_started = False
        self.game_ended = False
        #self.enemys = []
        #self.generate_enemy_list()

    #def generate_enemy_list(self):
     #   for i in range(5100, 50000, 5000):
      #      enemy = Enemy()
       #     enemy.at_dist = i
        #    random.seed(i)
         #   enemy.x_coordinates = random.randint(310, 450)
          #  self.enemys.append(enemy)
