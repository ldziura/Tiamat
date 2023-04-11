import time
import board
import random
import gc
import busio
import displayio
import adafruit_imageload
import random
import math
import terminalio
import json


from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text import label

from adafruit_bitmapsaver import save_pixels
import storage

from kmk.extensions import Extension

big_circle_pos = [120, 120]  # Position of the bigger circle (center of the screen)
big_circle_radius = 125


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def cartesian_to_polar(x, y):
    r = math.sqrt(x * x + y * y)
    theta = math.atan2(y, x)
    return r, theta

def polar_to_cartesian(r, theta):
    """
    /!\ The angle is in radians /!\\
    """

    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y

def color_palette(colstr):

    colors = {
        'black': 0x000000,
        'white': 0xFFFFFF,
        'gray': 0x808080,
        'lightgray': 0xC0C0C0,
        'darkgray': 0x404040,
        'red': 0xFF0000,
        'green': 0x00FF00,
        'blue': 0x0000FF,
        'yellow': 0xFFFF00,
        'cyan': 0x00FFFF,
        'magenta': 0xFF00FF,
        'orange': 0xFFA500,
        'purple': 0x800080,
        'brown': 0xA52A2A,
        'pink': 0xFFC0CB,
        'lime': 0x00FF00,
        'teal': 0x008080,
        'maroon': 0x800000,
        'navy': 0x000080,
        'olive': 0x808000,
        'violet': 0xEE82EE,
        'turquoise': 0x40E0D0,
        'silver': 0xC0C0C0,
        'gold': 0xFFD700,
        'indigo': 0x4B0082,
        'coral': 0xFF7F50,
        'salmon': 0xFA8072,
        'tan': 0xD2B48C,
        'khaki': 0xF0E68C,
        'plum': 0xDDA0DD,
        'darkgreen': 0x006400
    }
    try:
        return colors[colstr]
    except:
        return [0x000000]

def star_points(center, num_points, outer_radius, inner_radius, rotation):
    points = []
    angle = math.pi / num_points
    for i in range(num_points * 2):
        radius = inner_radius if i % 2 == 0 else outer_radius
        current_angle = i * angle + math.radians(rotation)
        x = math.ceil(center[0] + math.cos(current_angle) * radius)
        y = math.ceil(center[1] + math.sin(current_angle) * radius)
        points.append((x, y))
    return points


