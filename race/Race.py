# required modules
import os
import pygame
import sys
import time

# All classes for Race portion of the game:
from race import GameObject
from race import PlayerView
from race import Level
from race import FinishLine
from race import PlayerCar
from race import NpcCar
from race import AiAgent
        
class Race:

    def __init__(self, game):
        self.game = game
        # Init all necc game variables from Main class
        self.screen = game.screen
        self.clock = game.clock
        self.FPS = game.FPS
        self.display = game.display
        self.screen_rect = self.screen.get_rect()      
        self.player_selection = game.player_selection
        self.level_selection = game.level_selection
        self.npc_car_images = self.game.car_images
        self.npc_car_images = [self.game.car_image_directory + image for image in self.npc_car_images] # append the image directory to each of the image filenames
        self.npc_car_images = [image for image in self.npc_car_images if image != self.player_selection] # Don't let npc's be same color as player's color choice
        self.ai_selection = game.ai_selection
               
        # Init a dictionary to store all in-game (race) objects
        self.game_objects = {}
        # Init level and get critical level data from level's init .txt file to init all additional objects
        self.level = Level.Level(self.level_selection)     
        # Init race finish line
        self.finish_line = FinishLine.FinishLine(self.level, self.game_objects, self.game)    
        # Load and init the attributes for player and NPCs (as defined in Main class)
        self.player_attributes = self.game.init_player_attributes(self.player_selection, self.level.player_start_coords)
        self.npc_attributes = self.game.init_npc_attributes(self.npc_car_images, self.level.npcs, self.level.npc_start_coords, self.level.npc_points)
        # Init the player's car object
        self.player_car = PlayerCar.PlayerCar(self.player_attributes, self.game.key_state, self.game_objects)
        # If player selected, init the player AiAgent
        if self.game.ai_selection == True:
            self.ai_agent = AiAgent.AiAgent(self.game, self.player_car, self.level, self.game_objects)   
        # Init all npc car(s)
        self.npc_cars = []
        for i in range(0, self.npc_attributes["NPCS"], 1):
            self.npc_cars.append(NpcCar.NpcCar(self.npc_attributes, self.game_objects))        
        # Update dict w/all game objects for their reference across class objects
        self.game_objects.update({"level": self.level, "finish_line": self.finish_line, "player_car": self.player_car, "npc_cars": self.npc_cars})
        if self.ai_selection == True:
            self.game_objects.update({"ai": self.ai_agent})
        # Init player collision manager for collision detection
        self.player_car.init_collision_manager()
        # Init NPC collision manager for collision detection
        for car in self.npc_cars:
            car.init_collision_manager()
        # Init the player's viewport (i.e. the "view" blitted to the screen)
        self.player = PlayerView.PlayerView(self.screen, self.game_objects)
            
        # Start the game's race loop
        self.race_loop()
    
    # Update objects - Makes obj method calls to detect each of
    # their collision status', calculate their next movements, etc.
    def update(self):    
        self.level.update()
        self.player_car.update()
        if self.ai_selection == True:
            self.ai_agent.update()
        for car in self.npc_cars:
            car.update()
        self.finish_line.update()
        self.player.update_viewport()
    
    # Makes call to player's viewport to finalize the drawing of everything to the screen
    def draw(self):
        self.player.display_viewport() # Draws map and all game objects to image buffer
        pygame.display.update()        # After all draws to image buffer, update the display
    
    # Race loop
    def race_loop(self):

        while self.game.running:         
            self.game.get_events()      # Update keyboard inputs detected by game (Main class)      
            self.update()               # Update all in-race objects
            self.draw()                 # Draw to screen
            self.clock.tick(self.FPS)   # Ensures framerate constant is maintained
            