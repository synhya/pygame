import json
import os
import pygame
from scripts.LdtkJson import LdtkJSON

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path)
    img.set_colorkey((0,0,0))
    
    return img.convert_alpha()

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

def load_ldtk():
    with open('data/world.ldtk', 'r') as file:
        data = json.loads(file.read())
        ldtk_data = LdtkJSON.from_dict(data)

        return ldtk_data
    
def resize_image(image, scale: float):
    return pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))

# 우선 x축으로만 길다고 가정
# ++ 일단 메타정보 없이가고 나중에 pivot 필요하면 변경하는걸로.
def sheet_to_images(sheet: pygame.Surface) -> list[pygame.Surface]:
    images = []
    grid_size = sheet.get_height()
    for y in range(0, sheet.get_height(), grid_size):
        for x in range(0, sheet.get_width(), grid_size):
            grid_surface = sheet.subsurface(pygame.Rect(x, y, grid_size, grid_size))
            images.append(grid_surface.subsurface(get_non_transparent_bounding_box(grid_surface)))
    
    return images

def get_non_transparent_bounding_box(surface: pygame.Surface) -> pygame.Rect:
    mask = pygame.mask.from_surface(surface)
    return mask.get_bounding_rects()[0]

# display
def draw_bordered_image(surf: pygame.Surface, image: pygame.Surface, position: tuple[int, int], border_color: tuple[int, int, int] = (255, 10, 10), border_width: int = 1):
    bounding_box = get_non_transparent_bounding_box(image)
    bounding_box.topleft = position

    pygame.draw.rect(surf, border_color, bounding_box, border_width)