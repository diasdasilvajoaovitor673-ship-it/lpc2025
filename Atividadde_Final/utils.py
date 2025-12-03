import math
import os
from random import random, uniform
from typing import Iterable, Tuple
from PIL import Image
import pygame as pg
import config as C

Vec = pg.math.Vector2


def wrap_pos(pos: Vec) -> Vec:
    return Vec(pos.x % C.WIDTH, pos.y % C.HEIGHT)


def angle_to_vec(deg: float) -> Vec:
    rad = math.radians(deg)
    return Vec(math.cos(rad), math.sin(rad))


def rand_unit_vec() -> Vec:
    a = uniform(0, math.tau)
    return Vec(math.cos(a), math.sin(a))


def rand_edge_pos() -> Vec:
    if random() < 0.5:
        x = uniform(0, C.WIDTH)
        y = 0 if random() < 0.5 else C.HEIGHT
    else:
        x = 0 if random() < 0.5 else C.WIDTH
        y = uniform(0, C.HEIGHT)
    return Vec(x, y)


def load_image(path, size, color):
    try:
        img = pg.image.load(path).convert_alpha()
        img = pg.transform.scale(img, size)
        return img
    except (FileNotFoundError, pg.error):
        surf = pg.Surface(size)
        surf.fill(color)
        return surf


def load_gif_frames(path, size, color_fallback=(255, 0, 0)):
    frames = []
    duration = 0.1
    
    try:
        pil_img = Image.open(path)
        duration = pil_img.info.get('duration', 100) / 1000.0
        
        while True:
            frame = pil_img.convert("RGBA")
            mode = frame.mode
            s = frame.size
            data = frame.tobytes()
            py_img = pg.image.frombytes(data, s, mode)
            py_img = pg.transform.scale(py_img, size)
            frames.append(py_img)
            
            pil_img.seek(pil_img.tell() + 1)
            
    except (EOFError, FileNotFoundError, Exception) as e:
        if not frames:
            surf1 = pg.Surface(size)
            surf1.fill(color_fallback)
            surf2 = pg.Surface(size)
            surf2.fill((255, 255, 255)) 
            frames = [surf1, surf2]
            
    return frames, duration


def draw_poly(surface: pg.Surface, pts: Iterable[Tuple[int, int]]):
    pg.draw.polygon(surface, C.WHITE, list(pts), width=1)


def draw_circle(surface: pg.Surface, pos: Vec, r: int):
    pg.draw.circle(surface, C.WHITE, pos, r, width=1)


def text(surface: pg.Surface, font: pg.font.Font, s: str, x: int, y: int):
    surf = font.render(s, True, C.WHITE)
    rect = surf.get_rect(topleft=(x, y))
    surface.blit(surf, rect)


class AnimatedBackground:
    def __init__(self, gif_path, screen_size):
        self.frames = []
        self.current_frame = 0
        self.timer = 0.0
        
        try:
            pil_img = Image.open(gif_path)
        except:
            print(f"Erro ao carregar GIF: {gif_path}")
            return

        try:
            while True:
                frame = pil_img.convert("RGBA")
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                py_img = pg.image.frombytes(data, size, mode)
                
                py_img = pg.transform.scale(py_img, screen_size)
                self.frames.append(py_img)
                
                pil_img.seek(pil_img.tell() + 1)
        except EOFError:
            pass 

        try:
            self.delay = pil_img.info.get('duration', 100) / 1000.0
        except:
            self.delay = 0.1

    def update(self, dt):
        if not self.frames:
            return
            
        self.timer += dt
        if self.timer >= self.delay:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, surface):
        if self.frames:
            surface.blit(self.frames[self.current_frame], (0, 0))
        else:
            surface.fill((0, 0, 0))


def load_animation_from_folder(folder_path, size, count, color=(0, 255, 0)):
    frames = []
    for i in range(count):
        path_png = os.path.join(folder_path, f"{i}.png")
        try:
            img = load_image(path_png, size, color)
            frames.append(img)
        except:
            surf = pg.Surface(size)
            surf.fill(color)
            frames.append(surf)
    return frames


def load_animation_from_folder_list(folder_path, filenames, size, color=(0, 255, 0)):
    frames = []
    for name in filenames:
        path = os.path.join(folder_path, name)
        try:
            full_path = path + ".png"
            if not os.path.exists(full_path):
                full_path = path + ".jpg"
                
            img = load_image(full_path, size, color)
            frames.append(img)
        except:
            surf = pg.Surface(size)
            surf.fill(color)
            frames.append(surf)
    return frames