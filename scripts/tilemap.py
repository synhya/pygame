from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game

class Tilemap:
    def __init__(self, game: 'Game', tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {} 
        # self.offgrid_tiles = [{'type': 'grass', 'variant': 1, 'pos': (3 + i, 10)}]  # List of tiles that are not on the grid

        # for i in range(10):
        #     self.tilemap[str(3 + i) + ';10'] = {'type': 'grass', 'variant': 1, 'pos': (3 + i, 10)}
        #     self.tilemap['10;' + str(5 + i)] = {'type': 'stone', 'variant': 1, 'pos': (10, 5 + i)}

        self.layer = game.assets.ldtk.worlds # 이거 지금 빈배열나오는데 파싱잘못된듯.
        print(self.layer)

    def render(self, surf):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], tile['pos'])

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))