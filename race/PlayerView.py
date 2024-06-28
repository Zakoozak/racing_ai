import pygame

from race import GameObject

# Player class creates a 'viewport' (camera) for the player.  Recieves map and game object data
# and draws everything to the viewport surface, before the final output is drawn to screen. 
class PlayerView:
    # Initializes the player's viewport
    def __init__(self, screen, game_objects):
        self.screen = screen
        self.screen_rect = self.screen.get_rect()
        self.screen_width = self.screen_rect[2]
        self.screen_height = self.screen_rect[3]
        self.game_objects = game_objects
        self.level = game_objects["level"]
        self.finish_line = game_objects["finish_line"]
        self.player = game_objects["player_car"]
        self.ai = None
        if "ai" in game_objects:
            self.ai = game_objects["ai"]
        self.player_rect = self.player.rect
        self.npc_cars = game_objects["npc_cars"]
        
        self.level_image = self.level.image # racetrack image
        self.player_image = self.player.image
        # Create the viewport    
        self.viewport = pygame.Surface((self.screen_width, self.screen_height))
 
    # Updates any needed in-game object info and viewport coords
    def update_viewport(self):
        # Offset calculation -- calculates center of where the viewport (player's view) needs to be,
        # based on initial screen size and the player's sprite image size
        self.player_offset_x = (self.screen_width / 2) - (self.player.rect[2] / 2)
        self.player_offset_y = (self.screen_height / 2) - (self.player.rect[3] / 2)
        # Second offset calculation for the ai radar-- calculates the starting point of the radar beams ie.
        # The center point of the player_car rect for the x & y
        self.radar_offset_x = self.player_offset_x + .5 * self.player.rect.width
        self.radar_offset_y = self.player_offset_y + .5 * self.player.rect.height
        
        self.viewport.fill((255,255,255)) # Fill background of viewport white
        # Updates viewport coords 
        #(-1 moves viewport in equal and opposite movement of player)
        self.x = -1 * self.player.rect.x
        self.y = -1 * self.player.rect.y
        # Account for the offset
        self.x = self.x + self.player_offset_x
        self.y = self.y + self.player_offset_y
        
    # Constructs the player's viewport by appending map and all game objects to correct surfaces
    # (updates image buffer)
    def display_viewport(self):
        self.viewport.blit(self.level_image, (self.x, self.y))                              # draw the level image to viewport
        self.level_image.blit(self.finish_line.finish_line, self.finish_line.coords)        # draw the finsih line to the level image
        self.viewport.blit(self.player.image, (self.player_offset_x, self.player_offset_y)) # draw car to center of viewport
        if self.ai != None:
            for beam in self.ai.radar.radar_beams:
                if beam == None:
                    continue
                x1 = beam["start_coords"][0]
                y1 = beam["start_coords"][1]
                x2 = beam["collision_coords"][0]
                y2 = beam["collision_coords"][1]
                pygame.draw.line(self.viewport, (155,0,155), (self.x + x1, self.y + y1), (self.x + x2, self.y + y2), width=2)
                pygame.draw.circle(self.viewport, (0,255,0), (self.x + x2, self.y + y2), 4)
        for self.npc in self.npc_cars:
            self.viewport.blit(self.npc.image, (self.x + self.npc.x, self.y + self.npc.y))         # draw all NPC's
        
        # If race win condition is met, display win condition text to viewport
        if self.finish_line.race_end == True:
            for text in self.finish_line.race_end_prompt:
                self.viewport.blit(text[0], text[1])
        
        self.screen.blit(self.viewport, (0, 0)) # draw the viewport to screen
        

