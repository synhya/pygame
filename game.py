import pygame

from scripts.entities import Player
from scripts.utils import *
from scripts.LdtkTilemap import LdtkTilemap

class Game:
    def __init__(self):
        pygame.init()

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
            "tileset" : load_image('tilesets/cavesofgallet_tiles.png'),
            "ldtk" : load_ldtk()
        }

        self.base_color = pygame.Color("#171c39") 
        self.player = Player(self, (50, 50), (10, 18))

        self.tilemap = LdtkTilemap(self)
        
        self.scroll = [0, 0]

    def run(self):
        while True:
            self.display.fill(self.base_color)
            
            self.scroll[0] += (self.player.rect.centerx - self.display.get_width() / 2 - self.scroll[0]) / 8
            self.scroll[1] += (self.player.rect.centery - self.display.get_height() / 2 - self.scroll[1]) / 8
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.tilemap.render(self.display, offset = render_scroll)

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset = render_scroll)
            
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
                        self.player.velocity[1] = -2
                    
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False 

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()