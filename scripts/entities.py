import random
from typing import TYPE_CHECKING
import pygame
import math
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.utils import Animation

if TYPE_CHECKING:
    from game import Game
    from scripts.LdtkTilemap import LdtkTilemap
    
class PhysicsEntity:
    def __init__(self, game: 'Game', e_type, pos, size, anim_offset = (0, 0)):
        if size is None:
            first_key = next(iter(game.assets[e_type]))
            first_value = game.assets[e_type][first_key]
            if isinstance(first_value, list):
                first_value = first_value[0]
            elif isinstance(first_value, Animation):
                first_value = first_value.img()
            size = (first_value.get_width(), first_value.get_height())

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

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size = None):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect.left - 1, self.rect.bottom + 1) if self.flip else (self.rect.right + 1, self.rect.bottom + 1)):
                if self.collisions['right'] or self.collisions['left']:
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.rect.centerx - self.rect.centerx, self.game.player.rect.centery - self.rect.centery)
                if (abs(dis[1]) < 16):
                    self.game.sfx['shoot'].play()
                    if (self.flip and dis[0] < 0):
                        self.game.projectiles.append([[self.rect.centerx - 5, self.rect.centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dis[0] > 0):
                        self.game.projectiles.append([[self.rect.centerx + 5, self.rect.centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('walk')
        else:
            self.set_action('idle')

        if abs(self.game.player.dashing) >= 50:
            if self.rect.colliderect(self.game.player.rect):
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx['hit'].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect.center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect.center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect.center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect.center, math.pi, 5 + random.random()))
                
                return True
            

    def render(self, surf: pygame.Surface, offset=(0, 0)):
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect.centerx - 5 - self.game.assets['gun'].get_width() - offset[0], self.rect.centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect.centerx + 5 - offset[0], self.rect.centery - offset[1]))

        super().render(surf, offset)
    

class Player(PhysicsEntity):
    def __init__(self, game, pos, size = None):
        super().__init__(game, 'player', pos, size, (-4, -1))
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1

        if self.air_time > 120:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1

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

        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect.center, velocity=pvelocity, frame=random.randint(0, 7)))


        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
                pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
                self.game.particles.append(Particle(self.game, 'particle', self.rect.center, velocity=pvelocity, frame=random.randint(0, 7)))

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
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
