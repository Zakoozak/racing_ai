import pygame

# This class manages the game's title screen and player selections.
class Title():

    def __init__(self, game):
    
        self.game = game
        # Init all necc game variables from Main class
        self.car_image_directory = game.car_image_directory
        self.player_car_images = game.car_images
        self.level_image_directory = game.level_image_directory
        self.level_images = game.level_images
        self.name = game.name
        self.WIDTH = game.WIDTH
        self.HEIGHT = game.HEIGHT
        self.background_color = game.background_color
        self.screen = game.screen
        self.FPS = game.FPS
        self.display = game.display
        self.screen_rect = self.screen.get_rect()
        
        # Vars for player key inputs
        self.left = 0
        self.right = 0
        self.enter = 0
        
        self.title_running = True
        # Init the title screen
        self.title_screen()
                
    def draw(self, objects):
        self.screen.fill(self.background_color)
        for each in objects:
            self.screen.blit(each[0],each[1])
        pygame.display.update()
    
    # Title screen sequence
    def title_screen(self):
        # create title screen text
        font = pygame.font.SysFont("comicsansms", 90)
        title = font.render(self.name, True, (0,0,155)) # Game's title 
        title_rect = title.get_rect()
        title_rect.center = (self.WIDTH // 2, self.HEIGHT // 2) # center title text
        title_obj = (title, title_rect)
        font = pygame.font.SysFont("arial", 22, bold=True)
        prompt = font.render("Press Enter to Start (Esc to quit)", True, (0,0,0))
        prompt_rect = prompt.get_rect()
        prompt_rect.center = (self.WIDTH // 2, self.HEIGHT * .95)
        prompt_obj = (prompt, prompt_rect)
        self.draw_objects = [title_obj, prompt_obj]
    
        # Title screen loop and logic
        while self.game.running and self.title_running:
            self.game.get_events()
            if self.game.key_state["enter"] == True:
                self.enter = 1
            if self.game.key_state["enter"] == False and self.enter == 1:
                self.enter = 0
                self.car_select()
            self.draw(self.draw_objects)
            self.game.clock.tick(self.FPS)
    
    # Player car selection sequence
    def car_select(self):
        image_index = 0
        
        font = pygame.font.SysFont("arial", 32, bold=True)
        prompt1 = font.render("Please select your race car", True, (0,0,0))
        prompt1_rect = prompt1.get_rect()
        prompt1_rect.center = (self.WIDTH // 2, self.HEIGHT * .9)
        prompt1_obj = (prompt1, prompt1_rect)
        prompt2 = font.render("(use < > arrow and Enter keys, SPACE to restart.)", True, (0,0,0))
        prompt2_rect = prompt2.get_rect()
        prompt2_rect.center = (self.WIDTH // 2, self.HEIGHT * .95)
        prompt2_obj = (prompt2, prompt2_rect)
        
        self.draw_objects = [prompt1_obj, prompt2_obj]
        
        while self.game.running and self.title_running:
            car_filename = self.car_image_directory + self.player_car_images[image_index]
            image = pygame.image.load(car_filename)
            image.set_colorkey("white")
            image.convert_alpha()
            center = (self.WIDTH // 2, self.HEIGHT // 2)
            car_obj = (image, center)
            self.draw_objects.append(car_obj)

            self.game.get_events()
            if self.game.key_state["right"] == True:
                self.right = 1
            if self.game.key_state["right"] == False and self.right == 1:
                self.draw_objects.pop()
                image_index += 1
                self.right = 0
                if image_index >= len(self.player_car_images):
                    image_index = 0
            if self.game.key_state["left"] == True:
                self.left = 1
            if self.game.key_state["left"] == False and self.left == 1:
                self.draw_objects.pop()
                image_index -= 1
                self.left = 0
                if image_index < 0:
                    image_index = len(self.player_car_images) - 1
            if self.game.key_state["forward"] == True:
                self.title_screen()
            if self.game.key_state["enter"] == True:
                self.enter = 1
            if self.game.key_state["enter"] == False and self.enter == 1:
                self.enter = 0
                self.game.player_selection = car_filename # Sets the player's car choice for the game
                self.ai_select()
                
            self.draw(self.draw_objects)
            self.game.clock.tick(self.FPS)
    
    def ai_select(self):
        font = pygame.font.SysFont("arial", 32, bold=True)
        prompt1 = font.render("Initialize Artificial Intelligence Agent?", True, (0,0,0))
        prompt1_rect = prompt1.get_rect()
        prompt1_rect.center = (self.WIDTH // 2, self.HEIGHT * .8)
        prompt1_obj = (prompt1, prompt1_rect)
        prompt2 = font.render("'YES' for AI Agent control over player or 'NO' for a human-controlled game.", True, (0,0,0))
        prompt2_rect = prompt2.get_rect()
        prompt2_rect.center = (self.WIDTH // 2, self.HEIGHT * .85)
        prompt2_obj = (prompt2, prompt2_rect)
        prompt3 = font.render("Do you want to train the Deep Q-Learning Network (DQN)?", True, (0,0,0))
        prompt3_rect = prompt3.get_rect()
        prompt3_rect.center = (self.WIDTH // 2, self.HEIGHT * .8)
        prompt3_obj = (prompt3, prompt3_rect)
        prompt4 = font.render("'YES' to train the AI or 'NO' to control player from DQN only.", True, (0,0,0))
        prompt4_rect = prompt4.get_rect()
        prompt4_rect.center = (self.WIDTH // 2, self.HEIGHT * .85)
        prompt4_obj = (prompt4, prompt4_rect)
        prompt5 = font.render("(use < > arrow and Enter keys, SPACE to restart.)", True, (0,0,0))
        prompt5_rect = prompt5.get_rect()
        prompt5_rect.center = (self.WIDTH // 2, self.HEIGHT * .9)
        prompt5_obj = (prompt5, prompt5_rect)
        ans1 = font.render("NO", True, (0,0,0))
        ans1_rect = ans1.get_rect()
        ans1_rect.center = (self.WIDTH // 2, self.HEIGHT * .95)
        ans1_obj = (ans1, ans1_rect)
        ans2 = font.render("YES", True, (0,0,0))
        ans2_rect = ans2.get_rect()
        ans2_rect.center = (self.WIDTH // 2, self.HEIGHT * .95)
        ans2_obj = (ans2, ans2_rect)
        
        no_ai = [prompt1_obj, prompt2_obj, prompt5_obj, ans1_obj]
        yes_ai = [prompt1_obj, prompt2_obj, prompt5_obj, ans2_obj]
        no_train = [prompt3_obj, prompt4_obj, prompt5_obj, ans1_obj]
        yes_train = [prompt3_obj, prompt4_obj, prompt5_obj, ans2_obj]
        
        self.draw_objects = no_ai
        selected = False
        ai_selection = False
        ai_train = False
        while self.game.running and self.title_running:
            self.game.get_events()
            
            if selected == False:
                if self.game.key_state["right"] == True:
                    self.right = 1
                if self.game.key_state["right"] == False and self.right == 1 and ai_selection == False:
                    ai_selection = True
                    self.draw_objects = yes_ai
                    self.right = 0
                elif self.game.key_state["right"] == False and self.right == 1 and ai_selection == True:
                    ai_selection = False
                    self.draw_objects = no_ai
                    self.right = 0
                if self.game.key_state["left"] == True:
                    self.left = 1
                if self.game.key_state["left"] == False and self.left == 1 and ai_selection == False:
                    ai_selection = True
                    self.draw_objects = yes_ai
                    self.left = 0
                elif self.game.key_state["left"] == False and self.left == 1 and ai_selection == True:
                    ai_selection = False
                    self.draw_objects = no_ai
                    self.left = 0           
                if self.game.key_state["enter"] == True:
                    self.enter = 1
                if self.game.key_state["forward"] == True:
                    self.title_screen()
                if self.game.key_state["enter"] == False and self.enter == 1:
                    self.enter = 0
                    selected = True
                    self.game.ai_selection = ai_selection
                    self.draw_objects = no_train
                    if self.game.ai_selection == False:
                        self.game.ai_train = False
                        self.level_select()     # No AI was selected (human-play)
            else:                               # Selected is True, now select to train AI or not
                if self.game.key_state["right"] == True:
                        self.right = 1
                if self.game.key_state["right"] == False and self.right == 1 and ai_train == False:
                    ai_train = True
                    self.draw_objects = yes_train
                    self.right = 0
                elif self.game.key_state["right"] == False and self.right == 1 and ai_train == True:
                    ai_train = False
                    self.draw_objects = no_train
                    self.right = 0
                if self.game.key_state["left"] == True:
                    self.left = 1
                if self.game.key_state["left"] == False and self.left == 1 and ai_train == False:
                    ai_train = True
                    self.draw_objects = yes_train
                    self.left = 0
                elif self.game.key_state["left"] == False and self.left == 1 and ai_train == True:
                    ai_train = False
                    self.draw_objects = no_train
                    self.left = 0           
                if self.game.key_state["enter"] == True:
                    self.enter = 1
                if self.game.key_state["forward"] == True:
                    self.title_screen()
                if self.game.key_state["enter"] == False and self.enter == 1:
                    self.enter = 0
                    self.game.ai_train = ai_train
                    self.level_select()
      
            self.draw(self.draw_objects)
            self.game.clock.tick(self.FPS)
    
    def level_select(self):
        image_index = 0
        
        font = pygame.font.SysFont("arial", 32, bold=True)
        prompt1 = font.render("Please select the level", True, (0,0,0))
        prompt1_rect = prompt1.get_rect()
        prompt1_rect.center = (self.WIDTH // 2, self.HEIGHT * .9)
        prompt1_obj = (prompt1, prompt1_rect) 
        prompt2 = font.render("(use < > arrow and Enter keys, SPACE to restart.)", True, (0,0,0))
        prompt2_rect = prompt2.get_rect()
        prompt2_rect.center = (self.WIDTH // 2, self.HEIGHT * .95)
        prompt2_obj = (prompt2, prompt2_rect)
        self.draw_objects = [prompt1_obj, prompt2_obj]
        
        images = []
        # Load all level images, resize them, and add to a list which can then be cycled through
        for level in self.level_images:
            image = pygame.image.load(self.level_image_directory + level)
            image = pygame.transform.scale(image, (int(self.WIDTH * .75), int(self.HEIGHT * .75)))    # resize
            image_rect = image.get_rect()
            location = ((self.WIDTH - image_rect[2]) // 2, (self.HEIGHT - image_rect[3]) // 2)
            images.append((image, location))
            
        self.draw_objects.append(images[0])
        self.draw(self.draw_objects) # draw first level images in list
        
        while self.game.running and self.title_running:
            
            level_filename = self.level_image_directory + self.level_images[image_index] # current level image filename
            
            self.game.get_events()
            if self.game.key_state["right"] == True:
                self.right = 1
            if self.game.key_state["right"] == False and self.right == 1:
                self.draw_objects.pop()
                image_index += 1
                self.right = 0
                if image_index >= len(self.level_images):
                    image_index = 0
                self.draw_objects.append(images[image_index])
                self.draw(self.draw_objects)
            if self.game.key_state["left"] == True:
                self.left = 1
            if self.game.key_state["left"] == False and self.left == 1:
                self.draw_objects.pop()
                image_index -= 1
                self.left = 0
                if image_index < 0:
                    image_index = len(self.level_images) - 1
                self.draw_objects.append(images[image_index])
                self.draw(self.draw_objects)
            if self.game.key_state["enter"] == True:
                self.enter = 1
            if self.game.key_state["forward"] == True:
                self.title_screen()
            if self.game.key_state["enter"] == False and self.enter == 1:
                self.enter = 0
                self.game.level_selection = level_filename # Sets the player's car choice for the game
                self.title_running = False
                
            self.game.clock.tick(self.FPS)
            
            
    
    
    
    