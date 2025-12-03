from pathlib import Path
import pygame as pg
import config as C

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"


class SoundManager:
    def __init__(self):
        if not pg.mixer.get_init():
            pg.mixer.init()

        self.sfx_vol = C.MASTER_VOLUME * C.SFX_VOLUME_RATIO

        self.s_attack = self._load_sound("ataque.mp3")
        self.s_spawn = self._load_sound("spawnzumbi.mp3")
        self.s_death = self._load_sound("morte.mp3")
        self.s_hit = self._load_sound("morte.mp3") 

    def _load_sound(self, filename):
        path = SOUNDS_DIR / filename
        try:
            snd = pg.mixer.Sound(str(path))
            snd.set_volume(self.sfx_vol)
            return snd
        except Exception as e:
            return None

    def start_music(self):
        music_path = SOUNDS_DIR / "somdefundo.mp3"
        try:
            pg.mixer.music.load(str(music_path))
            
            music_vol = C.MASTER_VOLUME * C.MUSIC_VOLUME_RATIO
            pg.mixer.music.set_volume(music_vol)
            
            pg.mixer.music.play(-1)
        except Exception as e:
            print(f"[ERRO] Não carregou música de fundo: {music_path} -> {e}")

    def play_attack(self):
        if self.s_attack:
            self.s_attack.play()

    def play_sword(self):
        self.play_attack()

    def play_enemy_spawn(self):
        if self.s_spawn:
            self.s_spawn.play()

    def play_enemy_death(self):
        if self.s_death:
            self.s_death.play()

    def play_player_hit(self):
        if self.s_hit:
            self.s_hit.play()