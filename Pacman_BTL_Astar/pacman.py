'''
=================================================
|        MSV:        B21DCCN461                 |
|       Họ tên:     Hoàng Minh Khương           |
|                   PTIT                        |
=================================================
'''

from algorithms.a_star_in_grid import *

import pygame
import copy

import math
from board import boards

pygame.init()

WIDTH = 600
HEIGHT = 710
i_pos_player = 24
j_pos_player = 15
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BTL Nhóm 5 - A*")
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level = boards[0]                                   # mặc định để map 1
level_init = copy.deepcopy(boards[0])           
color_wall = 'aqua'
color_food = 'white'
cell_board = WIDTH // 30     # kích thước 1 cell trong board
player_images = []
direction = 0               # 0 - right, 1 - left, 2 - up, 3 - down 
direction_command = 0
counter = 0
flicker = False    # chỉnh hiệu ứng nhấp nháy của thức ăn
player_speed = 2
score = 0
powerup = False             # mode đặc biệt của pacman có thể ăn ghost
power_counter = 0           # đếm thời gian hết chế độ mode của pacman
eaten_ghost = [False, False, False, False]
moving = False
startup_counter = 0
lives = 3                   # số mạng của người chơi

player_x = j_pos_player * cell_board            # vị trí x của pacman 
player_y = i_pos_player * cell_board            # vị trí y của pacman 

targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
blinky_dead = False
inky_dead = False
clyde_dead = False
pinky_dead = False
blinky_box = False
inky_box = False
clyde_box = False
pinky_box = False
ghost_speeds = [2, 2, 2, 2]
power_food = 0                      # ăn đủ 4 chấm thì win game, tăng ở hàm check_collisions(), kiểm tra điều kiện win trong while

turns_allowed = [False, False, False, False]

PI = math.pi

game_over = False
game_won = False

min_distance = 0

win_img = pygame.transform.scale(pygame.image.load('assets/background/background.jpg'), (WIDTH, HEIGHT))
gameover_img = pygame.transform.scale(pygame.image.load('assets/background/game_over.png'), (WIDTH, HEIGHT))
start_game_img = pygame.transform.scale(pygame.image.load('assets/background/start_game.jpg'), (WIDTH, HEIGHT))
menu_map_img = pygame.transform.scale(pygame.image.load('assets/background/menu_map.jpg'), (WIDTH, HEIGHT))
start_btn_img = pygame.image.load('assets/button/start_btn.png').convert_alpha()
map1_btn_img = pygame.image.load('assets/button/map1.png').convert_alpha()
map2_btn_img = pygame.image.load('assets/button/map2.png').convert_alpha()
map3_btn_img = pygame.image.load('assets/button/map3.png').convert_alpha()

for i in range(1, 5):
        player_images += [pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (25, 25))]

blinky_img = pygame.transform.scale(pygame.image.load('assets/ghost_images/red.png'), (25, 25))
pinky_img = pygame.transform.scale(pygame.image.load('assets/ghost_images/pink.png'), (25, 25))
inky_img = pygame.transform.scale(pygame.image.load('assets/ghost_images/blue.png'), (25, 25))
clyde_img = pygame.transform.scale(pygame.image.load('assets/ghost_images/orange.png'), (25, 25))
spooked_img = pygame.transform.scale(pygame.image.load('assets/ghost_images/powerup.png'), (25, 25))
dead_img = pygame.transform.scale(pygame.image.load('assets/ghost_images/dead.png'), (25, 25))



blinky_x = 7 * 20
blinky_y = 6 * 20
blinky_direction = 0

pinky_x = 2 * 20
pinky_y = 27 * 20
pinky_direction = 0

inky_x = 13 * 20
inky_y = 15 * 20
inky_direction = 0

clyde_x = 16 * 20
clyde_y = 15 * 20
clyde_direction = 0

