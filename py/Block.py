import pygame as pg
from const import BLOCK_WIDTH, BLOCK_HEIGHT


class Block(pg.sprite.Sprite):
    """
    壁・地面に関するクラス
    """
    instances = pg.sprite.Group()  # 全てのBlockインスタンスを管理するグループ

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
        self.initial_pos = self.rect.x, self.rect.y  # 初期位置

        self.instances.add(self)
    
    def update(self, vx: int = 0, doReset: bool = False):
        """
        ブロックの位置を更新する
        引数: vx: x方向の移動量, doReset: 初期位置に戻すかどうか
        """
        if doReset:
            self.rect.x, self.rect.y = self.initial_pos
        else:
            self.rect.x += vx
