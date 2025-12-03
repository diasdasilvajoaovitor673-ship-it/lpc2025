import math
import os
from random import uniform
import pygame as pg

import config as C
from utils import (
    Vec,
    wrap_pos,
    load_image,
    load_gif_frames,
    load_animation_from_folder,
    load_animation_from_folder_list,
)

VAMPIRE_FOLDER = os.path.join("assets", "vampire", "v1")
SKELETON_FOLDER = os.path.join("assets", "skeleton1", "v1")

VAMPIRE_NAMES = [
    "vampire_v1_1",
    "vampire_v1_2",
    "vampire_v1_3",
    "vampire_v1_4",
]

SKELETON_NAMES = [
    "skeleton_v1_1",
    "skeleton_v1_2",
    "skeleton_v1_3",
    "skeleton_v1_4",
]

ENEMY_SIZE = (50, 50)
ENEMY_DELAY = 0.12


class Sword(pg.sprite.Sprite):
    def __init__(self, player, facing, frames):
        super().__init__()
        self.player = player
        self.facing = facing
        self.frames = frames
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_delay = 0.1

        self.image = self.frames[0]
        self.update_position()

    def update_position(self):
        offset = 40
        cx, cy = self.player.rect.centerx, self.player.rect.centery

        if self.facing == "RIGHT":
            self.rect = self.image.get_rect(center=(cx + offset, cy))
        elif self.facing == "LEFT":
            self.rect = self.image.get_rect(center=(cx - offset, cy))
        elif self.facing == "UP":
            self.rect = self.image.get_rect(center=(cx, cy - offset))
        elif self.facing == "DOWN":
            self.rect = self.image.get_rect(center=(cx, cy + offset))

    def update(self, dt):
        self.update_position()
        self.anim_timer += dt
        if self.anim_timer >= self.anim_delay:
            self.anim_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
                self.player.is_attacking = False
            else:
                self.image = self.frames[self.frame_index]
                self.update_position()


