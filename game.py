import pygame

from scripts.assets import Assets
from scripts.entities import PhysicsEntity
from scripts.utils import *
from scripts.tilemap import Tilemap

class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Bertha')
        pygame.display.set_icon(pygame.image.load('data/wing.png'))

        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False, False, False]

        player_idle=sheet_to_images(resize_image(load_image('entities/player.png'), 0.5))
        
        self.assets = Assets(
            player=player_idle[0],
            tileset=load_image('tilesets/cavesofgallet_tiles.png'),
            ldtk=load_ldtk()
        )

        self.base_color = pygame.Color("#171c39") 
        self.player = PhysicsEntity(self, 'player', (50, 50), (6, 8))

        self.tilemap = Tilemap(self)

    def run(self):
        while True:
            self.display.fill(self.base_color)
            
            self.tilemap.render(self.display)

            self.player.update((self.movement[1] - self.movement[0], 0))
            self.player.render(self.display)
            
            # debug
            # draw_bordered_image(self.display, self.player.game.assets.player, tuple(self.player.pos))

            print(self.tilemap.tiles_around(self.player.pos))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False 

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()