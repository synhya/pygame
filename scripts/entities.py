import random
from typing import TYPE_CHECKING
import pygame
import math
from scripts.particle import Particle

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

        self.last_movement = [0, 0]
        
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

        self.last_movement = movement
                
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
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions['bottom']:
            self.air_time = 0
            self.jumps = 1

        self.wall_slide = False # act as single frame switch
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('idle') # wall_slide

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('idle') # jump
            elif movement[0] != 0:
                self.set_action('walk')
            else:
                self.set_action('idle')

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            angle = random.random() * math.pi * 2
            speed = random.random() * 0.5 + 0.5
            pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            # self.game.particles.append(Particle(self.game, 'particle', self.rect.center, velocity=pvelocity, frame=random.randint(0, 7)))

        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(0, self.velocity[0] + 0.1, 0)

    def render(self, surf, offset):
        if abs(self.dashing) <= 50:
            super().render(surf, offset)

    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True

        elif self.jumps > 0:
            self.jumps -= 1
            self.velocity[1] = -3
            self.air_time = 5 # instant jump animation
            return True
        
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
