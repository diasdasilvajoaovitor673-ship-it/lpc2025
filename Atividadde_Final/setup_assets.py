import os
import pygame as pg

pg.init()
pg.font.init()

if not os.path.exists("assets"):
    os.makedirs("assets")
    print("Pasta 'assets' criada.")

barras = [
    ("hp_full.png", (0, 255, 0)),
    ("hp_mid.png", (255, 255, 0)),
    ("hp_low.png", (255, 0, 0))
]

font = pg.font.SysFont("Arial", 20, bold=True)

for nome, cor in barras:
    surf = pg.Surface((150, 40))
    surf.fill((50, 50, 50))
    
    inner = pg.Surface((146, 36))
    inner.fill(cor)
    surf.blit(inner, (2, 2))
    
    text = font.render("HP", True, (0,0,0))
    surf.blit(text, (10, 8))
    
    caminho = os.path.join("assets", nome)
    pg.image.save(surf, caminho)
    print(f"Imagem criada: {caminho}")

print("\nSucesso! Agora rode o main.py")
pg.quit()