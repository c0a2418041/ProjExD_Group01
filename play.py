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
        壁（ブロック＋可視状態の赤ブロック）との衝突判定
        """
        # 横方向の当たり
        self.rect.x += dx
        hit_blocks = pg.sprite.spritecollide(self, self.blocks, False)
        hit_blocks += pg.sprite.spritecollide(self, OptionalBlock.active_group(), False)
        for block in hit_blocks:
            if dx > 0:
                self.rect.right = block.rect.left
            elif dx < 0:
                self.rect.left = block.rect.right
            self.vx = 0

        # 縦方向の当たり
        self.rect.y += dy
        hit_blocks = pg.sprite.spritecollide(self, self.blocks, False)
        hit_blocks += pg.sprite.spritecollide(self, OptionalBlock.active_group(), False)
        for block in hit_blocks:
            if dy > 0:
                self.rect.bottom = block.rect.top
                self.is_jumping = False
                self.is_ground = True
            elif dy < 0:
                self.rect.top = block.rect.bottom
            self.vy = 0


    def update(self, key_lst: list[bool], screen: pg.Surface):
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


class OptionalBlock(pg.sprite.Sprite):
    """
    ON状態のときに表示される赤いブロック（当たり判定あり）
    """
    instances = []

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
        self.image.fill((255, 0, 0))  # 赤
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        OptionalBlock.instances.append(self)
        self.visible = True

    def update(self, vx: int = 0):
        self.rect.x += vx

    def draw(self, screen: pg.Surface):
        if self.visible:
            screen.blit(self.image, self.rect)

    @classmethod
    def set_visible(cls, visible: bool):
        for block in cls.instances:
            block.visible = visible

    @classmethod
    def active_group(cls) -> pg.sprite.Group:
        """
        現在可視状態のブロックだけをグループにして返す
        """
        group = pg.sprite.Group()
        for block in cls.instances:
            if block.visible:
                group.add(block)
        return group


class Switch_Button(pg.sprite.Sprite):
    '''
    ON/OFFを切り替えるボタン
    '''
    instances = []  # 全インスタンスを管理

    def __init__(self, state: str, pos: tuple[int, int]):
        """
        state: "N"ならON, "F"ならOFF
        pos: 配置する座標 (左上)
        """
        super().__init__()
        self.state = state
        self.pos = pos
        self.update_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        Switch_Button.instances.append(self)

    def update_image(self):
        if self.state == "N":
            self.image = pg.image.load("fig/ON.png")
        else:
            self.image = pg.image.load("fig/OFF.png")

    def toggle(self):
        # N→F, F→N
        if self.state == "N":
            self.state = "F"
        else:
            self.state = "N"
        self.update_image()

    def update(self, vx: int = 0):
        self.rect.x += vx

    def check_collision(self, player: Player):
    # 移動後の位置で当たり判定
        temp_rect = self.rect.move(0, 0)
        future_rect = player.rect.move(player.vx, player.vy)
        if temp_rect.colliderect(future_rect):
            if self.state == "N":
                for btn in Switch_Button.instances:
                    btn.state = "F"
                    btn.update_image()
                OptionalBlock.set_visible(False)
            elif self.state == "F":
                for btn in Switch_Button.instances:
                    btn.state = "N"
                    btn.update_image()
                OptionalBlock.set_visible(True)


def map_loading(filename: str) -> pg.sprite.Group:
    f = open(filename, "r", encoding="UTF-8")
    data = [line.strip() for line in f.readlines()]
    f.close()

    blocks = pg.sprite.Group()
    for i, row in enumerate(data):
        for j, char in enumerate(row):
            x = BLOCK_WIDTH * j
            y = BLOCK_HEIGHT * i
            if char == "1":
                blocks.add(Block((225, 150, 0), (x, y, x + BLOCK_WIDTH, y + BLOCK_HEIGHT)))
            elif char == "F":
                blocks.add(Switch_Button("F", (x, y)))
            elif char == "N":
                blocks.add(Switch_Button("N", (x, y)))
            elif char == "O":
                OptionalBlock((x, y))  # 画面に描画されるが、Groupには入れない
    return blocks



def main():
    pg.display.set_caption("Test")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    #インスタンス生成
    blocks = map_loading("map/stage1.txt")
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
        else:
            blocks.update()
        blocks.draw(screen)

        for ob in OptionalBlock.instances:
            ob.draw(screen)
            if player.rect.x > half_screen:
                ob.update(-player.vx)
        player.update(key_lst, screen)

        # Switch_Buttonとの衝突判定
        for btn in Switch_Button.instances:
            btn.check_collision(player)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()