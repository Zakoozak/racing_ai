import pygame
import math

# The AiRadar class inits a radar object used to detect distances at multiple angles from the player
# to the level's collision boundary.  Ultimately, these distance values are used as the primary inputs (along
# with the players speed) to the agents DQN ie. its deep nueral net.  The simulated radar beams are also
# drawn to screen as a visual aid.
class AiRadar():
    def __init__(self, player_car, level):
        self.player = player_car
        self.level = level
        self.level_width = level.image.get_width()
        self.level_height = level.image.get_height()
        self.level_mask = level.mask
        # Init flipped level masks for radar beams & store in list--needed for calc_radar_beams function (AI collision detection)
        mask = level.mask
        mask_flipped_x = pygame.mask.from_threshold(pygame.transform.flip(level.image, True, False), pygame.Color(level.level_boundary_color), (1,1,1,1))
        mask_flipped_y = pygame.mask.from_threshold(pygame.transform.flip(level.image, False, True), pygame.Color(level.level_boundary_color), (1,1,1,1))
        mask_flipped_xy = pygame.mask.from_threshold(pygame.transform.flip(level.image, True, True), pygame.Color(level.level_boundary_color), (1,1,1,1))
        self.level_masks = [[mask, mask_flipped_y], [mask_flipped_x, mask_flipped_xy]]
        # Init radar beam surface. 
        self.radar_length = 500
        self.radar_max_length = math.sqrt( (self.radar_length**2 + self.radar_length**2) )
        self.beam_surface = pygame.Surface((self.radar_length, self.radar_length))
        # Init list to store each radar collision detecting beam coords - used to draw beams to screen
        self.radar_beams = []
        # Init list to store each radar beams total distance - used as nueral nets' inputs for collision detection
        self.radar_beam_distances = []
        
    # Function which creates simulated 'radar beams' to determine distance from player
    # to level boundaries.  Calculates the distance of each beam, which are used as the
    # input to the DQN algorithm.  Beams are also drawn to screen for human visualization.
    def calc_radar_beams(self):
        # Clear radar lists for each iteration
        self.radar_beams = []
        self.radar_beam_distances = []
        # Get the current x,y coords of the center of the player  
        pos = (self.player.rect.x + .5 * self.player.rect.width, self.player.rect.y + .5 * self.player.rect.height)
        # Get player's current heading angle and create a list of angles in 30 degrees increments in both directions from that heading, covering 360°
        angles_right = []
        angles_left = []
        for i in range(int(self.player.angle), int(self.player.angle + 90), 30):
            angles_right.append(i)
        for i in range(int(self.player.angle) - 30, int(self.player.angle  - 90), -30):
            angles_left.append(i)
        # Zip both lists into single list
        angles = []
        for i in range(0, len(angles_right) + len(angles_left), 1):
            if angles_right:
                angles.append(angles_right.pop(0))
            if angles_left:
                angles.append(angles_left.pop(0))

        # Calc the coords needed to create a collision-sensor/radar beam at every angle 
        for angle in angles:
            c = math.cos(math.radians(angle))
            s = math.sin(math.radians(angle))
            # Indexing Booleans based on each angle's sign--if cos is less than 0 flip_x is True and if sin is less than 0 flip_y is True
            flip_x = c < 0
            flip_y = s < 0
            # Retreive the correct level mask based on the determined cos & sin signs
            level_mask = self.level_masks[flip_x][flip_y]
            # Calculate max possible beam length position x,y without any collision & draw to (invisible) beam surface
            x_max = self.level_width * abs(c)
            y_max = self.level_height * abs(s)
            self.beam_surface.fill((0,0,0,0))
            pygame.draw.line(self.beam_surface, (255,255,255), (0,0), (x_max, y_max))
            # Create beam mask
            #beam_mask = pygame.mask.from_surface(self.beam_surface)
            beam_mask = pygame.mask.from_threshold(self.beam_surface, pygame.Color(255,255,255), (1,1,1,1))
            # Find overlap between the level's mask (level boundary) and the current beam mask, based on level mask
            offset_x = self.level_width - pos[0] if flip_x else pos[0]
            offset_y = self.level_height - pos[1] if flip_y else pos[1]
            # Determine if there's an overlap (collision) between the radar beam and the level mask (i.e. its boundary)
            hit = level_mask.overlap(beam_mask, (int(offset_x), int(offset_y)))
            # If there is a collision detected for this beam, calculate x,y coords of where the beam collides with level boundary
            if hit is not None and (hit[0] != pos[0] or hit[1] != pos[1]):
                hit_x = self.level_width - hit[0] if flip_x else hit[0]
                hit_y = self.level_height - hit[1] if flip_y else hit[1]
                hit_pos = (hit_x, hit_y)
                #Store each beam starting coords, collision coords, and total distance in a dict
                beam = {"start_coords": pos, "collision_coords": hit_pos}
                # Add beam dictionary to radar_beams list used to draw radar beams to screen
                self.radar_beams.append(beam)
                # Calculate total length of each beam: d = √[(x2- x1)2 + (y2- y1)2]
                d = math.sqrt( (hit_pos[0] - pos[0])**2 + (hit_pos[1] - pos[1])**2)
                self.radar_beam_distances.append(d)
            else:   # If there is no collision for this beam angle, then store the max beam length for this beam
                self.radar_beams.append(None)
                self.radar_beam_distances.append(int(math.hypot(self.radar_length, self.radar_length)))
        #print("Distances:",self.radar_beam_distances)
        return self.radar_beam_distances