class GameManager:

    def __init__(self, sprite_sheet, sprite_palette, title_sheet, title_palette):

        self.container_group = displayio.Group()

        self.title_spritesheet = title_sheet
        self.title_palette = title_palette

        self.sprite_sheet = sprite_sheet
        self.palette = sprite_palette


        # ===GAME START MENU===#

        self.game_start_menu_is_displayed = True


        self.start_menu_label_pos = {"Start": [120, 120], "Controls" : [120, 150], "Rules" : [120, 180]}
        self.start_menu_label_padding = {"Start": 50, "Controls": 70, "Rules": 50}
        self.start_menu_label_order = ["Start", "Controls", "Rules"]
        self.start_menu_label_gfx = {"Start": None, "Controls": None, "Rules": None}

        self.current_game_start_selected_text = "Start"

        #create start label
        self.start_label = label.Label(font=terminalio.FONT, text="Start", color=color_palette("gold"),
                                       x=self.start_menu_label_pos["Start"][0],
                                       y=self.start_menu_label_pos["Start"][1],
                                       anchor_point=(0.5, 0.5),
                                       anchored_position=(self.start_menu_label_pos["Start"][0], self.start_menu_label_pos["Start"][1]),
                                       scale=2)



        self.controls_label = label.Label(font=terminalio.FONT, text="Controls", color=color_palette("gold"),
                                          x=self.start_menu_label_pos["Controls"][0],
                                          y=self.start_menu_label_pos["Controls"][1],
                                          anchor_point=(0.5, 0.5),
                                          anchored_position=(self.start_menu_label_pos["Controls"][0], self.start_menu_label_pos["Controls"][1]),
                                          scale=2)

        # self.controls_label_gfx = displayio.TileGrid(self.sprite_sheet, pixel_shader=self.palette, width=1, height=1, tile_height=16, tile_width=16)
        # self.controls_label_gfx[0] = 9
        # self.controls_label_gfx.x = self.start_menu_label_pos["Controls"][0] - self.start_menu_label_padding["Controls"]
        # self.controls_label_gfx.y = self.start_menu_label_pos["Controls"][1] - 8

        self.rules_label = label.Label(font=terminalio.FONT, text="Rules", color=color_palette("gold"),
                                       x=self.start_menu_label_pos["Rules"][0],
                                       y=self.start_menu_label_pos["Rules"][1],
                                       anchor_point=(0.5, 0.5),
                                       anchored_position=(self.start_menu_label_pos["Rules"][0], self.start_menu_label_pos["Rules"][1]),
                                       scale=2)

        # self.rules_label_gfx = displayio.TileGrid(self.sprite_sheet, pixel_shader=self.palette, width=1, height=1, tile_height=16, tile_width=16)
        # self.rules_label_gfx[0] = 9
        # self.rules_label_gfx.x = self.start_menu_label_pos["Rules"][0] - self.start_menu_label_padding["Rules"]
        # self.rules_label_gfx.y = self.start_menu_label_pos["Rules"][1] - 8


        self.snake_title = displayio.TileGrid(self.title_spritesheet, pixel_shader=self.title_palette, width=5, height=1, tile_height=16, tile_width=16)
        self.snake_title[0] = 0
        self.snake_title[1] = 1
        self.snake_title[2] = 2
        self.snake_title[3] = 3
        self.snake_title[4] = 4

        self.snake_title.x = 20
        self.snake_title.y = 20

        self.start_menu = displayio.Group(scale=1)

        self.snake_title_group = displayio.Group(scale=2)
        self.snake_title_group.append(self.snake_title)

        self.start_menu.append(self.snake_title_group)

        self.start_menu.append(self.start_label)
        # self.start_menu.append(self.start_label_gfx)

        self.start_menu.append(self.controls_label)
        # self.start_menu.append(self.controls_label_gfx)

        self.start_menu.append(self.rules_label)
        # self.start_menu.append(self.rules_label_gfx)

        # self.container_group.append(self.start_menu)




        #===GRAPHICS===#

        self.sprite_sheet = sprite_sheet
        self.palette = sprite_palette

        #create a sprite
        self.fruit_gfx = displayio.TileGrid(self.sprite_sheet, pixel_shader=self.palette, width=1, height=1, tile_height=16, tile_width=16)
        self.fruit_gfx[0] = 6

        #===SCORE MANAGEMENT===#

        self.score = 0
        self.score_pos = [120, 120]

        #display the score
        self.score_text = label.Label(font=terminalio.FONT, text="SCORE", color=color_palette("turquoise"), x=self.score_pos[0], y=self.score_pos[1]-10, anchor_point=(0.5, 0.5), anchored_position=(self.score_pos[0], self.score_pos[1]-10))
        self.score_number = label.Label(font=terminalio.FONT, text="0", color=color_palette("gold"), x=self.score_pos[0], y=self.score_pos[1]+10, anchor_point=(0.5, 0.5), anchored_position=(self.score_pos[0], self.score_pos[1]+10))

        #create a circle for the outer bound
        self.outer_bound = Circle(big_circle_pos[0], big_circle_pos[1], 119, outline=color_palette("red"))

        #create a circle for the inner bound
        self.inner_bound = Circle(big_circle_pos[0], big_circle_pos[1], 25, outline=color_palette("red"))


        #create a group to hold the score
        self.score_group = displayio.Group()
        self.score_group.append(self.outer_bound)
        self.score_group.append(self.inner_bound)
        self.score_group.append(self.score_text)
        self.score_group.append(self.score_number)


        self.scoreboard = None


        #===FRUIT MANAGEMENT===#

        self.fruit_size = 4


        #list of all the fruits
        self.fruits = ["apple", "cherry" ,"strawberry", "orange", "banana", "pear"]
        #dictionnary of all the fruits and their score
        self.fruits_score = {"apple": 1, "cherry": 1, "strawberry": 1, "orange": 2, "banana": 2, "pear": 2}

        #init first fruit at random
        self.current_fruit = random.choice(self.fruits)

        # random fruit pos in polar coordinates
        self.current_fruit_angle = random.randint(0, 360)
        self.current_fruit_radius = random.randint(25 + 20, 119 - 20)

        current_fruit_pos = polar_to_cartesian(self.current_fruit_radius, math.radians(self.current_fruit_angle))
        self.current_fruit_pos = [int(current_fruit_pos[0]), int(current_fruit_pos[1])]


        self.fruit_group = displayio.Group()
        self.fruit_group.append(self.fruit_gfx)

        #create the fruit
        self.create_fruit()


        #===SNAKE MANAGEMENT===#


        self.snake_size = 6
        self.snake = Snake(120, 120, self.snake_size, color_palette("purple"))

        self.snake_group = displayio.Group()
        self.snake_group.append(self.snake.group)

        self.snake_group.x = -self.snake_size
        self.snake_group.y = -self.snake_size


        #===GAME OVER MENU SCREEN===#

        self.game_over = False
        self.game_over_menu_is_displayed = False
        self.game_over_screen_radius = 0

        self.game_over_group = displayio.Group()

        #==TEXT==#

        self.game_over_pos = [120, 50]
        #create game over text
        self.game_over_text = label.Label(terminalio.FONT, text="GAME OVER", color=0xFFFFFF, x=self.game_over_pos[0], y=self.game_over_pos[1], anchor_point=(0.5, 0.5), anchored_position=(self.game_over_pos[0], self.game_over_pos[1]), scale=3)


        #create selectable text dict
        self.game_over_menu_label_order = ["Retry", "Quit"]
        self.game_over_menu_pos = {"Retry": [120, 85], "Quit": [120, 115]}
        self.game_over_menu_label_padding = {"Retry": 55, "Quit": 50}
        self.game_over_menu_label_gfx = {"Retry": None, "Quit": None}

        self.current_game_over_selected_text = "Retry"


        self.retry_text = label.Label(terminalio.FONT, text="Retry", color=0xFFFFFF,
                                      x=self.game_over_menu_pos["Retry"][0],
                                      y=self.game_over_menu_pos["Retry"][1],
                                      anchor_point=(0.5, 0.5),
                                      anchored_position=(self.game_over_menu_pos["Retry"][0], self.game_over_menu_pos["Retry"][1]),
                                      scale=2)
        self.quit_text = label.Label(terminalio.FONT, text="Quit", color=0xFFFFFF,
                                     x=self.game_over_menu_pos["Quit"][0],
                                     y=self.game_over_menu_pos["Quit"][1],
                                     anchor_point=(0.5, 0.5),
                                     anchored_position=(self.game_over_menu_pos["Quit"][0], self.game_over_menu_pos["Quit"][1]),
                                     scale=2)


        self.highscore_pos = [120, 150]
        self.highscore_num_offset = 24
        self.highscore_text = label.Label(terminalio.FONT, text="Highscores", color=0xFFFFFF,
                                          x=self.highscore_pos[0],
                                          y=self.highscore_pos[1],
                                          anchor_point=(0.5, 0.5),
                                          anchored_position=(self.highscore_pos[0], self.highscore_pos[1]),
                                          scale=2)

        self.highscore_number_text_0 = label.Label(terminalio.FONT, text="0", color=0xFFFFFF,
                                            x=self.highscore_pos[0],
                                            y=self.highscore_pos[1]+self.highscore_num_offset,
                                            anchor_point=(0.5, 0.5),
                                            anchored_position=(self.highscore_pos[0], self.highscore_pos[1]+self.highscore_num_offset),
                                            scale=2)

        self.highscore_number_text_1 = label.Label(terminalio.FONT, text="1", color=0xFFFFFF,
                                            x=self.highscore_pos[0],
                                            y=self.highscore_pos[1]+self.highscore_num_offset*2,
                                            anchor_point=(0.5, 0.5),
                                            anchored_position=(self.highscore_pos[0], self.highscore_pos[1]+self.highscore_num_offset*2),
                                            scale=2)

        self.highscore_number_text_2 = label.Label(terminalio.FONT, text="2", color=0xFFFFFF,
                                            x=self.highscore_pos[0],
                                            y=self.highscore_pos[1]+self.highscore_num_offset*3,
                                            anchor_point=(0.5, 0.5),
                                            anchored_position=(self.highscore_pos[0], self.highscore_pos[1]+self.highscore_num_offset*3),
                                            scale=2)

        self.highest_score_gfx_L = displayio.TileGrid(self.sprite_sheet, pixel_shader=self.palette, width=1, height=1, tile_width=16, tile_height=16,
                                                    default_tile=6,
                                                    x=self.highscore_pos[0] - 40,
                                                    y=self.highscore_pos[1] + 15)

        self.highest_score_gfx_R = displayio.TileGrid(self.sprite_sheet, pixel_shader=self.palette, width=1, height=1, tile_width=16, tile_height=16,
                                                    default_tile=6,
                                                    x=self.highscore_pos[0]-16 + 40,
                                                    y=self.highscore_pos[1] + 15,)




        self.game_over_menu = displayio.Group()
        self.game_over_menu.append(self.game_over_text)
        self.game_over_menu.append(self.retry_text)
        self.game_over_menu.append(self.quit_text)
        self.game_over_menu.append(self.highscore_text)
        self.game_over_menu.append(self.highscore_number_text_0)
        self.game_over_menu.append(self.highscore_number_text_1)
        self.game_over_menu.append(self.highscore_number_text_2)
        self.game_over_menu.append(self.highest_score_gfx_L)
        self.game_over_menu.append(self.highest_score_gfx_R)

        # add the text
        self.game_over_group.append(self.game_over_menu)







        self.display_start_menu()


    def start_game(self):

        print("loading game...")

        # create a new snake
        self.snake.reset_snake()

        # reset the score
        self.reset_score()

        # set game over to false
        self.game_over = False

        # remove all groups
        for i in range(len(self.container_group)):
            del self.container_group[0]

        self.game_start_menu_is_displayed = False
        self.game_over_menu_is_displayed = False

        #==ADD ALL GROUPS TO THE MAIN GROUP==#
        self.container_group.append(self.fruit_group)
        self.container_group.append(self.snake_group)
        self.container_group.append(self.score_group)

        self.snake.move_left(input=True)

        print("game loaded")

    def update_score(self):

        self.score_number.text = str(self.score)

    def reset_score(self):

        self.score = 0
        self.update_score()

    def add_score(self, score):

        self.score += score
        self.update_score()

    def create_fruit(self):

        self.current_fruit = random.choice(self.fruits)

        #random fruit pos in polar coordinates
        self.current_fruit_angle = random.randint(0, 360)
        self.current_fruit_radius = random.randint(25+20, 119-20)

        # print(f"fruit angle: {self.current_fruit_angle}, fruit radius: {self.current_fruit_radius}")

        #convert to carthesian
        current_fruit_pos = polar_to_cartesian(self.current_fruit_radius, math.radians(self.current_fruit_angle))
        self.current_fruit_pos = [int(current_fruit_pos[0]+120), int(current_fruit_pos[1]+120)]

        # print(f"fruit pos: {self.current_fruit_pos}")

        # fruit_shape = Circle(self.current_fruit_pos[0], self.current_fruit_pos[1], self.fruit_size, fill=self.fruits_color[self.current_fruit], outline=self.fruits_color[self.current_fruit])

        #chose a random fruit sprite
        self.fruit_gfx[0] = random.randint(0, 5)
        self.fruit_gfx.x = self.current_fruit_pos[0]-8
        self.fruit_gfx.y = self.current_fruit_pos[1]-8




        # self.fruit_group.append(fruit_shape)

    def check_fruit_collision(self):

        # print("checking fruit collision")

        snake_head_pos = self.snake.pos

        # print(f"snake head pos: {snake_head_pos}, fruit pos: {self.current_fruit_pos}")

        distance_between = distance(snake_head_pos, self.current_fruit_pos)

        # print(f"distance between: {distance_between}")

        if distance_between <= self.snake.radius + self.fruit_size:
            # print("fruit collision detected")

            # print(f"fruit is worth {self.fruits_score[self.current_fruit]} points")

            # del self.fruit_group[-1]
            self.add_score(self.fruits_score[self.current_fruit])
            # print("added score")

            self.create_fruit()
            # print("created new fruit")

            self.snake.grow()
            # print("grew snake")

    def check_win_lose_condition(self):

        if self.snake.is_dead:
            # print("game over")
            self.game_over = True

    def play_game_over_animation(self):


        #remove all groups
        for i in range(len(self.container_group)):
            del self.container_group[0]

        self.container_group.append(self.game_over_group)


        self.game_over_screen_radius = 120
        self.game_over_group.insert(0, Circle(120, 120, self.game_over_screen_radius, fill=0x680000))

    def display_start_menu(self):

        self.game_start_menu_is_displayed = True
        self.game_over_menu_is_displayed = False

        for i in range(len(self.container_group)):
            #del all groups
            del self.container_group[0]

        self.container_group.append(self.start_menu)
        # self.container_group.append(self.select_arrow_group)

        # self.update_arrow_pos()
        self.update_labels_arrow_bullet_point()

    def display_game_over_menu(self):

        print("---displaying game over menu")

        self.game_over_menu_is_displayed = True


        self.load_scoreboard()

        print("loaded scoreboard")
        print(self.scoreboard)
        self.update_scoreboard()

        self.set_highscores()

        try:
            self.save_scoreboard()
        except:
            print("could not save scoreboard")

        # self.update_arrow_pos()
        self.update_labels_arrow_bullet_point()

        print("---finished displaying game over menu")


        # self.quit_text.text = str(self.scoreboard[3])

    def update_labels_arrow_bullet_point(self):


        if self.game_start_menu_is_displayed:

            print(f"current game start selected text: {self.current_game_start_selected_text}")

            for label in self.start_menu_label_order:

                bp = self.start_menu_label_gfx[label]

                if bp is None:
                    print(f"bullet point for {label} is none in start menu")
                    self.add_menu_bullet_point(label, "start_menu")
                    bp = self.start_menu_label_gfx[label]


                if label == self.current_game_start_selected_text:
                    print(f"label {label} is selected")

                    bp[0] = 8

                else:
                    # print(f"label {label} is not selected")
                    bp[0] = 9



        elif self.game_over_menu_is_displayed:

            print(f"current game over selected text: {self.current_game_over_selected_text}")

            for label in self.game_over_menu_label_order:

                bp = self.game_over_menu_label_gfx[label]

                if bp is None:
                    print(f"bullet point for {label} is none in game over menu")
                    self.add_menu_bullet_point(label, "game_over")
                    bp = self.game_over_menu_label_gfx[label]

                if label == self.current_game_over_selected_text:
                    print(f"label {label} is selected")

                    bp[0] = 8

                else:

                    # print(f"label {label} is not selected")
                    bp[0] = 9


        else:
            print("no menu is displayed")

    def add_menu_bullet_point(self, label, menu):

        if menu == "start_menu":
            label_pos = self.start_menu_label_pos[label]
            label_padding = self.start_menu_label_padding[label]

            group_to_add = self.start_menu
            gfx_list = self.start_menu_label_gfx

        elif menu == "game_over":
            label_pos = self.game_over_menu_pos[label]
            label_padding = self.game_over_menu_label_padding[label]

            group_to_add = self.game_over_menu
            gfx_list = self.game_over_menu_label_gfx

        else:
            print("menu not found")
            return

        bullet_point = displayio.TileGrid(self.sprite_sheet, pixel_shader=self.palette, width=1, height=1, tile_height=16, tile_width=16)
        bullet_point[0] = 9
        bullet_point.x = label_pos[0] - label_padding
        bullet_point.y = label_pos[1] - 8

        gfx_list[label]=bullet_point

        group_to_add.append(bullet_point)

    def move_arrows(self, direction):

        #get current menu mode (game over or start menu)
        if self.game_over_menu_is_displayed:
            menu_mode = "game_over"

            menu_list = self.game_over_menu_label_order

            c_selected = self.current_game_over_selected_text
            c_selected_index = self.game_over_menu_label_order.index(c_selected)


        elif self.game_start_menu_is_displayed:
            menu_mode = "start_menu"

            menu_list = self.start_menu_label_order

            c_selected = self.current_game_start_selected_text
            c_selected_index = self.start_menu_label_order.index(c_selected)

        else:
            print("error: no menu is displayed")
            return

        print(f"current selected: {c_selected}")
        print(f"current selected index: {c_selected_index}")
        print(f"menu list: {menu_list}")
        print(f"menu mode: {menu_mode}")


        if direction == "up":
            print("moving up")
            #if the index is not the first one, move the arrow up
            if c_selected_index != 0:

                    #get the new selected text
                    new_selected = menu_list[c_selected_index - 1]


                    if menu_mode == "start_menu":
                        self.current_game_start_selected_text = new_selected
                    elif menu_mode == "game_over":
                        self.current_game_over_selected_text = new_selected


                    #move the arrow
                    self.update_labels_arrow_bullet_point()

            else:
                print("already at the top")

        elif direction == "down":

            print("moving down")


            # if the index is not the last one, move the arrow down
            if c_selected_index != len(menu_list)-1:


                # get the new selected text
                new_selected = menu_list[c_selected_index + 1]

                if menu_mode == "start_menu":
                    self.current_game_start_selected_text = new_selected
                elif menu_mode == "game_over":
                    self.current_game_over_selected_text = new_selected

                # move the arrow
                self.update_labels_arrow_bullet_point()

    def select_menu(self):

        if self.game_start_menu_is_displayed:

            if self.current_game_start_selected_text == "Start":
                print("start")
                self.start_game()
                return

            elif self.current_game_start_selected_text == "Quit":
                print("quit")
                return

        elif self.game_over_menu_is_displayed:


            if self.current_game_over_selected_text == "Retry":
                print("retry")
                self.retry()
                return

            elif self.current_game_over_selected_text == "Quit":
                print("quit")
                self.quit()
                return

        else:
            print("no menu is displayed")

    def retry(self):

        print("deleting the circle")
        del self.game_over_group[0]

        #reset the game
        self.start_game()

    def quit(self):


        print("deleting the circle")
        del self.game_over_group[0]

        self.display_start_menu()


    def load_scoreboard(self):

        #load scoreboard from json file
        with open("scoreboard.json", "r") as f:
            scoreboard = json.load(f)

            self.scoreboard = scoreboard["scoreboard"]

        #close the file
        f.close()

    def save_scoreboard(self):

        scoreboard = {"scoreboard": self.scoreboard}

        #save scoreboard to json file
        with open("scoreboard.json", "w") as f:
            json.dump(scoreboard, f)
        #close the file
        f.close()

    def update_scoreboard(self):

        #check if the score is higher than the lowest score in the scoreboard
        if self.score > self.scoreboard[2]:

            #if it is, add it to the scoreboard
            self.scoreboard.append(self.score)

            #sort the scoreboard
            self.scoreboard.sort(reverse=True)

            #remove the lowest score
            self.scoreboard.pop()

            #save the scoreboard
            # self.save_scoreboard()

    def set_highscores(self):

        #set the highscores
        self.highscore_number_text_0.text = str(self.scoreboard[0])
        self.highscore_number_text_1.text = str(self.scoreboard[1])
        self.highscore_number_text_2.text = str(self.scoreboard[2])





