import os
import sys
import time
import math
import random

import pygame as pg


# Screen
WIDTH = 1100
HEIGHT = 650


# Block
BLOCK_WIDTH = 50
BLOCK_HEIGHT = 50


# Player
SPEED_WALK = 10
SPEED_JUMP = -40
SPEED_GRAVITY = 2


os.path.dirname(os.path.abspath(__file__))


class Player(pg.sprite.Sprite):
    """
    プレイヤーに関するクラス
    """
    delta = {
        pg.K_a: -1,
        pg.K_d: +1,
    }

    def __init__(self, center: tuple[int, int], blocks: pg.sprite.Group):
        """
        初期位置などを決める
        """
        super().__init__()
        # 吹っ飛び用のタイマーと減速率を追加
        self.knockback_timer = 5
        self.knockback_duration = 20  # 吹っ飛び時間（フレーム数）
        self.knockback_friction = 0.85
        # Surface
        self.image = pg.image.load("fig/test.gif")
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.blocks = blocks

        # Flags
        self.is_ground = True
        self.is_jumping = True

        # Speed
        self.vx, self.vy = 0, 0
        self.walk_speed = SPEED_WALK
        self.jump_speed = SPEED_JUMP
        self.gravity = SPEED_GRAVITY
    
    def wall(self, dx: int, dy: int) -> list[int]:
        """
        壁との衝突判定と位置調整を行う
        引数: dx, dy: プレイヤーが移動しようとした量
        """
        self.rect.x += dx
        hit_blocks = pg.sprite.spritecollide(self, self.blocks, False)
        for block in hit_blocks:
            if dx > 0:
                self.rect.right = block.rect.left
            elif dx < 0:
                self.rect.left = block.rect.right
            self.vx = 0
        
        self.rect.y += dy
        hit_blocks = pg.sprite.spritecollide(self, self.blocks, False)
        for block in hit_blocks:
            if dy > 0:
                self.rect.bottom = block.rect.top
                self.is_jumping = False
                self.is_ground = True
            elif dy < 0:
                self.rect.top = block.rect.bottom
            self.vy = 0

    def get_rect(self):
        return self.rect
    
    def set_velocity(self, vx: int, vy: int):
        self.vx = vx
        self.vy = vy
        self.is_jumping = True
        self.knockback_timer = self.knockback_duration

        
    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        画面に表示する
        """
        input_vx = 0
        if key_lst[pg.K_a]:
            self.vx = self.delta[pg.K_a] * self.walk_speed
        if key_lst[pg.K_d]:
            self.vx = self.delta[pg.K_d] * self.walk_speed
        
        self.vx += input_vx

        if self.is_jumping:
            self.vy += self.gravity
            self.is_ground = False

        self.wall(self.vx, self.vy)
        screen.blit(self.image, self.rect)

        if not key_lst[pg.K_a] and not key_lst[pg.K_d]:
            self.vx = 0


class Block(pg.sprite.Sprite):
    """
    壁・地面に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rect: tuple[int]):
        """
        ブロックの色, 座標の設定
        """
        super().__init__()
        self.image = pg.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
        self.image.fill(color)  # 色設定
        self.rect = self.image.get_rect()
        self.rect.topleft = rect[:2]
        self.rect.bottomright = rect[2:]
    
    def update(self, vx: int = 0):
        self.rect.x += vx


def map_loading(filename: str) -> pg.sprite.Group:
    """
    ./map/filename.txt からブロックの位置を読み込む関数
    引数: filename
    """
    # File Loading
    f = open(filename, "r", encoding="UTF-8")
    data = f.readlines()
    data = [row.replace("\n", "") for row in data]
    # Generating Surfaces
    blocks = pg.sprite.Group()
    for i, row in enumerate(data):
        for j, char in enumerate(row):
            if char == "1":
                blocks.add(Block((225, 150, 0),
                    (BLOCK_WIDTH * j,
                     BLOCK_HEIGHT * i, 
                     BLOCK_WIDTH * (j+1), 
                     BLOCK_HEIGHT * (i+1))))
    return blocks


def main():
    pg.display.set_caption("Test")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    #インスタンス生成
    blocks = map_loading("map/stage1.txt")
    player = Player((150, HEIGHT - 150), blocks)
    turrets = pg.sprite.Group()
    bullets = pg.sprite.Group()
    turrets.add(Turret((600, HEIGHT - 100), "right", bullets))

    half_screen = WIDTH // 2

    #時間計測用
    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE and not player.is_jumping:
                    player.is_jumping = True
                    player.vy = player.jump_speed
        
        screen.fill((255, 255, 255))
        player.vy += player.gravity
        for turret in turrets:
            turret.fire_player(player)
        if player.rect.x > half_screen:
            blocks.update(-player.vx)
            turrets.update(-player.vx)
        else:
            blocks.update()
            turrets.update()
        blocks.draw(screen)
        turrets.draw(screen)
        player.update(key_lst, screen) 
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()