import pygame

import main

# Finish line class creates a "finish line" object and keeps track
# of the laps of the race, as to know when a "win/lose" condtion is met.
class FinishLine:

    def __init__(self, level, game_objects, game):
        # Extract coordinates
        self.coords = level.finish_line_coords
        # Extract No. of laps for Level
        self.laps = level.laps
        # Create reference to all game objects
        self.game_objects = game_objects
        # Running variables
        self.game = game

        # Init vars to create finish line surface
        x = self.coords[0]
        y = self.coords[1]
        w = self.coords [2]
        h = self.coords[3]
        font_size = self.coords[4]
        color = self.coords[5]

        # Create the finish line surface
        fl = pygame.Surface((w,h))
        
        # Color
        fl.fill(color)        
        
        # Finish line text
        fl_font = pygame.font.SysFont("comicsansms", font_size, bold=True)
        fl_text = fl_font.render("F I N I S H", True, (0,0,0)) # Black Color Text
        # Center Finish Line Text to Finish Line Surface
        fl_text_rect = fl_text.get_rect()
        text_x = (w - fl_text_rect.w) // 2
        text_y = (h - fl_text_rect.h) // 2
        # Append finish line text to finish line surface
        fl.blit(fl_text, (text_x, text_y))
        
        # Init vars to be used by PlayerView Class to draw the finish line
        self.finish_line = fl
        self.coords = (x,y)
        
        # Split the bottom half and top half of Finish Line Surface
        # and create seperate rects for collisioning and lap incremeneting
        self.top = pygame.Rect(x, y, w, h * .5)
        self.bottom = pygame.Rect(x, y + h * .5, w, h * .5)
        # Init empty lists to track car rects and collision booleans
        self.cars = []          # Car objects
        self.car_rects = []     # Car object rectangles
        self.collisions = []    # Collision boolean list for every car object        
        # Init race results list --appends a car game object once it finishes a race
        self.race_results = []
        self.race_end = False
        self.race_end_text_time = 7000 # Amount of time (ms) to display text to screen when race ends

     # Detects collisions with in-game objects and increments lap count for players   
    def update(self):
        # Update car rects list on every iteration, to get new coords of every car rect
        if self.collisions:
            self.car_rects.append(self.game_objects["player_car"].rect)
            for car in self.game_objects["npc_cars"]:
                self.car_rects.append(car.rect)
        # If this is the first call to update, init collisions and car object lists
        else:
            self.car_rects.append(self.game_objects["player_car"].rect)
            self.collisions.append([False, False])
            self.cars.append(self.game_objects["player_car"])
            for car in self.game_objects["npc_cars"]:
                self.car_rects.append(car.rect)
                self.collisions.append([False, False])
                self.cars.append(car)

        # For every car, detects collision with both (top and bottom) sides of the finish line
        # The "bottom" and "top" collision list variables will then get the list index of the
        # car rect element stored in the self.cars list corresponding to the in-game car colliding
        bottom_collisions = pygame.Rect.collidelistall(self.bottom, self.car_rects)
        top_collisions = pygame.Rect.collidelistall(self.top, self.car_rects)
        
        # For each collision detected with the lower half of the finish line
        for i in bottom_collisions:
            # If Car is ONLY in bottom half of finish line
            if i not in top_collisions:
                self.collisions[i][0] = True # set bottom collision to True
                self.collisions[i][1] = False # set top collision to False
            # Player has continued to move backwards over finish line, decrement car's lap count
            elif self.collisions[i][1] == True:
                self.cars[i].lap_count -= 1
                self.collisions[i][1] = False
        
        # For each collision detected with the upper half of the finish line
        for i in top_collisions:
            if i not in bottom_collisions:
                self.collisions[i][1] = True # Set Top to True
            # Player has continued over the finish line, increment car's lap count   
            elif self.collisions[i][0] == True:
                self.cars[i].lap_count += 1
                self.collisions[i][0] = False
              

                ####################### CHECK RACE WIN CONDITION #######################
                # If a car reaches race's lap count, update the race results list
                if self.cars[i].lap_count > self.laps and i not in self.race_results:
                    self.race_results.append(i)
                    font = pygame.font.SysFont("comicsansms", 90)
                    finish = font.render("Race Over.", True, (0,0,155))
                    finish_rect = finish.get_rect()
                    finish_rect.center = (self.game.WIDTH // 2, int(self.game.HEIGHT * .4)) # center text
                    finish_obj = (finish, finish_rect)
                    # The player has finished first, generate first place text to blit on screen
                    if i == 0 and len(self.race_results) == 1:
                        font = pygame.font.SysFont("comicsansms", 90)
                        place = font.render("Congrats, You Won!!", True, (0,0,155)) # Game's title 
                        place_rect = place.get_rect()
                        place_rect.center = (self.game.WIDTH // 2, int(self.game.HEIGHT * .5)) # center title text
                        place_obj = (place, place_rect)
                        self.race_end_prompt = [finish_obj, place_obj]
                        self.race_end = True
                        self.race_end_timer = 0
                    # Player finish race other than first place, generate corresponding text to blit on screen
                    elif i == 0:
                        font = pygame.font.SysFont("comicsansms", 90)
                        place = font.render("You Came In Place " + str(len(self.race_results)) + "!", True, (0,0,155)) # Game's title 
                        place_rect = place.get_rect()
                        place_rect.center = (self.game.WIDTH // 2, int(self.game.HEIGHT * .5)) # center title text
                        place_obj = (place, place_rect)
                        self.race_end_prompt = [finish_obj, place_obj]
                        self.race_end = True
                        self.race_end_timer = 0
        # Race is over, stop player car and increment race end timer to display text for short while
        if self.race_end:
            self.game.key_state["e_brake"] = True
            self.game.key_state["forward"] = False
            self.race_end_timer += self.game.clock.get_time()    # Increment timer to keep race end text on screen
            if self.race_end_timer > self.race_end_text_time:
                self.game.running = False                        # End the current Game
                main.Main()                                      # Restart--go to title screen
        
        # Empty car rect list for the next iteration
        self.car_rects = []

        
        