class Snake:

    def __init__(self, x, y, radius, color):
        """
        Initializes a Snake object with the given parameters.

        :param x: The starting x-coordinate of the snake's head.
        :param y: The starting y-coordinate of the snake's head.
        :param radius: The radius of the snake's head and body parts.
        :param color: The color of the snake's head and body parts.
        """

        self.is_dead = False

        # initialize position and bounds
        self.pos = [x, y]
        self.inner_bound = 24
        self.outer_bound = 120

        # initialize angle and radius center
        self.angle = 0
        self.radius_center = 100

        # initialize flip and direction
        self.flip = False
        self.direction = ["up", "down", "left", "right"]
        self.current_direction = None
        self.last_input_direction = None

        # initialize speed
        self.angular_speed = 5
        self.radial_speed = 5

        # initialize radius and color
        self.radius = radius
        self.color = color

        # initialize snake head
        self.snake_head = Circle(self.pos[0], self.pos[1], self.radius, fill=self.color, outline=self.color)

        # initialize body parts
        self.body_parts = []
        self.sneak_head_last_pos = [self.pos,]

        # initialize snake head direction
        self.snake_head_direction = []

        # initialize displayio group
        self.group = displayio.Group()
        self.group.append(self.snake_head)

    def update_position(self):



        self_col = self.check_self_collision()
        if self_col:
            self.is_dead = True
            # print("snake is dead")

        # convert polar coordinates back to x,y
        c_x, c_y = polar_to_cartesian(self.radius_center, math.radians(self.angle))

        self.pos[0] = int(c_x + 120)
        self.pos[1] = int(c_y + 120)

        self.snake_head.x = self.pos[0]
        self.snake_head.y = self.pos[1]



        # update the position of the body parts
        self.move_snake_body()

        # print(f"sneak head array pos: {self.sneak_head_last_pos}")
        #keep as much elements in the array as there are body parts
        if len(self.sneak_head_last_pos) > len(self.body_parts):
            self.sneak_head_last_pos.pop(0)


        if len(self.snake_head_direction) > len(self.body_parts):
            self.snake_head_direction.pop(0)

        # print(f"snake head direction: {self.snake_head_direction}")

        self.snake_head_direction.append(self.current_direction)


        #print(f"ball pos: {self.pos}, shape pos: {self.shape.x}, {self.shape.y}")

    def add_body_part(self, radius, color):
        #create a new body part for the snake
        body_part = Circle(self.pos[0]+int(self.radius), self.pos[1]+int(self.radius), radius, fill=color, outline=color)
        self.body_parts.append(body_part)

        #add the body part to the group
        self.group.insert(0, body_part)

        # print(f"body part added, length: {len(self.body_parts)}")

    def grow(self):

        # print("growing")

        if len(self.body_parts)%2 == 0:
            color = color_palette("lime")
        else:
            color = color_palette("teal")
        #add a new body part to the snake
        self.add_body_part(self.radius, color)

    def check_self_collision(self):

        if len(self.body_parts) < 7:
            return False

        number_of_parts_to_check =  math.ceil((self.radius_center * (len(self.body_parts)-7))/(self.outer_bound-5))

        #print(f"number of parts to check: {number_of_parts_to_check}")


        #check the last n body parts, n being the number of body parts
        for i in range(number_of_parts_to_check):

                # print(f"checking body part {i}")

                #get the position of the body part
                body_part_pos = [self.body_parts[i].x, self.body_parts[i].y]

                # print(f"body part pos: {body_part_pos}")

                #check if the body part is within the radius of the snake head
                distance_between = distance(self.pos, body_part_pos)

                # print(f"distance between: {distance_between}")

                if distance_between <= self.radius*2:
                    #print("self collision detected")
                    return True

    def move_snake_head(self, angle=0, angle_dir=1, radius_center=0, radius_dir=1):


        old_x = self.pos[0]
        old_y = self.pos[1]

        self.sneak_head_last_pos.append([old_x, old_y])
        # print("snake moving")

        old_angle = self.angle
        old_radius_center = self.radius_center

        if self.flip:
            angle_dir *= -1
            radius_dir *= -1

        #increment angle by 1
        self.angle += angle * angle_dir
        self.radius_center += radius_center * radius_dir



        #if snake is going up check if radius_center is out of bounds
        if self.current_direction == "up":
            if self.radius_center > self.outer_bound-self.radius*2:
                # print("radius_center out of bounds up")
                self.radius_center = self.outer_bound-self.radius*2
                self.move_left()
                self.last_input_direction = "left"


        #if snake is going downn check if center is out of bounds
        if self.current_direction == "down":
            if self.radius_center < self.inner_bound+self.radius*2:
                # print("radius_center out of bounds down")
                self.radius_center = self.inner_bound+self.radius*2
                self.move_right()
                self.last_input_direction = "right"


        #compare old radius center with new radius center to see if we crossed the 0 point
        #if old radius is negative we approached the 0 point from the negative side
        #if old radius is positive we approached the 0 point from the positive side

        if old_radius_center <= 0:
            if self.radius_center > 0:
                # print("crossed 0 point from negative side")
                self.flip = False

        if old_radius_center >= 0:
            if self.radius_center < 0:
                # print("crossed 0 point from positive side")
                self.flip = True


        self.update_position()

    def move_snake_body(self):

        if len(self.body_parts) == 0:
            return
        # update the position of the body parts
        for i, body_part in enumerate(self.body_parts):
            # print(f"body part pos: {self.sneak_head_last_pos[i]}")
            body_part.x = self.sneak_head_last_pos[i][0]
            body_part.y = self.sneak_head_last_pos[i][1]

    def reset_snake(self):

        self.is_dead = False

        self.angle = 0
        self.radius_center = 100

        self.current_direction = None
        self.last_input_direction = None

        self.body_parts = []
        self.sneak_head_last_pos = [self.pos, ]
        self.snake_head_direction = []

        self.update_position()

    def move_left(self, input=False):

        if input:
            if self.last_input_direction == "left" or self.last_input_direction == "right":
                return

        self.current_direction = "left"
        self.move_snake_head(angle=self.angular_speed, angle_dir=-1)


        if input:
            self.last_input_direction = "left"

    def move_right(self, input=False):

        if input:
            if self.last_input_direction == "left" or self.last_input_direction == "right":
                return

        self.current_direction = "right"
        self.move_snake_head(angle=self.angular_speed, angle_dir=+1)

        if input:
            self.last_input_direction = "right"

    def move_up(self, input=False):

        if input:
            if self.last_input_direction == "up" or self.last_input_direction == "down":
                return

        self.current_direction = "up"
        self.move_snake_head(radius_center=self.radial_speed, radius_dir=+1)


        if input:
            self.last_input_direction = "up"

    def move_down(self, input=False):

        if input:
            if self.last_input_direction == "up" or self.last_input_direction == "down":
                return

        self.current_direction = "down"
        self.move_snake_head(radius_center=self.radial_speed, radius_dir=-1)


        if input:
            self.last_input_direction = "down"

    def continue_move(self):

        #continue moving in the same direction as last move
        if self.current_direction == "left":
            self.move_left()
        elif self.current_direction == "right":
            self.move_right()
        elif self.current_direction == "up":
            self.move_up()
        elif self.current_direction == "down":
            self.move_down()
        else:

            #print("no direction set")
            return


