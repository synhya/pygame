import math
import random
import pygame

from scripts.entities import Enemy, Player
from scripts.spark import Spark
from scripts.utils import *
from scripts.LdtkTilemap import LdtkTilemap
from scripts.particle import Particle

class Game:
    def __init__(self):
        pygame.init() # pygame.init() 가끔 에러남.

        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Bertha')
        pygame.display.set_icon(pygame.image.load('data/wing.png'))

        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False, False, False]

        self.assets = {
            "player": {
                'idle': Animation(sheet_to_images(load_image('entities/player/Soldier-Idle.png')), 10, True),
                'walk': Animation(sheet_to_images(load_image('entities/player/Soldier-Walk.png')), 3, True),
                'hurt': Animation(sheet_to_images(load_image('entities/player/Soldier-Hurt.png')), 4, False),
                'death': Animation(sheet_to_images(load_image('entities/player/Soldier-Death.png')), 4, False),
                'attack': Animation(sheet_to_images(load_image('entities/player/Soldier-Attack01.png')), 4, False),
            },
            "enemy": {
                'idle': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Idle.png'), grid_count=7, flip=True), 10, True),
                'walk': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Run.png'), grid_count=8, flip=True), 7, True),
                'hurt': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Hit.png'), grid_count=5, flip=True), 7, False),
                'death': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Die.png'), grid_count=15, flip=True), 7, False),
                'attack': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Attack.png'), grid_count=10, flip=True), 7, False),
                'stun': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Stun.png'), grid_count=18, flip=True), 7, False),
            },
            "particle": {
                "leaf": Animation(load_images('particles/leaf'), 20, False),
                "particle": Animation(load_images('particles/particle'), 6, False),
            },
            "tileset" : load_image('tilesets/cavesofgallet_tiles.png'),
            "gun" : resize_image(load_image('gun.png'), 2),
            "projectile" : resize_image(load_image('projectile.png'), 1.5),
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        self.sfx['jump'].set_volume(0.5)
        self.sfx['dash'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.4)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['ambience'].set_volume(0.2)

        self.base_color = pygame.Color("#171c39") 
        self.player = Player(self, (50, 50), (10, 18))

        self.tilemap = LdtkTilemap(self)

        self.level = 0
        self.load_level(self.level)

        self.screenshake = 0
        
    def load_level(self, index):
        self.tilemap.load_level(index)
        self.leaf_spanwers = []

        self.enemies = []
        for identifier in self.tilemap.spawn_pos:
            if identifier == 'Player':
                spawn_pos = (self.tilemap.spawn_pos[identifier][0][0] * self.tilemap.mutiplier, self.tilemap.spawn_pos[identifier][0][1] * self.tilemap.mutiplier)
                self.player.rect.topleft = spawn_pos
                self.player.air_time = 0
            elif identifier == 'Enemy':
                for pos in self.tilemap.spawn_pos[identifier]:
                    spawn_pos = (pos[0] * self.tilemap.mutiplier, pos[1] * self.tilemap.mutiplier)
                    self.enemies.append(Enemy(self, spawn_pos))

        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    def run(self):
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.fill(self.base_color)

            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(self.tilemap.tilemap.levels) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.load_level(self.level)
            
            self.scroll[0] += (self.player.rect.centerx - self.display.get_width() / 2 - self.scroll[0]) / 8
            self.scroll[1] += (self.player.rect.centery - self.display.get_height() / 2 - self.scroll[1]) / 8
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.leaf_spanwers:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            self.tilemap.render(self.display_2, offset = render_scroll)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset = render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display_2, offset = render_scroll)

            # [(x, y), direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1] 
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check((projectile[0])):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect.collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.screenshake = max(16, self.screenshake)
                        self.sfx['shoot'].play()
                        self.player.set_action('hurt')
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect.center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect.center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset = render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                self.display_2.blit(display_sillhouette, offset) 
            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset = render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            # debug
            # draw_bordered_image(self.display, self.player.rect, render_scroll)

            # for enemy in self.enemies:
            #     draw_bordered_image(self.display, enemy.rect, render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False 

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)

            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)

Game().run()
