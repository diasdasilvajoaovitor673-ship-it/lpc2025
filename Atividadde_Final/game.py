import random
import sys
from dataclasses import dataclass
import math
import pygame as pg

import config as C
from systems import World
from utils import text, AnimatedBackground


@dataclass
class Scene:
    name: str


class Game:
    def __init__(self):
        pg.init()
        pg.joystick.init()
        self.joy = None
        if pg.joystick.get_count() > 0:
            self.joy = pg.joystick.Joystick(0)
            self.joy.init()
            print("Joystick conectado:", self.joy.get_name())

        if C.RANDOM_SEED is not None:
            random.seed(C.RANDOM_SEED)

        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("inverted world")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("consolas", 20)
        self.big = pg.font.SysFont("consolas", 48)
        self.scene = Scene("menu")
        self.world = World()

        self.go_bg = AnimatedBackground("assets/gameover.gif", (C.WIDTH, C.HEIGHT))

        try:
            menu_img = pg.image.load("assets/menu.png").convert()
            self.menu_bg = pg.transform.scale(menu_img, (C.WIDTH, C.HEIGHT))
        except Exception as e:
            print(f"[ERRO] Não carregou menu.png: {e}")
            self.menu_bg = pg.Surface((C.WIDTH, C.HEIGHT))
            self.menu_bg.fill((0, 0, 0))

    def run(self):
        while True:
            dt = self.clock.tick(C.FPS) / 1000.0

            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit(0)
                if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit(0)
                if e.type == pg.MOUSEBUTTONDOWN:
                    mx, my = pg.mouse.get_pos()
                    print(f"self.walls.add(Wall({mx}, {my}, 50, 50))")

                if self.scene.name == "play":
                    if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                        self.world.try_fire()
                    if e.type == pg.KEYDOWN and e.key == pg.K_LSHIFT:
                        self.world.player.hyperspace()

                    if e.type == pg.JOYBUTTONDOWN and self.joy is not None:
                        if e.button == 0:
                            self.world.try_fire()
                        if e.button == 1:
                            self.world.player.hyperspace()

                elif self.scene.name == "menu":
                    if e.type == pg.KEYDOWN or e.type == pg.JOYBUTTONDOWN:
                        self.scene = Scene("play")

                elif self.scene.name == "gameover":
                    if e.type == pg.KEYDOWN or e.type == pg.JOYBUTTONDOWN:
                        self.world = World()
                        self.scene = Scene("play")

            keys = pg.key.get_pressed()
            joy_input = {"thrust": False, "aim_x": 0.0, "aim_y": 0.0}
            if self.joy is not None and self.scene.name == "play":
                x_axis = self.joy.get_axis(0)
                y_axis = self.joy.get_axis(1)
                deadzone = 0.25
                magnitude = math.hypot(x_axis, y_axis)
                if magnitude > deadzone:
                    joy_input["aim_x"] = x_axis
                    joy_input["aim_y"] = y_axis
                    joy_input["thrust"] = True

            self.screen.fill(C.BLACK)

            if self.scene.name == "menu":
                self.draw_menu()

            elif self.scene.name == "play":
                if self.world.is_game_over:
                    self.scene = Scene("gameover")
                else:
                    self.world.update(dt, keys, joy_input)
                    self.world.draw(self.screen, self.font)

            elif self.scene.name == "gameover":
                self.go_bg.update(dt)
                self.go_bg.draw(self.screen)

                if (pg.time.get_ticks() // 500) % 2 == 0:
                    text(
                        self.screen,
                        self.big,
                        "GAME OVER",
                        C.WIDTH // 2 - 120,
                        C.HEIGHT // 2 - 50,
                    )
                    text(
                        self.screen,
                        self.font,
                        "Pressione qualquer tecla",
                        C.WIDTH // 2 - 130,
                        C.HEIGHT // 2 + 20,
                    )

            pg.display.flip()

    def draw_menu(self):
        self.screen.blit(self.menu_bg, (0, 0))