class Display(Extension):
    # REF: https://github.com/todbot/CircuitPython_GC9A01_demos
    # REF: https://github.com/KMKfw/kmk_firmware/tree/master/kmk/extensions

    # GC9A01 display initialization sequence
    _INIT_SEQUENCE = bytearray(
        b"\xFE\x00"  # Inter Register Enable1 (FEh)
        b"\xEF\x00"  # Inter Register Enable2 (EFh)
        b"\xB6\x02\x00\x00"  # Display Function Control (B6h) [S1→S360 source, G1→G32 gate]
        b"\x36\x01\x88"  # Memory Access Control(36h) [Invert Row order, BGR color]
        b"\x3a\x01\x05"  # COLMOD: Pixel Format Set (3Ah) [16 bits / pixel]
        b"\xC3\x01\x13"  # Power Control 2 (C3h) [VREG1A = 5.06, VREG1B = 0.68]
        b"\xC4\x01\x13"  # Power Control 3 (C4h) [VREG2A = -3.7, VREG2B = 0.68]
        b"\xC9\x01\x22"  # Power Control 4 (C9h)
        b"\xF0\x06\x45\x09\x08\x08\x26\x2a"  # SET_GAMMA1 (F0h)
        b"\xF1\x06\x43\x70\x72\x36\x37\x6f"  # SET_GAMMA2 (F1h)
        b"\xF2\x06\x45\x09\x08\x08\x26\x2a"  # SET_GAMMA3 (F2h)
        b"\xF3\x06\x43\x70\x72\x36\x37\x6f"  # SET_GAMMA4 (F3h)
        b"\x66\x0a\x3c\x00\xcd\x67\x45\x45\x10\x00\x00\x00"
        b"\x67\x0a\x00\x3c\x00\x00\x00\x01\x54\x10\x32\x98"
        b"\x74\x07\x10\x85\x80\x00\x00\x4e\x00"
        b"\x98\x02\x3e\x07"
        b"\x35\x00"  # Tearing Effect Line ON (35h) [both V-blanking and H-blanking]
        b"\x21\x00"  # Display Inversion ON (21h)
        b"\x11\x80\x78"  # Sleep Out Mode (11h) and delay(120)
        b"\x29\x80\x14"  # Display ON (29h) and delay(20)
        b"\x2a\x04\x00\x00\x00\xef"  # Column Address Set (2Ah) [Start col = 0, end col = 239]
        b"\x2b\x04\x00\x00\x00\xef"  # Row Address Set (2Bh) [Start row = 0, end row = 239]
    )

    def __init__(self):

        # Init display hardware with manual refresh control
        displayio.release_displays()

        self.display_spi = busio.SPI(clock=board.LCD_CLK, MOSI=board.LCD_DIN)

        self.display_bus = displayio.FourWire(
            self.display_spi,
            baudrate=62500000,
            command=board.LCD_DC,
            chip_select=board.LCD_CS,
            reset=board.LCD_RST)

        self.display = displayio.Display(
            self.display_bus,
            Display._INIT_SEQUENCE,
            width=240, height=240,
            backlight_pin=board.LCD_BL,
            auto_refresh=False)

        # ================================

        gc.collect()

        # Load the sprite sheet (bitmap)
        self.sp_sheet, self.sp_palette = adafruit_imageload.load("/Sprite_Sheet.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)

        self.ti_sheet, self.ti_palette = adafruit_imageload.load("/Snake_Title.bmp", bitmap=displayio.Bitmap, palette=displayio.Palette)

        # make the color at 0 index transparent.
        self.sp_palette.make_transparent(2)
        self.ti_palette.make_transparent(0)


        self.game_manager = GameManager(sprite_sheet=self.sp_sheet, sprite_palette=self.sp_palette, title_sheet=self.ti_sheet, title_palette=self.ti_palette)
        self.snake = self.game_manager.snake

        #add groups to display
        self.game_group = displayio.Group()
        self.game_group.append(self.game_manager.container_group)



        self.display.show(self.game_group)


        # self.snake_group.x = -5
        # self.snake_group.y = -5

        self.move_right()

        # Manual refresh
        self.display.refresh()
        gc.collect()



    def on_runtime_enable(self, sandbox):
        return

    def on_runtime_disable(self, sandbox):
        return

    def during_bootup(self, sandbox):
        return

    def before_matrix_scan(self, sandbox):
        return

    def after_matrix_scan(self, sandbox):
        return

    def before_hid_send(self, sandbox):
        return

    def on_powersave_enable(self, sandbox):
        return

    def on_powersave_disable(self, sandbox):
        return

    def after_hid_send(self, sandbox):

        self.snake.continue_move()
        self.game_manager.check_fruit_collision()
        self.game_manager.check_win_lose_condition()

        if self.game_manager.game_over:

            if self.game_manager.game_over_menu_is_displayed or self.game_manager.game_start_menu_is_displayed:
                return

            #remove snake group
            # self.display_group.remove(self.snake_group)
            # print("starting death animation")
            #
            time.sleep(0.5)

            for i in range(len(self.snake.body_parts)):

                # print("delete")
                #remove body parts
                del self.snake.group[-2]
                self.display.refresh()
                gc.collect()
                time.sleep(1/len(self.snake.body_parts))

            print("finished death animation")

            # self.display_group.remove(self.snake_group)

            time.sleep(0.3)

            self.game_manager.play_game_over_animation()

            self.display.refresh()
            gc.collect()

            print("call to display game over menu")
            self.game_manager.display_game_over_menu()

            self.display.refresh()
            gc.collect()


        self.display.refresh()
        gc.collect()

    def move_left(self):

        if self.game_manager.game_over_menu_is_displayed or self.game_manager.game_start_menu_is_displayed:
            # print("we are in the menu")
            pass
        else:
            self.snake.move_left(input=True)

        self.display.refresh()
        gc.collect()

    def move_right(self):

        if self.game_manager.game_over_menu_is_displayed or self.game_manager.game_start_menu_is_displayed:
            # print("we are in the menu")
            pass
        else:
            self.snake.move_right(input=True)

        self.display.refresh()
        gc.collect()

    def move_up(self):

        if self.game_manager.game_over_menu_is_displayed or self.game_manager.game_start_menu_is_displayed:
            # print("we are in the menu")
            self.game_manager.move_arrows(direction="up")

        else:
            self.snake.move_up(input=True)

        self.display.refresh()
        gc.collect()

    def move_down(self):

        if self.game_manager.game_over_menu_is_displayed or self.game_manager.game_start_menu_is_displayed:
            # print("we are in the menu")
            self.game_manager.move_arrows(direction="down")

        else:
            self.snake.move_down(input=True)

        self.display.refresh()
        gc.collect()

    def select(self):

        if self.game_manager.game_over_menu_is_displayed or self.game_manager.game_start_menu_is_displayed:
            self.game_manager.select_menu()

        #refresh display
        self.display.refresh()
        gc.collect()

    def create_body(self):

        # self.snake.grow()
        # self.game_manager.create_fruit()
        # self.game_manager.add_score(1)
        for i in range(20):
            self.snake.grow()
            self.snake.continue_move()
            time.sleep(0.05)
            self.display.refresh()
            gc.collect()

        self.game_manager.score = 1001
        self.game_manager.update_score()

        self.display.refresh()
        gc.collect()

    def screenshot(self):


        #create a label to inform the user that a screenshot is being taken
        screenshot_label = label.Label(terminalio.FONT, text="Taking Screenshot...", color=0x000000, x=120, y=120, anchor_point=(0.5, 0.5), anchored_position=(120, 100), scale=1)
        may_take_a_wile_label = label.Label(terminalio.FONT, text="This may take a while", color=0x000000, x=120, y=130, anchor_point=(0.5, 0.5), anchored_position=(120, 120), scale=1)
        do_not_unplug_label = label.Label(terminalio.FONT, text="Do not unplug the device", color=0x000000, x=120, y=140, anchor_point=(0.5, 0.5), anchored_position=(120, 140), scale=1)

        #create a rounded rectangle to display the label
        back_rec = RoundRect(30, 70, 180, 100, 5, fill=color_palette("white"), outline=color_palette("gold"), stroke=2)

        #add the label to the display group
        self.game_group.append(back_rec)
        self.game_group.append(screenshot_label)
        self.game_group.append(may_take_a_wile_label)
        self.game_group.append(do_not_unplug_label)



        #refresh the display
        self.display.refresh()
        gc.collect()

        time.sleep(4)

        # remove the label from the display group
        self.game_group.remove(screenshot_label)
        self.game_group.remove(may_take_a_wile_label)
        self.game_group.remove(do_not_unplug_label)
        self.game_group.remove(back_rec)

        # refresh the display
        self.display.refresh()
        gc.collect()


        try:
            save_pixels(file_or_filename='/screenshot.bmp', pixel_source=self.display)
        except:
            print("Error while saving the screenshot")
            time.sleep(3)
            pass



        screenshot_has_been_taken = label.Label(terminalio.FONT, text="Screenshot has been taken", color=0x000000, x=120, y=110, anchor_point=(0.5, 0.5), anchored_position=(120, 110), scale=1)
        resume = label.Label(terminalio.FONT, text="The game will resume", color=0x000000, x=120, y=130, anchor_point=(0.5, 0.5), anchored_position=(120, 130), scale=1)


        #add the label to the display group
        self.game_group.append(back_rec)
        self.game_group.append(screenshot_has_been_taken)
        self.game_group.append(resume)

        # refresh the display
        self.display.refresh()
        gc.collect()


        time.sleep(4)

        # remove the label from the display group
        self.game_group.remove(screenshot_has_been_taken)
        self.game_group.remove(resume)
        self.game_group.remove(back_rec)

        # refresh the display
        self.display.refresh()
        gc.collect()

