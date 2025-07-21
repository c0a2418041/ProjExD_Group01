import pygame as pg

class Goal(pg.sprite.Sprite):
    """
    ゴールに関するクラス
    """
    instances = pg.sprite.Group()

    def __init__(self, rect: tuple[int]):
        """
        ブロックの色, 座標の設定
        """
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load("fig/goal.gif"), 0, 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = rect[:2]
        self.rect.bottomright = rect[2:]
        self.initial_pos = self.rect.x, self.rect.y  # 初期位置

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