import math
from random import uniform
from pathlib import Path

import pygame as pg

import config as C
from sprites import Player, Enemy, Sword, load_image, Wall
from utils import Vec, AnimatedBackground
from sound import SoundManager

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


class MixedKeys:
    def __init__(self, base_keys, joy_flags):
        self.base = base_keys
        self.joy = joy_flags

    def __getitem__(self, key):
        try:
            val = self.base[key]
        except Exception:
            val = False

        ax = self.joy.get("aim_x", 0.0)
        ay = self.joy.get("aim_y", 0.0)
        deadzone = 0.25

        if key == pg.K_UP and ay < -deadzone:
            return True
        if key == pg.K_DOWN and ay > deadzone:
            return True
        if key == pg.K_LEFT and ax < -deadzone:
            return True
        if key == pg.K_RIGHT and ax > deadzone:
            return True

        return val


class World:
    def __init__(self):
        self.maps = [
            AnimatedBackground(str(ASSETS_DIR / "mapa1.gif"), (C.WIDTH, C.HEIGHT)),
            AnimatedBackground(str(ASSETS_DIR / "mapa2.gif"), (C.WIDTH, C.HEIGHT)),
        ]
        self.current_map_index = 0

        self.player = Player(Vec(C.WIDTH / 2, C.HEIGHT / 2))
        self.sword_attacks = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group(self.player)

        self.walls = pg.sprite.Group()
        self.create_walls_for_map(0)
        self.show_walls = False

        self.score = 0
        self.lives = C.START_LIVES
        self.is_game_over = False

        self.wave = 1
        self.wave_timer = 0.0
        self.spawn_rate = C.UFO_SPAWN_EVERY
        self.max_enemies = C.BASE_MAX_ENEMIES
        self.enemy_timer = self.spawn_rate

        self.safe_timer = 0

        self.sound = SoundManager()
        self.sound.start_music()

        self.hp_sprites = {
            3: load_image(str(ASSETS_DIR / "hp_full.png"), (150, 40), (0, 255, 0)),
            2: load_image(str(ASSETS_DIR / "hp_mid.png"),  (150, 40), (255, 255, 0)),
            1: load_image(str(ASSETS_DIR / "hp_low.png"),  (150, 40), (255, 0, 0)),
        }

    def create_walls_for_map(self, map_index):
        self.walls.empty()
        if map_index == 0:
            self.walls.add(Wall(0, -50, C.WIDTH, 50))
            self.walls.add(Wall(580, 305, 25, 100))
            self.walls.add(Wall(607, 380, 100, 25))
            self.walls.add(Wall(707, 341, 50, 50))
            self.walls.add(Wall(610, 284, 50, 50))
            self.walls.add(Wall(623, 273, 50, 50))
            self.walls.add(Wall(642, 274, 50, 50))
            self.walls.add(Wall(667, 274, 50, 50))
            self.walls.add(Wall(683, 261, 50, 50))
            self.walls.add(Wall(701, 248, 50, 50))
            self.walls.add(Wall(714, 232, 50, 50))
            self.walls.add(Wall(727, 228, 50, 50))
            self.walls.add(Wall(747, 230, 50, 50))
            self.walls.add(Wall(771, 283, 50, 50))
            self.walls.add(Wall(772, 315, 50, 50))
            self.walls.add(Wall(759, 323, 50, 50))
            self.walls.add(Wall(147, 228, 100, 120))
            self.walls.add(Wall(337, 306, 50, 100))
            self.walls.add(Wall(245, 303, 100, 100))
            self.walls.add(Wall(286, 272, 50, 50))
            self.walls.add(Wall(327, 279, 50, 50))
            self.walls.add(Wall(239, 244, 50, 50))
            self.walls.add(Wall(191, 349, 50, 50))
            self.walls.add(Wall(535, 631, 50, 100))
            self.walls.add(Wall(567, 595, 50, 50))
            self.walls.add(Wall(622, 592, 50, 100))
            self.walls.add(Wall(289, 597, 50, 120))
            self.walls.add(Wall(336, 597, 50, 50))
            self.walls.add(Wall(387, 625, 50, 100))
            self.walls.add(Wall(635, 1, 160, 50))
            self.walls.add(Wall(146, 3, 160, 50))
            self.walls.add(Wall(918, 241, 50, 50))
            self.walls.add(Wall(2, 198, 30, 50))
            self.walls.add(Wall(147, 63, 30, 50))
            self.walls.add(Wall(770, 62, 30, 50))
            self.walls.add(Wall(776, 458, 80, 50))
            self.walls.add(Wall(152, 452, 80, 50))
            self.walls.add(Wall(671, 662, 280, 50))
            self.walls.add(Wall(0, 633, 280, 50))

        elif map_index == 1:
            self.walls.add(Wall(0, C.HEIGHT, C.WIDTH, 50))
            self.walls.add(Wall(395, 2, 45, 50))
            self.walls.add(Wall(534, 4, 30, 50))
            self.walls.add(Wall(0, 620, 280, 50))
            self.walls.add(Wall(718, 618, 280, 50))
            self.walls.add(Wall(633, 664, 100, 50))
            self.walls.add(Wall(689, 636, 50, 50))
            self.walls.add(Wall(291, 662, 50, 50))
            self.walls.add(Wall(625, 251, 50, 50))
            self.walls.add(Wall(677, 248, 50, 50))
            self.walls.add(Wall(731, 209, 50, 50))
            self.walls.add(Wall(728, 162, 50, 50))
            self.walls.add(Wall(727, 107, 50, 50))
            self.walls.add(Wall(627, 50, 50, 50))
            self.walls.add(Wall(672, 54, 50, 50))
            self.walls.add(Wall(578, 33, 50, 50))
            self.walls.add(Wall(188, 104, 50, 50))
            self.walls.add(Wall(189, 151, 50, 50))
            self.walls.add(Wall(192, 205, 50, 50))
            self.walls.add(Wall(191, 254, 50, 50))
            self.walls.add(Wall(238, 249, 50, 50))
            self.walls.add(Wall(280, 245, 50, 50))
            self.walls.add(Wall(314, 248, 50, 50))
            self.walls.add(Wall(336, 273, 50, 50))
            self.walls.add(Wall(337, 290, 50, 50))
            self.walls.add(Wall(380, 293, 50, 50))
            self.walls.add(Wall(244, 53, 50, 50))
            self.walls.add(Wall(295, 51, 50, 50))
            self.walls.add(Wall(324, 38, 50, 50))
            self.walls.add(Wall(339, 23, 50, 50))
            self.walls.add(Wall(811, 62, 50, 50))
            self.walls.add(Wall(814, 111, 50, 50))
            self.walls.add(Wall(798, 144, 50, 50))
            self.walls.add(Wall(787, 177, 50, 50))
            self.walls.add(Wall(766, 185, 50, 50))
            self.walls.add(Wall(768, 225, 50, 50))
            self.walls.add(Wall(768, 259, 50, 50))
            self.walls.add(Wall(768, 294, 50, 50))
            self.walls.add(Wall(763, 312, 50, 50))
            self.walls.add(Wall(861, 12, 50, 50))
            self.walls.add(Wall(897, 8, 50, 50))
            self.walls.add(Wall(724, 351, 50, 50))
            self.walls.add(Wall(697, 357, 50, 50))
            self.walls.add(Wall(696, 383, 50, 50))
            self.walls.add(Wall(660, 361, 50, 50))
            self.walls.add(Wall(640, 348, 50, 50))
            self.walls.add(Wall(641, 333, 50, 50))
            self.walls.add(Wall(595, 330, 50, 50))
            self.walls.add(Wall(567, 330, 50, 50))
            self.walls.add(Wall(536, 294, 50, 50))
            self.walls.add(Wall(579, 294, 50, 50))
            self.walls.add(Wall(599, 271, 50, 50))
            self.walls.add(Wall(870, 256, 30, 50))
            self.walls.add(Wall(873, 291, 30, 50))
            self.walls.add(Wall(877, 346, 30, 50))
            self.walls.add(Wall(824, 312, 30, 50))
            self.walls.add(Wall(823, 285, 30, 50))
            self.walls.add(Wall(107, 65, 50, 50))
            self.walls.add(Wall(105, 111, 50, 50))
            self.walls.add(Wall(110, 151, 50, 50))
            self.walls.add(Wall(158, 212, 50, 50))
            self.walls.add(Wall(151, 274, 50, 50))
            self.walls.add(Wall(152, 273, 50, 50))
            self.walls.add(Wall(1, 2, 50, 50))
            self.walls.add(Wall(26, 3, 50, 50))
            self.walls.add(Wall(44, 3, 50, 50))
            self.walls.add(Wall(80, 7, 50, 50))
            self.walls.add(Wall(86, 8, 50, 50))
            self.walls.add(Wall(171, 323, 50, 50))
            self.walls.add(Wall(203, 340, 50, 50))
            self.walls.add(Wall(208, 355, 50, 50))
            self.walls.add(Wall(233, 362, 50, 50))
            self.walls.add(Wall(246, 381, 50, 50))
            self.walls.add(Wall(269, 375, 50, 50))
            self.walls.add(Wall(270, 373, 50, 50))
            self.walls.add(Wall(298, 358, 50, 50))
            self.walls.add(Wall(309, 342, 50, 50))
            self.walls.add(Wall(321, 339, 50, 50))
            self.walls.add(Wall(350, 338, 50, 50))
            self.walls.add(Wall(372, 337, 50, 50))
            self.walls.add(Wall(379, 340, 50, 50))

    def change_map(self, new_index):
        self.current_map_index = new_index
        self.create_walls_for_map(new_index)
        self.sword_attacks.empty()

    def spawn_enemy(self):
        if uniform(0, 1) < 0.5:
            x = 0 if uniform(0, 1) < 0.5 else C.WIDTH
            y = uniform(0, C.HEIGHT)
        else:
            x = uniform(0, C.WIDTH)
            y = 0 if uniform(0, 1) < 0.5 else C.HEIGHT

        enemy = Enemy(Vec(x, y), self.sound)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

        self.sound.play_enemy_spawn()

    def try_fire(self):
        sword = self.player.attack()
        if sword:
            self.sword_attacks.add(sword)
            self.all_sprites.add(sword)
            self.sound.play_sword()

    def update(self, dt: float, keys, joy=None):
        if joy is None:
            joy = {}

        if keys[pg.K_h]:
            self.show_walls = not self.show_walls
            pg.time.delay(150)

        self.maps[self.current_map_index].update(dt)
        self.all_sprites.update(dt)

        if self.current_map_index == 0 and self.player.pos.y > C.HEIGHT:
            self.change_map(1)
            self.player.pos.y = 20
        elif self.current_map_index == 1 and self.player.pos.y < 0:
            self.change_map(0)
            self.player.pos.y = C.HEIGHT - 20

        hits = pg.sprite.spritecollide(self.player, self.walls, False)
        if hits:
            self.player.pos -= self.player.player_vel_applied * dt
            self.player.rect.center = self.player.pos

        mixed_keys = MixedKeys(keys, joy)
        self.player.control(mixed_keys, dt)

        for enemy in self.enemies:
            if enemy.state == "DEATH":
                continue
            diff = self.player.pos - enemy.pos
            dist = diff.length()
            if dist <= C.ENEMY_ATTACK_RANGE:
                enemy.dir = Vec(0, 0)
                enemy.trigger_attack()
            else:
                if diff.length() > 0:
                    enemy.dir = diff.normalize()

        self.wave_timer += dt
        if self.wave_timer >= C.WAVE_DURATION:
            self.wave_timer = 0
            self.wave += 1
            self.spawn_rate = max(C.MIN_SPAWN_RATE, self.spawn_rate * 0.9)
            self.max_enemies += 2

        self.enemy_timer -= dt
        if self.enemy_timer <= 0:
            if len(self.enemies) < self.max_enemies:
                self.spawn_enemy()
            self.enemy_timer = self.spawn_rate

        self.handle_collisions()

    def handle_collisions(self):
        hits = pg.sprite.groupcollide(
            self.sword_attacks, self.enemies, False, False
        )
        for sword, hit_enemies in hits.items():
            for enemy in hit_enemies:
                if enemy.state != "DEATH":
                    enemy.take_damage(1)
                    if enemy.hp <= 0:
                        self.score += 100
                        self.sound.play_enemy_death()
                        self.player.trigger_kill_anim()

        if self.player.invuln <= 0:
            live_enemies = [
                e for e in self.enemies if e.state != "DEATH"
            ]
            hits = pg.sprite.spritecollide(
                self.player, live_enemies, False, pg.sprite.collide_rect
            )
            if hits:
                self.take_hit()

    def take_hit(self):
        self.sound.play_player_hit()
        self.lives -= 1
        if self.lives > 0:
            self.player.invuln = C.SAFE_SPAWN_TIME
        else:
            self.is_game_over = True

    def draw(self, surf: pg.Surface, font: pg.font.Font):
        self.maps[self.current_map_index].draw(surf)

        if self.player.invuln > 0:
            if (pg.time.get_ticks() // 100) % 2 == 0:
                self.all_sprites.draw(surf)
        else:
            self.all_sprites.draw(surf)

        txt = f"SCORE: {self.score:05d}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (20, 20))

        txt_wave = f"WAVE {self.wave}"
        label_wave = font.render(txt_wave, True, (255, 255, 0))
        surf.blit(
            label_wave,
            (C.WIDTH // 2 - label_wave.get_width() // 2, 20),
        )

        current_hp = max(1, min(3, self.lives))
        if self.lives > 0:
            hp_img = self.hp_sprites[current_hp]
            x_pos = C.WIDTH - hp_img.get_width() - 20
            y_pos = 20
            surf.blit(hp_img, (x_pos, y_pos))