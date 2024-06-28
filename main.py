# required modules
import pygame
import os
import sys
import time
import pickle

# Import Classes for different parts of the game
import Title
from race import Race
        
# The Main class inits the entire game with default game variables, such as the FPS, 
# screen height and width, etc.  It also initializes the player's key input bindings and states,
# and, finally moves the game from one major game state to another.
class Main:

    def __init__(self):
        sys.setrecursionlimit(100000)
    
        self.name = "AI RACER"
        self.FPS = 50  # 40-80 FPS range recommended, !!! NOTE: If altered too much, may also have to adjust player and NPC attributes accordingly!!!
        self.WIDTH = 1500
        self.HEIGHT = 1100
        self.colors = {"red": (255,0,0), "green": (0,128,0), "blue": (0,0,255), "black": (0,0,0), "white": (255,255,255), 
                        "yellow": (255,255,0), "darkgreen": (0,100,0), "skyblue": (135,206,235), "snow": (255, 250, 250),
                        "silver": (192,192,192), "lime": (0,255,0), "khaki": (240,230,140), "orange": (255,165,0), "paper": (242,242,242)}
        self.background_color = self.colors["white"]
        self.running = True
        
        pygame.init()
        self.display = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.caption = pygame.display.set_caption(self.name)
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        
        # Define variables to store critical game/player information to be shared 
        # across different game states/sequences -- Do not need to modify, these
        # are initialized by other class objects.
        self.player_selection = None
        self.level_selection = None
        self.player_attributes = None
        self.player_attributes = None
        self.ai_selection = None
        self.ai_train = None
        
        # Methods calls for more initializing...
        self.init_key_bindings()
        self.get_image_files()
        
        # Game is now setup, go to the title screen.
        self.init_title_screen()  
    
    # Loads game's image files from specified directories
    def get_image_files(self):
        self.car_image_directory = "race/car_sprite_images/"
        self.car_images = ["blue_car.png", "green_car.png", "red_car.png", "orange_car.png", "yellow_car.png", "purple_car.png", "navy_car.png", "pink_car.png", "white_car.png", "black_car.png", "forest_car.png"]
        
        self.level_image_directory = "race/levels/"
        self.level_images = []
        
        for image_file in os.listdir(self.level_image_directory):
            if image_file.endswith(".png"):
                self.level_images.append(image_file)
    
    # Called by the "Race" class--Initializes player attributes - may need to adjust/tune depending on game FPS 
    def init_player_attributes(self, player_selection, player_start_coords):
        # Set all attributes for the player
        player_attributes = {"IMAGE_FILE": player_selection, # sprite image file
                                  "MAX_SPEED": 350,         # Range 150 - 380
                                  "ACCEL": 2.9,             # Range .5 - 6
                                  "HANDLING": 3.15,         # Range 1.5 - 3.5  
                                  "DECELERATION": .025,     # .025
                                  "E_BRAKE_DECEL": .075,    # .075
                                  "E_BRAKE_HANDLING": 4,    # 4
                                  "HEALTH": 100,            # Not currently used
                                  "BOOST": 0,               # Not currently used
                                  "START_COORDS": (player_start_coords[0], player_start_coords[1], player_start_coords[2])} # x, y, & angle coords
        return player_attributes
    
    # Called by Race Class Obj--Initializes NPC attributes with a low / high range.  
    # A range is used instead of a single value to, which helps establish psudo-randomness 
    # between different NPCs. To make NPC's more challenging, increase attribute values / adjust the range
    def init_npc_attributes(self, npc_car_images, npcs, npc_start_coords, npc_waypoints ):
        npc_attributes = {"MAX_SPEED": (25,35),
                               "ACCEL": (.025, .05),     
                               "HANDLING": (2, 3),  
                               "DECELERATION": .025,
                               "IMAGE_FILES": npc_car_images,
                               "NPCS": npcs,
                               "NPC_START_COORDS": npc_start_coords,
                               "NPC_POINTS": npc_waypoints}                              
        return npc_attributes
    
    # Keyboard bindings
    def init_key_bindings(self):
        
        self.key = {"left": pygame.K_LEFT,
                    "right": pygame.K_RIGHT,
                    "up": pygame.K_UP,
                    "down": pygame.K_DOWN,
                    "escape": pygame.K_ESCAPE,
                    "enter": pygame.K_RETURN,
                    "forward": pygame.K_SPACE,
                    "e_brake": pygame.K_b,
                    "r_brake": pygame.K_r,
                    "boost": pygame.K_n}
        
        self.key_state = {"left": False,
                          "right": False,
                          "up": False,
                          "down": False,
                          "escape": False,
                          "enter": False,
                          "forward": False,
                          "e_brake": False,
                          "r_brake": False,
                          "boost": False,
                          "left_click": False}
                          
    # Checks for events (i.e. human player key inputs)                     
    def get_events(self):
        # Check for key input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
            if  event.type == pygame.KEYDOWN:
                if event.key == self.key["escape"]:
                    self.key_state["escape"] = True
                    self.running = False
                if event.key == self.key["enter"]:
                    self.key_state["enter"] = True
                if event.key == self.key["left"]:
                    self.key_state["left"] = True
                if event.key == self.key["right"]:
                    self.key_state["right"] = True
                if event.key == self.key["up"]:
                    self.key_state["up"] = True
                if event.key == self.key["down"]:
                    self.key_state["down"] = True
                if event.key == self.key["forward"]:
                   self.key_state["forward"] = True
                if event.key == self.key["e_brake"]:
                   self.key_state["e_brake"] = True
                if event.key == self.key["boost"]:
                    self.key_state["boost"] = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.key_state["left_click"] = True
            
            if  event.type == pygame.KEYUP:
                if event.key == self.key["enter"]:
                    self.key_state["enter"] = False
                if event.key == self.key["left"]:
                    self.key_state["left"] = False
                if event.key == self.key["right"]:
                    self.key_state["right"] = False
                if event.key == self.key["up"]:
                    self.key_state["up"] = False
                if event.key == self.key["down"]:
                    self.key_state["down"] = False
                if event.key == self.key["forward"]:
                    self.key_state["forward"] = False
                if event.key == self.key["e_brake"]:
                    self.key_state["e_brake"] = False
                if event.key == self.key["boost"]:
                    self.key_state["boost"] = False
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.key_state["left_click"] = False
    
    # Go to the game's Title Screen
    def init_title_screen(self):
        Title.Title(self)
        if self.running:
            self.save_game_state(self)  # Saves the initial race state (Req. to reload episodes for training the neural net)
            self.load_game_state()

    # Start the game's race sequence      
    def init_race(self):
        Race.Race(self)
        
    # Saves the initial race state (needed to reload new episodes for training the neural net)
    def save_game_state(self, game):
        # Can't pickle these object types
        self.display = None
        self.screen = None
        self.clock = None
        with open("./game_state/saved_game", "wb") as f:
            pickle.dump(game, f)
            
    # Reload the game's initial race state (restarts training episode)    
    def load_game_state(self):
        # Load a new pygame instance from save file
        with open("./game_state/saved_game", "rb") as f:
            game = pickle.load(f)
        # Re-init these objects on load
        game.clock = pygame.time.Clock()
        game.display = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        game.screen = pygame.display.get_surface()
        self.running = False # quit the old (current) instance
        game.init_race()     # Start a new race (i.e. a new training "episode")
        return

# Init game object
if __name__ == '__main__':
    Main()
