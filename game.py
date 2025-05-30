'''Group name: CAS/DAN 05
   Group members:
    Bipana Tripathee[SID: 388875]
    Elijah cantoria[SID:358778 ]
    Sakshi Sakshi[SID:386993]
    Shreeya Regmi[SID:390356 ]'''

# These are the standards library imports.
import os
import random
import sys
import math

# Pygame library import
import pygame

# This is the process of importing custom classes from scripts folder.
from scripts.entity import PhysicsEntity
from scripts.player import Player
from scripts.enemy import Enemy
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.cloud import Clouds
from scripts.particle import Particle
from scripts.spark import Spark

# Here is the main game class.
class Game:
    def __init__(self):
        # Initializing all imported pygame modules.
        pygame.init()
        
        # Setting the window title.
        pygame.display.set_caption('Welcome To 2D Ninja Game: CAS/DAN-05 ')
        
        # I set the window size like this.
        self.screen = pygame.display.set_mode((800, 600))
        
# I create two surafaces:one with alpha support for transparency.
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))
        
# Here I initialized the clock for FPS control.
        self.clock = pygame.time.Clock()
        
        # This is the movement flags:[Left, right]
        self.movement = [False, False]

# Here I loaded all game assets(images and animations)
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'large_decor': load_images('tiles/large_decor'),
            'player': load_image('entities/player.png'),
            'background': load_image('background_night.png'),
            'clouds': load_images('clouds'),
            
            # These are Enemy animations.
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            
            # These are player animation.
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            
            # These are particle animations.
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            
            # These are items.
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png')
        }

# Loding and setting volumes for sound effects.
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        
# Initializing background clouds.
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        # Default font
        self.font = pygame.font.SysFont(None, 24)
        
# This part is the staring of game.
        self.reset_game()
        
# Resetting the game to its initial state
    def reset_game(self):
        self.lives = 5 # setting initial number of lives
        self.score = 0 # Setting initial score.
        self.level = 0  # Starting from level 0
        self.player = Player(self, (50, 50), (8, 15)) # Initializing player with position and size
        self.tilemap = Tilemap(self, tile_size=16)# Loading the tilemap with specified tile size
        self.current_level_passed = False # level is not yet completed
        self.game_over = False # This means game is not over at the start
        self.load_level(self.level) # Loading the initial level
        
# Loading a specific level from JSON map data
    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json') # Loading the map
        self.leaf_spawners = [] # Initializing list for leaf effect
        self.enemies = [] # Initializing enemy list 
        
        
# This part is setting up leaf spawners from decorative trees
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
# Setting up player and enemy spawn points.
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']  #  Setting player's starting position
                self.player.air_time = 0  # Resetting player's airtime
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15))) # spawn enemy
                
# Resetting game-related visual elements
        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30
        
        # This is the main game loop
    def run(self):
        # Play background music and ambient sound
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        self.sfx['ambience'].play(-1)

        while True:
            self.display.fill((0, 0, 0, 0))# Clearing the main display
            self.display_2.blit(self.assets['background'], (0, 0))
            self.screenshake = max(0, getattr(self, 'screenshake', 0) - 1)

#This is the Game over screen logic
            if self.game_over:
                self.display_2.fill((0, 0, 0))
                game_over_text = self.font.render("Game Over! Score: " + str(self.score), True, (255, 0, 0))
                retry_text = self.font.render("Press R to Restart", True, (255, 255, 255))
                self.display_2.blit(game_over_text, (100, 100))
                self.display_2.blit(retry_text, (100, 120))
                self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), (0, 0))
                pygame.display.update()
                
                # Checking for quit or restart.
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.reset_game()
                self.clock.tick(60)
                continue
            
            # Handling level completion and transition to next level
            if self.current_level_passed:
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level)
                    self.current_level_passed = False
            if self.transition < 0:
                self.transition += 1
                
# Handling player death and life loss
            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.load_level(self.level)
                        
# Smoothing camera following the player.
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
# This is the random leaf particle spawning
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
                    
# Updating and rendering clouds and tiles
            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)
            
#  Updating and rendering enemies
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
                    self.score += 10
                    if not len(self.enemies):
                        self.current_level_passed = True
                        
#  Updating and rendering player if alive
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)
                
#  Updating and rendering projectiles.
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                                        projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (
                            math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[
                                math.cos(angle + math.pi) * speed * 0.5,
                                math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
#  Updating and rendering sparks
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
                    
# creating silhouette for a glowing effect
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, 1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)
                
# Updating and rendering all particles                
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
                    
# This section shows Handling player input and events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_k:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_j:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
# Handling transition effect
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2,
                                                                       self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            # Displaying player stats (lives and score)
            lives_text = self.font.render(f'Lives: {self.lives}', True, (255, 255, 255))
            score_text = self.font.render(f'Score: {self.score}', True, (255, 255, 0))
            self.display_2.blit(self.display, (0, 0))
            self.display_2.blit(lives_text, (5, 5))
            self.display_2.blit(score_text, (5, 20))
            
# Applying screenshake effect
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                  random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            
            # Updating the display and maintain framerate
            pygame.display.update()
            self.clock.tick(60)

# start the game loop
Game().run()
