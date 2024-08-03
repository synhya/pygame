from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game import Game

NEIGHBOR_OFFSETS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
class Tilemap:
    def __init__(self, game: 'Game'):
        self.game = game
        self.level = game.assets.ldtk.levels[0]
        
        # get tile instance list
        self.layer_instances = self.level.layer_instances 
        self.layer_instances.reverse()      

        # get tileset surface list
        tile_grid_size = game.assets.ldtk.defs.tilesets[0].tile_grid_size
        self.tileset = self.load_tiles(game.assets.tileset, tile_grid_size, tile_grid_size)

    def tiles_around(self, pos):
        tiles = []
        
        for layer_index, layer_instance in enumerate(self.layer_instances):
            if layer_instance.int_grid_csv == None or len(layer_instance.int_grid_csv) == 0:
                continue
            
            tile_size = layer_instance.grid_size
            tile_loc = (int(pos[0] // tile_size), int(pos[1] // tile_size))

            for offset in NEIGHBOR_OFFSETS:
                check_loc = (tile_loc[0] + offset[0], tile_loc[1] + offset[1])
                if(check_loc[0] < 0 or check_loc[0] >= layer_instance.c_wid or check_loc[1] < 0 or check_loc[1] >= layer_instance.c_hei):
                    continue
                
                index = check_loc[1] * layer_instance.c_wid + check_loc[0]
                
                if layer_instance.int_grid_csv[index] > 0: # exists
                    tiles.append(
                        {
                            'layer_index': layer_index,
                            'tile': layer_instance.int_grid_csv[index],
                            'pos': (check_loc[0] * tile_size, check_loc[1] * tile_size)
                        }
                    )
            
        return tiles
        
    def render(self, surf: pygame.Surface):
        for layer_instance in self.layer_instances:
            tilemap = layer_instance.auto_layer_tiles 
            for tile in tilemap:
                tile_surface = pygame.transform.flip(self.tileset[tuple(tile.src)], tile.f & 1, tile.f & 2)
                tile_surface.set_alpha(int(tile.a * 255))
                surf.blit(tile_surface, tuple(tile.px))
        
    @staticmethod
    def load_tiles(tileset_image: pygame.Surface, tile_width, tile_height) -> list[pygame.Surface]:
        tiles = {}
        tileset_width, tileset_height = tileset_image.get_size()
        for y in range(0, tileset_height, tile_height):
            for x in range(0, tileset_width, tile_width):
                tiles[(x, y)] = tileset_image.subsurface(pygame.Rect(x, y, tile_width, tile_height))
        
        return tiles