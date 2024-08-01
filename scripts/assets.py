from dataclasses import dataclass
import pygame

from scripts.LdtkJson import LdtkJSON

@dataclass
class Assets:
    player: pygame.Surface
    ldtk: LdtkJSON