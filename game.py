import math
import random
import pygame

from scripts.entities import Player
from scripts.utils import *
from scripts.LdtkTilemap import LdtkTilemap
from scripts.particle import Particle

class Game:
    def __init__(self):
        pygame.display.init() # pygame.init() 가끔 에러남.

        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Bertha')
        pygame.display.set_icon(pygame.image.load('data/wing.png'))

        self.display = pygame.Surface((320, 240))

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
                'idle': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Idle.png')), 10, True),
                'walk': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Run.png')), 3, True),
                'hurt': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Hit.png')), 4, False),
                'death': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Die.png')), 4, False),
                'attack': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Attack.png')), 4, False),
                'stun': Animation(sheet_to_images(load_image('entities/mushroom/Mushroom-Stun.png')), 4, False),
            },
            "particle": {
                "leaf": Animation(load_images('particles/leaf'), 20, False),
                "particle": Animation(load_images('particles/particle'), 6, False),
            },
            "tileset" : load_image('tilesets/cavesofgallet_tiles.png'),
            "ldtk" : load_ldtk()
        }

        self.base_color = pygame.Color("#171c39") 
        self.player = Player(self, (50, 50), (10, 18))

        self.tilemap = LdtkTilemap(self)

        self.leaf_spanwers = []
        self.particles = []
        # 해당 타일의 배열을 가져와서 hitbox만들자.

        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                print(spawner['pos'], 'enemy')
        
        self.scroll = [0, 0]

    def run(self):
        while True:
            self.display.fill(self.base_color)
            
            self.scroll[0] += (self.player.rect.centerx - self.display.get_width() / 2 - self.scroll[0]) / 8
            self.scroll[1] += (self.player.rect.centery - self.display.get_height() / 2 - self.scroll[1]) / 8
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.leaf_spanwers:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            self.tilemap.render(self.display, offset = render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset = render_scroll)
            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset = render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            # debug
            # draw_bordered_image(self.display, self.player.rect, render_scroll)

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
                        self.player.jump()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False 

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()