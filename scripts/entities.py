from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from game import Game
    from scripts.LdtkTilemap import LdtkTilemap
    
class PhysicsEntity:
    def __init__(self, game: 'Game', e_type, pos, size, anim_offset = (0, 0)):
        self.game = game
        self.type = e_type
        self.rect = pygame.FRect(*pos, *size)
        self.velocity = [0, 0]
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}

        self.action = ''
        self.anim_offset = anim_offset
        self.flip = False
        self.set_action('idle')
        
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type][action].copy()


    def update(self, tilemap: 'LdtkTilemap', movement=(0, 0)):
        self.collisions = {'top': False, 'bottom': False, 'left': False, 'right': False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.rect.left += frame_movement[0]
        for rect in tilemap.physics_rects_around(self.rect.center):
            if self.rect.colliderect(rect):
                if frame_movement[0] > 0:
                    self.rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    self.rect.left = rect.right
                    self.collisions['left'] = True
        
        self.rect.top += frame_movement[1]
        for rect in tilemap.physics_rects_around(self.rect.center):
            if self.rect.colliderect(rect):
                if frame_movement[1] > 0:
                    self.rect.bottom = rect.top
                    self.collisions['bottom'] = True
                if frame_movement[1] < 0:
                    self.rect.top = rect.bottom
                    self.collisions['top'] = True

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
                
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['bottom'] or self.collisions['top']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf: pygame.Surface, offset):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.rect.left + (0 if self.flip else self.anim_offset[0]) - offset[0], self.rect.top + self.anim_offset[1] - offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size, (-4, -1))
        self.air_time = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions['bottom']:
            self.air_time = 0

        if self.air_time > 4:
            self.set_action('idle') # jump
        elif movement[0] != 0:
            self.set_action('walk')
        else:
            self.set_action('idle')