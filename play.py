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

    def update(self, key_lst: list[bool], screen: pg.Surface, spikes: pg.sprite.Group, springs: pg.sprite.Group) -> bool:
        """
        画面に表示する
        """
        self.vx = 0
        if key_lst[pg.K_a]:
            self.vx = self.delta[pg.K_a] * self.walk_speed
        if key_lst[pg.K_d]:
            self.vx = self.delta[pg.K_d] * self.walk_speed
        
        if self.is_jumping:
            self.vy += self.gravity
            self.is_ground = False

        self.wall(self.vx, self.vy)
        if pg.sprite.spritecollide(self, spikes, False):
            return True

        if pg.sprite.spritecollide(self, springs, False):
            self.is_jumping = True
            self.vy = SPEED_JUMP * 1.5
        screen.blit(self.image, self.rect)


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


def map_loading(filename: str) -> tuple[pg.sprite.Group, pg.sprite.Group, pg.sprite.Group]:
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
    spikes = pg.sprite.Group()
    springs = pg.sprite.Group()
    for i, row in enumerate(data):
        for j, char in enumerate(row):
            if char == "1":
                blocks.add(Block((225, 150, 0),
                    (BLOCK_WIDTH * j,
                     BLOCK_HEIGHT * i, 
                     BLOCK_WIDTH * (j+1), 
                     BLOCK_HEIGHT * (i+1))))
            elif char == "2":
                spikes.add(Spike((BLOCK_WIDTH * j,BLOCK_HEIGHT * i)))
            elif char == "3":
                springs.add(Spring((BLOCK_WIDTH * j,BLOCK_HEIGHT * i)))
    return blocks, spikes, springs

class Spike(pg.sprite.Sprite):
    """
    棘の設置
    """
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = pg.image.load("fig/toge.gif")
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, vx: int = 0):
        self.rect.x += vx

class Spring(pg.sprite.Sprite):
    """
    ばねの設置
    """
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = pg.image.load("fig/bane.gif")
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, vx: int = 0):
        self.rect.x += vx



def main():
    pg.display.set_caption("Test")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    #インスタンス生成
    blocks, spikes, springs = map_loading("map/stage1.txt")
    player = Player((150, HEIGHT - 150), blocks)
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
        
        # Clear Screen
        screen.fill((255, 255, 255))

	    # なにかの処理
        player.vy += player.gravity        

        # Update
        if player.rect.x > half_screen:
            blocks.update(-player.vx) 
            spikes.update(-player.vx)
            springs.update(-player.vx)
        else:
            blocks.update()
            spikes.update()
            springs.update()
        blocks.draw(screen)
        spikes.draw(screen)
        springs.draw(screen)

        gameover = player.update(key_lst, screen, spikes, springs)
        if gameover:
            fonto = pg.font.Font(None, 80)
            txt = fonto.render("Game Over",True,(255,0,0))
            screen.blit(txt,[WIDTH//2-150,HEIGHT//2])
            pg.display.update()
            time.sleep(1)
            break
        player.update(key_lst, screen, spikes, springs)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()