class Player(pg.sprite.Sprite):
    def __init__(self, pos: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(0, 0)
        self.angle = 0.0
        self.cool = 0.0
        self.lives = C.START_LIVES
        self.invuln = 0.0

        self.facing = "RIGHT"
        self.is_attacking = False
        self.kill_timer = 0.0

        size = (50, 50)

        self.frames_idle_right = load_animation_from_folder(
            os.path.join("assets", "parado"), size, 3, (0, 255, 0)
        )
        self.frames_idle_left = [
            pg.transform.flip(img, True, False) for img in self.frames_idle_right
        ]
        
        self.frames_walk_right = load_animation_from_folder(
            os.path.join("assets", "direita"), size, 3, (0, 0, 255)
        )
        self.frames_walk_left = load_animation_from_folder(
            os.path.join("assets", "esquerda"), size, 3, (0, 0, 255)
        )
        
        self.img_kill_right = load_image(
            os.path.join("assets", "percival_mata_direita.png"), size, (255, 0, 0)
        )
        self.img_kill_left = load_image(
            os.path.join("assets", "percival_mata_esquerda.png"), size, (255, 0, 0)
        )

        sword_size = (60, 60)
        folder = os.path.join("assets", "espada")

        self.sword_frames = {
            "RIGHT": load_animation_from_folder_list(
                folder, ["espada_pra_direita_1", "espada_pra_direita_2"], sword_size
            ),
            "LEFT": load_animation_from_folder_list(
                folder, ["espada_pra_esquerda_1", "espada_pra_esquerda_2"], sword_size
            ),
            "UP": load_animation_from_folder_list(
                folder, ["espada_pra_cima_1", "espada_pra_cima_2"], sword_size
            ),
            "DOWN": load_animation_from_folder_list(
                folder, ["espada_pra_baixo_1", "espada_pra_baixo_2"], sword_size
            ),
        }

        self.image = self.frames_idle_right[0]
        self.rect = self.image.get_rect(center=pos)
        self.anim_timer = 0.0
        self.frame_index = 0

    def control(self, keys, dt):
        dir_vec = Vec(0, 0)
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            dir_vec.x = -1
            self.facing = "LEFT"
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            dir_vec.x = 1
            self.facing = "RIGHT"
        if keys[pg.K_UP] or keys[pg.K_w]:
            dir_vec.y = -1
            self.facing = "UP"
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            dir_vec.y = 1
            self.facing = "DOWN"

        if dir_vec.length() > 0:
            dir_vec = dir_vec.normalize()
            self.kill_timer = 0.0

        self.vel = dir_vec * C.PLAYER_SPEED

    def attack(self):
        if self.is_attacking or self.cool > 0:
            return None
        self.is_attacking = True
        self.cool = 0.4
        frames = self.sword_frames.get(self.facing, self.sword_frames["RIGHT"])
        return Sword(self, self.facing, frames)

    def trigger_kill_anim(self):
        if self.vel.length() == 0:
            self.kill_timer = 2.0
            self.anim_timer = 0

    def update(self, dt):
        if self.cool > 0: self.cool -= dt
        if self.invuln > 0: self.invuln -= dt
        if self.kill_timer > 0: self.kill_timer -= dt

        self.player_vel_applied = self.vel
        self.pos += self.vel * dt

        if self.pos.x < C.PLAYER_RADIUS: self.pos.x = C.PLAYER_RADIUS
        if self.pos.x > C.WIDTH - C.PLAYER_RADIUS: self.pos.x = C.WIDTH - C.PLAYER_RADIUS

        self.anim_timer += dt
        current_frames = []
        anim_speed = 0.2

        if self.kill_timer > 0:
            if "RIGHT" in self.facing: current_frames = [self.img_kill_right]
            else: current_frames = [self.img_kill_left]
        elif self.vel.length() > 0:
            if self.facing == "LEFT": current_frames = self.frames_walk_left
            else: current_frames = self.frames_walk_right
            anim_speed = 0.15
        else:
            if self.facing == "LEFT": current_frames = self.frames_idle_left
            else: current_frames = self.frames_idle_right
            anim_speed = 0.3

        if current_frames:
            if self.anim_timer >= anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(current_frames)
            self.image = current_frames[self.frame_index % len(current_frames)]

        self.rect = self.image.get_rect(center=self.pos)

    def fire(self): return None
    def hyperspace(self): pass


class Enemy(pg.sprite.Sprite):
    def __init__(self, pos, sound):
        super().__init__()
        self.pos = Vec(pos)
        self.sound = sound

        self.state = "WALK"
        self.hp = 1
        self.facing = "RIGHT"
        size = ENEMY_SIZE

        is_vampire = uniform(0, 1) < 0.5
        if is_vampire:
            base_folder = VAMPIRE_FOLDER
            base_names = VAMPIRE_NAMES
        else:
            base_folder = SKELETON_FOLDER
            base_names = SKELETON_NAMES

        frames = load_animation_from_folder_list(
            base_folder,
            base_names,
            size,
            color=(255, 0, 0),
        )

        self.frames_walk = frames
        self.frames_attack = frames
        self.frames_death = frames

        self.delay_walk = 0.18
        self.delay_attack = 0.12
        self.delay_death = 0.10

        self.frame_index = 0
        self.anim_timer = 0.0
        self.current_frames = self.frames_walk
        self.current_delay = self.delay_walk

        self.image = self.frames_walk[0]
        self.rect = self.image.get_rect(center=pos)

        self.speed = C.UFO_SPEED
        self.dir = Vec(0, 0)
        self.attack_cool = 0.0

    def update(self, dt: float):
        if self.attack_cool > 0: self.attack_cool -= dt
        if self.state == "WALK": self.update_walk(dt)
        elif self.state == "ATTACK": self.update_attack(dt)
        elif self.state == "DEATH": self.update_death(dt)
        
        if self.alive():
            self.pos = wrap_pos(self.pos)
            self.rect.center = self.pos

    def update_walk(self, dt):
        self.pos += self.dir * self.speed * dt
        if self.dir.x < 0: self.facing = "LEFT"
        elif self.dir.x > 0: self.facing = "RIGHT"
        self.animate_loop(dt, self.frames_walk, self.delay_walk)

    def update_attack(self, dt):
        finished = self.animate_once(dt, self.frames_attack, self.delay_attack)
        if finished:
            self.state = "WALK"
            self.attack_cool = C.ENEMY_ATTACK_COOLDOWN
            self.update_image(self.frames_walk)

    def update_death(self, dt):
        finished = self.animate_once(dt, self.frames_death, self.delay_death)
        if finished: self.kill()

    def animate_loop(self, dt, frames, delay):
        self.anim_timer += dt
        if self.anim_timer >= delay:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.update_image(frames)

    def animate_once(self, dt, frames, delay):
        self.anim_timer += dt
        if self.anim_timer >= delay:
            self.anim_timer = 0
            self.frame_index += 1
            if self.frame_index >= len(frames):
                self.frame_index = 0
                return True
            else:
                self.update_image(frames)
        return False

    def update_image(self, frame_list):
        idx = self.frame_index % len(frame_list)
        base_img = frame_list[idx]
        if self.facing == "LEFT":
            base_img = pg.transform.flip(base_img, True, False)
        self.image = base_img
        self.rect = self.image.get_rect(center=self.pos)

    def trigger_attack(self):
        if self.state == "WALK" and self.attack_cool <= 0:
            self.state = "ATTACK"
            self.frame_index = 0
            self.anim_timer = 0
            self.update_image(self.frames_attack)

    def take_damage(self, amount=1):
        if self.state == "DEATH": return
        self.hp -= amount
        if self.hp <= 0:
            self.state = "DEATH"
            self.frame_index = 0
            self.anim_timer = 0
            self.update_image(self.frames_death)


class Wall(pg.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((255, 0, 0))
        self.image.set_alpha(128)
        self.rect = self.image.get_rect(topleft=(x, y))