from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from game import Game
    from scripts.tilemap import Tilemap
    
class PhysicsEntity:
    def __init__(self, game: 'Game', e_type, pos, size, pos_offset = (0, 0)):
        self.game = game
        self.type = e_type
        self.rect = pygame.FRect(*pos, *size)
        self.pos_offset = pos_offset
        self.velocity = [0, 0]
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}

        self.action = ''
        self.anim_offset = ()
        self.flip = False
        self.set_action('idle')
        
    def pos(self):
        return (self.rect.left + self.pos_offset[0], self.rect.top + self.pos_offset[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            # self.animation = self.assets[self.e_type + '/' + self.action]

    def update(self, tilemap: 'Tilemap', movement=(0, 0)):
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.rect.left += frame_movement[0]
        for rect in tilemap.physics_rects_around(self.pos()):
            if self.rect.colliderect(rect):
                if frame_movement[0] > 0:
                    self.rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    self.rect.left = rect.right
                    self.collisions['left'] = True
        
        self.rect.top += frame_movement[1]
        for rect in tilemap.physics_rects_around(self.pos()):
            if self.rect.colliderect(rect):
                if frame_movement[1] > 0:
                    self.rect.bottom = rect.top
                    self.collisions['bottom'] = True
                if frame_movement[1] < 0:
                    self.rect.top = rect.bottom
                    self.collisions['top'] = True
                
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['bottom'] or self.collisions['top']:
            self.velocity[1] = 0

    def render(self, surf: pygame.Surface, offset):
        surf.blit(self.game.assets.player, (self.rect.left + self.pos_offset[0] - offset[0], self.rect.top + self.pos_offset[1] - offset[1]))