import json
import os
import pygame
from scripts.LdtkJson import LdtkJSON

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

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