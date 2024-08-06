

import pygame


class Tilemap:
    def __init__(self, game, tile_size):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgird_tiles = []

    def render(self, surf: pygame.Surface, offset):
        alligned_offset = (offset[0] // self.tile_size, offset[1] // self.tile_size)

        for x in range(alligned_offset[0], surf.get_width() + alligned_offset[0] + 1, self.tile_size):
            for y in range(alligned_offset[1], surf.get_height() + alligned_offset[1] + 1, self.tile_size):
                tile_loc = str(x // self.tile_size) + ';' + str(y // self.tile_size)
                if tile_loc in self.tilemap:
                    tile = self.tilemap[tile_loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (x - offset[0], y - offset[1]))
                        