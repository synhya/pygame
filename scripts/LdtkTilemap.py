from typing import TYPE_CHECKING, Dict, List

import pygame

from scripts.LdtkJson import LayerInstance, TileInstance
from scripts.utils import load_ldtk

if TYPE_CHECKING:
    from game import Game

PHYSICS_TILES = [1]
class LdtkTilemap:
    def __init__(self, game: 'Game'):
        self.game = game
        self.tilemap = load_ldtk()

        # 스프라이트가 너무 작은 경우 타일 확대.
        self.mutiplier = 1.5

        # get tileset surface list
        tile_grid_size = self.tilemap.defs.tilesets[0].tile_grid_size
        self.tileset = self.load_tiles(game.assets["tileset"], tile_grid_size, tile_grid_size)

    def load_level(self, index):
        self.level = self.tilemap.levels[index]
        # get tile instance list
        self.layer_instances: List[LayerInstance] = list(filter(lambda x: x.type != "Entities", self.level.layer_instances))
        self.layer_instances.reverse()      

        self.entity_layer_instances: List[LayerInstance] = list(filter(lambda x: x.type == "Entities", self.level.layer_instances))
        
        for layer_instance in self.layer_instances:
            tilemap = {}
            for tile in layer_instance.auto_layer_tiles:
                tilemap[(tile.px[0], tile.px[1])] = tile
                
            layer_instance.tilemap = tilemap

        self.spawn_pos = {}
        for layer_instance in self.entity_layer_instances:
            for entity in layer_instance.entity_instances:
                identifier = entity.identifier
                position = entity.px
                
                if identifier in self.spawn_pos:
                    # 이미 해당 identifier가 존재하면 리스트에 추가
                    self.spawn_pos[identifier].append(position)
                else:
                    # 존재하지 않으면 새로운 리스트로 저장
                    self.spawn_pos[identifier] = [position]

    def tiles_around(self, pos):
        tiles = []
        
        for layer_index, layer_instance in enumerate(self.layer_instances):
            if layer_instance.int_grid_csv == None or len(layer_instance.int_grid_csv) == 0:
                continue
            
            tile_size = layer_instance.grid_size * self.mutiplier
            tile_loc = (int(pos[0] // tile_size), int(pos[1] // tile_size))

            for x in range(-2, 3):
                for y in range(-2, 3):
                    offset = (x, y)
                    check_loc = (tile_loc[0] + offset[0], tile_loc[1] + offset[1])
                    if(check_loc[0] < 0 or check_loc[0] >= layer_instance.c_wid or check_loc[1] < 0 or check_loc[1] >= layer_instance.c_hei):
                        continue
                    
                    index = check_loc[1] * layer_instance.c_wid + check_loc[0]
                    
                    if layer_instance.int_grid_csv[index] > 0: # exists
                        tiles.append(
                            {
                                'layer_index': layer_index,
                                'value': layer_instance.int_grid_csv[index],
                                'pos': (check_loc[0] * tile_size, check_loc[1] * tile_size)
                            }
                        )
        return tiles
    
    def solid_check(self, pos):
        for layer_instance in self.layer_instances:
            if layer_instance.int_grid_csv == None or len(layer_instance.int_grid_csv) == 0:
                continue

            tile_size = layer_instance.grid_size * self.mutiplier
            tile_loc = (int(pos[0] // tile_size), int(pos[1] // tile_size))

            index = tile_loc[1] * layer_instance.c_wid + tile_loc[0]

            if layer_instance.int_grid_csv[index] in PHYSICS_TILES: # walls
                return layer_instance.tilemap[(tile_loc[0] * layer_instance.grid_size, tile_loc[1] * layer_instance.grid_size)]

    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['value'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'], (int(self.layer_instances[tile['layer_index']].grid_size * self.mutiplier), int(self.layer_instances[tile['layer_index']].grid_size * self.mutiplier))))
        
        return rects
        
    def render(self, surf: pygame.Surface, offset):
        for layer_instance in self.layer_instances:
            tile_size = int(layer_instance.grid_size * self.mutiplier)

            alligned_offset = ((offset[0] // tile_size) * tile_size, (offset[1] // tile_size) * tile_size)
            
            for _x in range(alligned_offset[0], alligned_offset[0] + surf.get_width() + tile_size, tile_size):
                for _y in range(alligned_offset[1], alligned_offset[1] + surf.get_height() + tile_size, tile_size):
                    x = int(_x / self.mutiplier)
                    y = int(_y / self.mutiplier)
                    if (x, y) in layer_instance.tilemap:
                        tile = layer_instance.tilemap[(x, y)]
                        tile_surface = pygame.transform.flip(self.tileset[tuple(tile.src)], tile.f & 1, tile.f & 2)
                        tile_surface.set_alpha(int(tile.a * 255))
                        tile_surface = pygame.transform.scale(tile_surface, (int(tile_size), int(tile_size)))
                        surf.blit(tile_surface, (tile.px[0] * self.mutiplier - offset[0], tile.px[1] * self.mutiplier - offset[1]))

            # tilemap = layer_instance.auto_layer_tiles 

            # for tile in tilemap:
            #     tile_surface = pygame.transform.flip(self.tileset[tuple(tile.src)], tile.f & 1, tile.f & 2)
            #     tile_surface.set_alpha(int(tile.a * 255))
            #     render_pos = (tile.px[0] - offset[0] * depth, tile.px[1] - offset[1] * depth)
            #     surf.blit(tile_surface, render_pos)
        
    @staticmethod
    def load_tiles(tileset_image: pygame.Surface, tile_width, tile_height) -> list[pygame.Surface]:
        tiles = {}
        tileset_width, tileset_height = tileset_image.get_size()
        for y in range(0, tileset_height, tile_height):
            for x in range(0, tileset_width, tile_width):
                tiles[(x, y)] = tileset_image.subsurface(pygame.Rect(x, y, tile_width, tile_height))
        
        return tiles