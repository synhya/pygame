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
# Python에서 기본 인수로 가변 객체(예: 리스트, 딕셔너리)를 사용하면, 해당 객체는 함수가 호출될 때마다 재사용됩니다
def sheet_to_images(sheet: pygame.Surface, grid_size = None, grid_count = -1, flip = False) -> list[pygame.Surface]:
    if grid_size is None:
        grid_size = [-1, -1]

    images = []

    if grid_size[0] < 0:
        if grid_count < 0:
            grid_size[0] = sheet.get_height()
        else:
            grid_size[0] = int(sheet.get_width() / grid_count)
    
    if grid_size[1] < 0:
        grid_size[1] = sheet.get_height()

    for x in range(0, sheet.get_width(),grid_size[0]):
        for y in range(0, sheet.get_height(),  grid_size[1]):
            grid_surface = sheet.subsurface(pygame.Rect(x, y, *grid_size))
            masked_rect = get_non_transparent_bounding_box(grid_surface)

            if masked_rect.width > 0 and masked_rect.height > 0:
                if flip:
                    grid_surface = pygame.transform.flip(grid_surface, True, False)
                images.append(grid_surface.subsurface(masked_rect))
    
    return images

def get_non_transparent_bounding_box(surface: pygame.Surface) -> pygame.Rect:
    mask = pygame.mask.from_surface(surface)
    bounding_rects = mask.get_bounding_rects()
    
    if bounding_rects:
        return bounding_rects[0]
    else:
        return pygame.Rect(0, 0, 0, 0)

# display
def draw_bordered_image(surf: pygame.Surface, rect: pygame.FRect, offset: tuple[int, int] = (0, 0), border_color: tuple[int, int, int] = (255, 10, 10), border_width: int = 1):
    bounding_box = rect.copy()
    bounding_box.left -= offset[0]
    bounding_box.top -= offset[1]

    pygame.draw.rect(surf, border_color, bounding_box, border_width)

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.img_duration = img_dur
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (len(self.images) * self.img_duration)
        else:
            self.frame = min(self.frame + 1, len(self.images) * self.img_duration - 1)
            if self.frame >= len(self.images) * self.img_duration - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]