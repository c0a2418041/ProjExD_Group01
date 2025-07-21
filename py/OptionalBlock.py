from const import BLOCK_HEIGHT, BLOCK_WIDTH

import pygame as pg


class OptionalBlock(pg.sprite.Sprite):
    """
    ON状態のときに表示される赤いブロック（当たり判定あり）
    """
    instances = pg.sprite.Group()

    def __init__(self, visible: bool, pos: tuple[int, int]):
        super().__init__()
        self.visible = visible
        self.image = pg.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
        if self.visible:
            self.image.fill((255, 0, 0))  # 赤
        else:
            self.image.fill((255,255,255))  # 透明（白）
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.initial_pos = self.rect.x, self.rect.y
        self.instances.add(self)

    def update(self, vx: int = 0, doReset: bool = False):
        """
        ブロックの位置を更新する\n
        引数: vx: x方向の移動量
        """
        if doReset:
            self.rect.x, self.rect.y = self.initial_pos
        else:
            self.rect.x += vx

    def draw(self, screen: pg.Surface):
        if self.visible:
            screen.blit(self.image, self.rect)