#####################
# vẽ đường đi tới foods (các chấm màu xanh)
def draw_direction_food(draw_food: bool, node_des: Node):
    global index
    index = 0
    lst = []
    if not draw_food:
        draw_food = True
        i = node_des.i            # lưu lại tọa đồ điểm đích
        j = node_des.j
        while str(node_des) != 'None':
            if node_des.i != i or node_des.j != j:
                level[node_des.i][node_des.j] = -1
            lst.append((node_des.i, node_des.j))
            node_des = node_des.parent
    return draw_food, lst[::-1]        

# điều khiển pacman theo đường đi của thuật toán 
def control_pacman(src: Node, des: Node):
    # RIGHT
    global direction
    if src.i == des.i and src.j < des.j:
        return 0
    # LEFT
    if src.i == des.i and src.j > des.j:
        return 1
    # UP
    if src.i > des.i and src.j == des.j:
        return 2
    # DOWN
    if src.i < des.i and src.j == des.j:
        return 3
    return direction


######################

class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id) :
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + cell_board//2
        self.center_y = self.y_pos + cell_board//2
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()

    def draw(self) -> pygame.rect.Rect:
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - cell_board // 2, self.center_y - cell_board // 2), (20, 20))
        return ghost_rect
        
    
    def check_collisions(self):
        # R, L, U, D
        self.turns = [False, False, False, False]
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - cell_board//2) // cell_board][self.center_x // cell_board] == 9:
                self.turns[2] = True
            if level[self.center_y // cell_board][(self.center_x - cell_board//2) // cell_board] < 3 \
                    or (level[self.center_y // cell_board][(self.center_x - cell_board//2) // cell_board] == 9 and (
                    self.in_box or self.dead)):
                self.turns[1] = True
            if level[self.center_y // cell_board][(self.center_x + cell_board//2) // cell_board] < 3 \
                    or (level[self.center_y // cell_board][(self.center_x + cell_board//2) // cell_board] == 9 and (
                    self.in_box or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + cell_board//2) // cell_board][self.center_x // cell_board] < 3 \
                    or (level[(self.center_y + cell_board//2) // cell_board][self.center_x // cell_board] == 9 and (
                    self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - cell_board//2) // cell_board][self.center_x // cell_board] < 3 \
                    or (level[(self.center_y - cell_board//2) // cell_board][self.center_x // cell_board] == 9 and (
                    self.in_box or self.dead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 8 <= self.center_x % cell_board <= 12:
                    if level[(self.center_y + cell_board//2) // cell_board][self.center_x // cell_board] < 3 or (level[(self.center_y + cell_board//2) // cell_board][self.center_x // cell_board] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - cell_board//2) // cell_board][self.center_x // cell_board] < 3 \
                            or (level[(self.center_y - cell_board//2) // cell_board][self.center_x // cell_board] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 8 <= self.center_y % cell_board <= 12:
                    if level[self.center_y // cell_board][(self.center_x - cell_board) // cell_board] < 3 \
                            or (level[self.center_y // cell_board][(self.center_x - cell_board) // cell_board] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // cell_board][(self.center_x + cell_board) // cell_board] < 3 \
                            or (level[self.center_y // cell_board][(self.center_x + cell_board) // cell_board] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 8 <= self.center_x % cell_board <= 12:
                    if level[(self.center_y + cell_board//2) // cell_board][self.center_x // cell_board] < 3 or (level[(self.center_y + cell_board//2) // cell_board][self.center_x // cell_board] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - cell_board//2) // cell_board][self.center_x // cell_board] < 3 \
                            or (level[(self.center_y - cell_board//2) // cell_board][self.center_x // cell_board] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 8 <= self.center_y % cell_board <= 12:
                    if level[self.center_y // cell_board][(self.center_x - cell_board//2) // cell_board] < 3 \
                            or (level[self.center_y // cell_board][(self.center_x - cell_board//2) // cell_board] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // cell_board][(self.center_x + cell_board//2) // cell_board] < 3 \
                            or (level[self.center_y // cell_board][(self.center_x + cell_board//2) // cell_board] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 12 * 20 <= self.x_pos <= 18 * 20 and 14 * 20 <= self.y_pos <= 17 * 20:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def move_clyde(self):
        # r, l, u, d
        # clyde is going to turn whenever advantageous for pursuit
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 600
        elif self.x_pos > 600:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self):
        # r, l, u, d
        # blinky is going to turn whenever colliding with walls, otherwise continue straight
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 600
        elif self.x_pos > 600:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_inky(self):
        # r, l, u, d
        # inky turns up or down at any point to pursue, but left and right only on collision
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 600
        elif self.x_pos > 600:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self):
        # r, l, u, d
        # inky is going to turn left or right whenever advantageous, but only up or down on collision
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 600
        elif self.x_pos > 600:
            self.x_pos = -30
        return self.x_pos, self.y_pos, self.direction

class Button:
    def __init__(self, x, y, image, scale) -> None:
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    
    def draw(self, surface):
        action = False
        # lấy vị trí của con trỏ trên màn hình
        pos = pygame.mouse.get_pos()
        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
                # print('click')
            
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))
    
        return action

# vẽ giao diện start game
def draw_start_display() -> bool:
    start_btn = Button(200, 550, start_btn_img, 0.7)
    screen.blit(start_game_img, (0, 0))
    return start_btn.draw(start_game_img)
    
# vẽ giao diện menu map
def draw_menu_map():
    map1_btn = Button(75, 500, map1_btn_img, 0.3)
    map2_btn = Button(225, 500, map2_btn_img, 0.3)
    map3_btn = Button(375, 500, map3_btn_img, 0.3)
    ans = [map1_btn.draw(menu_map_img), map2_btn.draw(menu_map_img), map3_btn.draw(menu_map_img)]
    screen.blit(menu_map_img, (0, 0))
    return ans

# vẽ map
def draw_board():
    global player_x, player_y
    for i in range(len(level)):
        for j in range(len(level[i])):

            if level[i][j] == -1:
                pygame.draw.circle(screen, 'green', (j * cell_board + 0.5 * cell_board, i * cell_board + 0.5 * cell_board), 1)

            # if level[i][j] == 1:
            #     pygame.draw.circle(screen, color_food, (j * cell_board + 0.5 * cell_board, i * cell_board + 0.5 * cell_board), 2)

            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, color_food, (j * cell_board + 0.5 * cell_board, i * cell_board + 0.5 * cell_board), 5)

            if level[i][j] == 3:
                pygame.draw.line(screen, color_wall, (j * cell_board + 0.5 * cell_board, i * cell_board), (j * cell_board + 0.5 * cell_board, i * cell_board + cell_board), 2)

            if level[i][j] == 4:
                pygame.draw.line(screen, color_wall, (j * cell_board, i * cell_board + 0.5 * cell_board), (j * cell_board + cell_board, i * cell_board + 0.5 * cell_board), 2)

            if level[i][j] == 5:
                pygame.draw.arc(screen, color_wall, [(j * cell_board - 0.4 * cell_board), (i * cell_board + 0.5 * cell_board), cell_board, cell_board], 0, PI/2, 2)

            if level[i][j] == 6:
                pygame.draw.arc(screen, color_wall, [(j * cell_board + 0.5 * cell_board), (i * cell_board + 0.5 * cell_board), cell_board, cell_board], PI/2 , PI, 2)

            if level[i][j] == 7:
                pygame.draw.arc(screen, color_wall, [(j * cell_board + 0.5 * cell_board), (i * cell_board - 0.4 * cell_board), cell_board, cell_board], PI, 3 * PI/2, 2)

            if level[i][j] == 8:
                pygame.draw.arc(screen, color_wall, [(j * cell_board - 0.4 * cell_board), (i * cell_board - 0.4 * cell_board), cell_board, cell_board], 3* PI/2, 0, 2)

            if level[i][j] == 9:
                pygame.draw.line(screen, color_food, (j * cell_board, i * cell_board + 0.5 * cell_board), (j * cell_board + cell_board, i * cell_board + 0.5 * cell_board), 2)

def draw_player():
    if direction == 0:       # RIGHT
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:     # LEFT
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 180), (player_x, player_y))
    elif direction == 2:     # UP
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:    # DOWN
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))

def check_position(centerx, centery):
    turns = [False, False, False, False]
    #          R      L      U      D
    fudge_number = cell_board //2
    if centerx // cell_board < 29:
        if direction == 0:
            if level[centerx // cell_board][(centerx - fudge_number)//cell_board] < 3:
                turns[1] = True
        
        if direction == 1:
            if level[centerx // cell_board][(centerx + fudge_number)//cell_board] < 3:
                turns[0] = True
        
        if direction == 2:
            if level[(centerx + fudge_number) // cell_board][centerx//cell_board] < 3:
                turns[3] = True

        if direction == 3:
            if level[(centerx - fudge_number) // cell_board][centerx//cell_board] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 8 <= centerx % cell_board <= 12:
                # print('center x = ',center_x)
                if level[(centery + fudge_number) // cell_board][centerx // cell_board] < 3:
                    turns[3] = True
                if level[(centery - fudge_number) // cell_board][centerx // cell_board] < 3:
                    turns[2] = True
            if 8 <= centery % cell_board <= 12:
                # print('center y = ',center_y)
                if level[centery // cell_board][(centerx - fudge_number) // cell_board] < 3:
                    turns[1] = True
                if level[centery // cell_board][(centerx + fudge_number) // cell_board] < 3:
                    turns[0] = True

        if direction == 0 or direction == 1:
            if 8 <= centerx % cell_board <= 12:
                # print('center x = ',center_x)
                if level[(centery + cell_board) // cell_board][centerx // cell_board] < 3:
                    turns[3] = True
                if level[(centery - cell_board) // cell_board][centerx // cell_board] < 3:
                    turns[2] = True
            if 8 <= centery % cell_board <= 12:
                # print('center y = ',center_y)
                if level[centery // cell_board][(centerx - fudge_number) // cell_board] < 3:
                    turns[1] = True
                if level[centery // cell_board][(centerx + fudge_number) // cell_board] < 3:
                    turns[0] = True


    else:
        turns[0] = True
        turns[1] = True

    return turns

def move_player(play_x, play_y):
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y

# Kiểm tra va chạm với food
def check_collisons(scor, power, power_count, eaten_ghosts):
    global power_food, min_distance
    if level[center_y // cell_board][center_x // cell_board] == 1 or level[center_y // cell_board][center_x // cell_board] == -1:
        level[center_y // cell_board][center_x // cell_board] = 0
        scor += 10
        min_distance += 1
    elif level[center_y // cell_board][center_x // cell_board] == 2:
        level[center_y // cell_board][center_x // cell_board] = 0
        scor += 50
        power = True
        power_count = 0
        eaten_ghosts = [False, False, False, False]
        power_food += 1
        min_distance += 1

    return scor, power, power_count, eaten_ghosts

# Hàm vẽ điểm ra màn hình
def draw_misc():
    text_score = font.render(f'Score: {score}', True, color_food)
    screen.blit(text_score, (10, 670))

    text_A_Star = font.render(f'A* = {min_distance}', True, color_food)
    screen.blit(text_A_Star, (280, 670))
    # nếu chế độ mode thì hiển thị lên màn hình chấm xanh dương sau 10s sẽ biến mất
    if powerup:
        pygame.draw.circle(screen, color_wall, (140, 680), 7)

    # vẽ số mạng của người chơi
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[1], (cell_board, cell_board)), (450 + i * 30, 670))
    
    # GAME OVER
    if game_over:
        _font_script = pygame.font.Font('font/PixelifySans-VariableFont_wght.ttf', 16)
        script_text = _font_script.render('Space bar to restart!', True, 'white')
        screen.blit(gameover_img, (0, 0))
        screen.blit(script_text, (200, 600))
    # WIN
    if game_won:
        _font_header = pygame.font.Font('font/PixelifySans-VariableFont_wght.ttf', 100)
        vic_text = _font_header.render('Victory', True, 'aqua')

        _font_script = pygame.font.Font('font/PixelifySans-VariableFont_wght.ttf', 16)
        script_text = _font_script.render('Space bar to restart!', True, 'white')

        screen.blit(win_img, (0, 0))
        screen.blit(vic_text, (100, 200))
        screen.blit(script_text, (200, 400))


def get_targets(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    if player_x < 300:
        runaway_x = 600
    else:
        runaway_x = 0

    if player_y < 300:
        runaway_y = 600
    else:
        runaway_y = 0
    
    return_target = (15 * 20, 14 * 20)
    
    if powerup:
        if not blinky.dead and not eaten_ghost[0]:
            blink_target = (runaway_x, runaway_y)
        elif not blinky.dead and eaten_ghost[0]:
            if 11 * 20 < blink_x < 18 * 20 and 13 * 20 < blink_y < 17 * 20:
                blink_target = (15*20, 12*20)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target
        
        if not inky.dead and not eaten_ghost[1]:
            ink_target = (runaway_x, runaway_y)
        elif not inky.dead and eaten_ghost[1]:
            if 11 * 20 < ink_x < 18 * 20 and 13 * 20 < ink_y < 17 * 20:
                ink_target = (15*20, 12*20)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target

        if not pinky.dead and not eaten_ghost[2]:
            pink_target = (runaway_x, runaway_y)
        elif not pinky.dead and eaten_ghost[2]:
            if 11 * 20 < pink_x < 18 * 20 and 13 * 20 < pink_y < 17 * 20:
                pink_target = (15*20, 12*20)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target

        if not clyde.dead and not eaten_ghost[3]:
            clyd_target = (runaway_x, runaway_y)
        elif not clyde.dead and eaten_ghost[3]:
            if 11 * 20 < clyd_x < 18 * 20 and 13 * 20 < clyd_y < 17 * 20:
                clyd_target = (15*20, 12*20)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    else:
        '''
            kiểm tra nếu vị trí của ma nằm trong ghost box ...
        '''
        if not blinky.dead:
            if 11 * 20 < blink_x < 18 * 20 and 13 * 20 < blink_y < 17 * 20:
                blink_target = (15*20, 12*20)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target

        if not inky.dead:
            if 11 * 20 < ink_x < 18 * 20 and 13 * 20 < ink_y < 17 * 20:
                ink_target = (15*20, 12*20)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target

        if not pinky.dead:
            if 11 * 20 < pink_x < 18 * 20 and 13 * 20 < pink_y < 17 * 20:
                pink_target = (15*20, 12*20)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target

        if not clyde.dead:
            if 11 * 20 < clyd_x < 18 * 20 and 13 * 20 < clyd_y < 17 * 20:
                clyd_target = (15*20, 12*20)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    return [blink_target, ink_target, pink_target, clyd_target]

# xét vị trí pacman đến các food còn lại, trả về mảng các food cần ăn tối ưu nhất
def sort_food(foods, i_pos, j_pos, ans: list):
    if len(foods) <= 0: 
        return 
    foods.sort(key=lambda x : (x[0] - i_pos) ** 2 + (x[1] - j_pos) ** 2)
    ans.append(foods[0])
    sort_food(foods[1:], foods[0][0], foods[0][1], ans)

# định hướng chiều đi chuyển của pacman
def pacman_router(lst_trace):
    global direction
    global index
    if index < len(lst_trace):
        if player_x % 20 == 0 and player_y % 20 == 0:
            src = Node(player_y // 20, player_x // 20)
            des = Node(lst_trace[index][0], lst_trace[index][1])
            if src.i == des.i and src.j == des.j:
                index += 1
                if index < len(lst_trace):
                    des = Node(lst_trace[index][0], lst_trace[index][1])
                direction = control_pacman(src, des)

def get_foods(level):
    res = []
    for i in range(len(level)):
        for j in range(len(level[0])):
            if level[i][j] == 2:
                res.append((i, j))
    return res

#############################
start_state_btn = False    # biến check trạng thái click của button start
map_1_state_btn = False     # biến check trạng thái click button map1
map_2_state_btn = False     # biến check trạng thái click button map2
map_3_state_btn = False     # biến check trạng thái click button map3
#############################

run = True

while run:
    if not start_state_btn:
        start_state_btn = draw_start_display()
    elif not map_1_state_btn and not map_2_state_btn and not map_3_state_btn:
        map_1_state_btn, map_2_state_btn, map_3_state_btn = draw_menu_map()
        if map_1_state_btn: 
            level = boards[0]
            level_init = copy.deepcopy(boards[0])
            foods = get_foods(level)
            ans = []                                            # lưu mảng thứ tự các food cần ăn tối ưu (mảng các tuple lưu vị trí i, j của food)
            sort_food(foods, i_pos_player, j_pos_player, ans)
            index = 0
            idx = 0
            color_wall = 'aqua'
            draw_foods = [False] * len(ans)
            eaten_foods = [False] * len(ans)
        elif map_2_state_btn: 
            level = boards[1]
            level_init = copy.deepcopy(boards[1])
            foods = get_foods(level)
            ans = []                                            # lưu mảng thứ tự các food cần ăn tối ưu (mảng các tuple lưu vị trí i, j của food)
            sort_food(foods, i_pos_player, j_pos_player, ans)
            index = 0
            idx = 0
            color_wall = 'red'
            draw_foods = [False] * len(ans)
            eaten_foods = [False] * len(ans)
        elif map_3_state_btn: 
            level = boards[2]
            level_init = copy.deepcopy(boards[2])
            foods = get_foods(level)
            ans = []                                            # lưu mảng thứ tự các food cần ăn tối ưu (mảng các tuple lưu vị trí i, j của food)
            sort_food(foods, i_pos_player, j_pos_player, ans)
            index = 0
            idx = 0
            color_wall = 'blue'
            draw_foods = [False] * len(ans)
            eaten_foods = [False] * len(ans)

    else:

        timer.tick(fps)
        if counter < 19:
            counter += 1
            flicker = True if counter <= 3 else False
        else:
            counter = 0
            flicker = True

        if powerup and power_counter < 300:      # check lúc ăn được viên food to thì pacman ăn được ma trong tgian 5s
            power_counter +=1
        elif powerup and power_counter >= 300:
            power_counter = 0
            powerup = False
            eaten_ghost = [False, False, False, False]

        # đếm số chấm to ăn được để quyết định win game
        if power_food == len(ans):
            game_won = True


        if startup_counter < 180 and not game_over and not game_won:      # 3s đầu chưa chạy pacman khi load game
            moving = False
            startup_counter += 1
        else:
            moving = True
        
        screen.fill('black')

        center_x = player_x + cell_board//2
        center_y = player_y + cell_board//2

        if powerup:
            ghost_speeds = [1, 1, 1, 1]
        else:
            ghost_speeds = [2, 2, 2, 2]
        
        if eaten_ghost[0]:
            ghost_speeds[0] = 2
        if eaten_ghost[1]:
            ghost_speeds[1] = 2
        if eaten_ghost[2]:
            ghost_speeds[2] = 2
        if eaten_ghost[3]:
            ghost_speeds[3] = 2
        

        if blinky_dead:
            ghost_speeds[0] = 3
        if inky_dead:
            ghost_speeds[1] = 3
        if pinky_dead:
            ghost_speeds[2] = 3
        if clyde_dead:
            ghost_speeds[3] = 3

            

        # vẽ giao diện trò chơi
        draw_board()
        # duyệt qua các node của đường đi A* và di chuyển pacman
        for i in range(len(ans)):
            if player_x == ans[i][1] * 20 and player_y == ans[i][0] * 20:
                eaten_foods[i] = True
                idx += 1

        if idx < len(ans) and not eaten_foods[idx] and not draw_foods[idx] :
            draw_foods[idx], lst_trace = draw_direction_food(draw_foods[idx], aStar(Node(player_y // 20, player_x // 20), Node(ans[idx][0],ans[idx][1]), level))    # # lưu đường đi dựa vào A*
        
        for i in range(len(ans)):
            if not eaten_foods[i] and draw_foods[i]: 
                pacman_router(lst_trace)

        draw_player()

        player_circle = pygame.draw.circle(screen, 'black', (center_x + 1, center_y + 2), 30/2, 2)

        blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speeds[0], blinky_img, blinky_direction, blinky_dead, blinky_box, 0)
        inky = Ghost(inky_x, inky_y, targets[0], ghost_speeds[1], inky_img, inky_direction, inky_dead, inky_box, 1)
        pinky = Ghost(pinky_x, pinky_y, targets[0], ghost_speeds[2], pinky_img, pinky_direction, pinky_dead, pinky_box, 2)
        clyde = Ghost(clyde_x, clyde_y, targets[0], ghost_speeds[3], clyde_img, clyde_direction, clyde_dead, clyde_box, 3)
        draw_misc()

        targets = get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)
        turns_allowed = check_position(center_x, center_y)
        

        if moving:
            player_x, player_y = move_player(player_x, player_y)
            if not blinky_dead and not blinky.in_box:
                blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
            else:
                blinky_x, blinky_y, blinky_direction = blinky.move_clyde()

            if not pinky_dead and not pinky.in_box:
                pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
            else:
                pinky_x, pinky_y, pinky_direction = pinky.move_clyde()

            if not inky_dead and not inky.in_box:
                inky_x, inky_y, inky_direction = inky.move_inky()
            else:
                inky_x, inky_y, inky_direction = inky.move_clyde()

            clyde_x, clyde_y, clyde_direction = clyde.move_clyde()

        score, powerup, power_counter, eaten_ghost = check_collisons(score, powerup, power_counter, eaten_ghost)
        
        # check va chạm với ghost
        if not powerup:
            if (player_circle.colliderect(blinky.rect) and not blinky.dead) or \
                    (player_circle.colliderect(inky.rect) and not inky.dead) or \
                    (player_circle.colliderect(pinky.rect) and not pinky.dead) or \
                    (player_circle.colliderect(clyde.rect) and not clyde.dead):
                if lives > 0 :
                    lives -= 1
                    startup_counter = 0
                    powerup = False
                    power_counter = 0

                    player_x = 15 * cell_board            # vị trí x của pacman 
                    player_y = 24 * cell_board            # vị trí y của pacman 
                    direction = 0
                    direction_command = 0

                    blinky_x = 7 * 20
                    blinky_y = 6 * 20
                    blinky_direction = 0

                    pinky_x = 2 * 20
                    pinky_y = 27 * 20
                    pinky_direction = 0

                    inky_x = 13 * 20
                    inky_y = 15 * 20
                    inky_direction = 0

                    clyde_x = 16 * 20
                    clyde_y = 15 * 20
                    clyde_direction = 0

                    blinky_dead = False
                    inky_dead = False
                    clyde_dead = False
                    pinky_dead = False
                    eaten_ghost = [False] * len(ans)

                    index = 0
                    draw_foods[idx] = False
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0
        if powerup and player_circle.colliderect(blinky.rect) and eaten_ghost[0] and not blinky.dead:
            if lives > 0 :
                lives -= 1
                startup_counter = 0
                powerup = False
                power_counter = 0

                player_x = 15 * cell_board            # vị trí x của pacman 
                player_y = 24 * cell_board            # vị trí y của pacman 
                direction = 0
                direction_command = 0

                blinky_x = 7 * 20
                blinky_y = 6 * 20
                blinky_direction = 0

                pinky_x = 2 * 20
                pinky_y = 27 * 20
                pinky_direction = 0

                inky_x = 13 * 20
                inky_y = 15 * 20
                inky_direction = 0

                clyde_x = 16 * 20
                clyde_y = 15 * 20
                clyde_direction = 0

                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                eaten_ghost = [False] * len(ans)

                index = 0
                
            else:
                game_over = True
                moving = False
                startup_counter = 0
        if powerup and player_circle.colliderect(inky.rect) and eaten_ghost[1] and not inky.dead:
            if lives > 0 :
                lives -= 1
                startup_counter = 0
                powerup = False
                power_counter = 0

                player_x = 15 * cell_board            # vị trí x của pacman 
                player_y = 24 * cell_board            # vị trí y của pacman 
                direction = 0
                direction_command = 0

                blinky_x = 7 * 20
                blinky_y = 6 * 20
                blinky_direction = 0

                pinky_x = 2 * 20
                pinky_y = 27 * 20
                pinky_direction = 0

                inky_x = 13 * 20
                inky_y = 15 * 20
                inky_direction = 0

                clyde_x = 16 * 20
                clyde_y = 15 * 20
                clyde_direction = 0

                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                eaten_ghost = [False] * len(ans)

                index = 0
            else:
                game_over = True
                moving = False
                startup_counter = 0
        if powerup and player_circle.colliderect(pinky.rect) and eaten_ghost[2] and not pinky.dead:
            if lives > 0 :
                lives -= 1
                startup_counter = 0
                powerup = False
                power_counter = 0

                player_x = 15 * cell_board            # vị trí x của pacman 
                player_y = 24 * cell_board            # vị trí y của pacman 
                direction = 0
                direction_command = 0

                blinky_x = 7 * 20
                blinky_y = 6 * 20
                blinky_direction = 0

                pinky_x = 17 * 20
                pinky_y = 14 * 20
                pinky_direction = 0

                inky_x = 13 * 20
                inky_y = 15 * 20
                inky_direction = 0

                clyde_x = 16 * 20
                clyde_y = 15 * 20
                clyde_direction = 0

                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                eaten_ghost = [False] * len(ans)

                index = 0
            else:
                game_over = True
                moving = False
                startup_counter = 0
        if powerup and player_circle.colliderect(clyde.rect) and eaten_ghost[3] and not clyde.dead:
            if lives > 0 :
                lives -= 1
                startup_counter = 0
                powerup = False
                power_counter = 0

                player_x = 15 * cell_board            # vị trí x của pacman 
                player_y = 24 * cell_board            # vị trí y của pacman 
                direction = 0
                direction_command = 0

                blinky_x = 7 * 20
                blinky_y = 6 * 20
                blinky_direction = 0

                pinky_x = 2 * 20
                pinky_y = 27 * 20
                pinky_direction = 0

                inky_x = 13 * 20
                inky_y = 15 * 20
                inky_direction = 0

                clyde_x = 16 * 20
                clyde_y = 15 * 20
                clyde_direction = 0

                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                eaten_ghost = [False] * len(ans)

                index = 0
            else:
                game_over = True
                moving = False
                startup_counter = 0
        
        if powerup and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghost[0]:
            blinky_dead = True
            eaten_ghost[0] = True
            score += (2 ** eaten_ghost.count(True)) * 100
        if powerup and player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghost[1]:
            inky_dead = True
            eaten_ghost[1] = True
            score += (2 ** eaten_ghost.count(True)) * 100
        if powerup and player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghost[2]:
            pinky_dead = True
            eaten_ghost[2] = True
            score += (2 ** eaten_ghost.count(True)) * 100
        if powerup and player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghost[3]:
            clyde_dead = True
            eaten_ghost[3] = True
            score += (2 ** eaten_ghost.count(True)) * 100

        if blinky.in_box and blinky_dead:
            blinky_dead = False
        if inky.in_box and inky_dead:
            inky_dead = False
        if pinky.in_box and pinky_dead:
            pinky_dead = False
        if clyde.in_box and clyde_dead:
            clyde_dead = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and (game_over or game_won):
                startup_counter = 0
                powerup = False
                power_counter = 0

                player_x = j_pos_player * cell_board            # vị trí x của pacman (cột j)
                player_y = i_pos_player * cell_board            # vị trí y của pacman (cột i)
                direction = 0
                direction_command = 0

                blinky_x = 7 * 20
                blinky_y = 6 * 20
                blinky_direction = 0

                pinky_x = 2 * 20
                pinky_y = 27 * 20
                pinky_direction = 0

                inky_x = 13 * 20
                inky_y = 15 * 20
                inky_direction = 0

                clyde_x = 16 * 20
                clyde_y = 15 * 20
                clyde_direction = 0

                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                eaten_ghost = [False, False, False, False]
                score = 0
                lives = 3
                level = level_init
                game_over = False
                game_won = False

                power_food = 0
                draw_foods = [False] * len(ans)
                index = 0
                eaten_foods = [False] * len(ans)
                min_distance = 0
                idx = 0
                map_1_state_btn, map_2_state_btn, map_3_state_btn = [False] * 3

    pygame.display.flip()




pygame.quit()