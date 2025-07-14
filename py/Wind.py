from Player import Player

import pygame as pg

class Wind(pg.sprite.Sprite):
    """
    扇風機に関するクラス
    """
    img = pg.image.load("fig/wind.gif")
    imgs = {
        0:img,
        180:pg.transform.flip(img, True, False),
    }

    instances = pg.sprite.Group()  # 全てのWindインスタンスを管理するグループ

    def __init__(self, center: tuple[int], angle: int = 0, vel: list[int] = [5, 5]):
        """
        扇風機の初期位置を設定
        引数: center: 扇風機の初期x,y座標
        """
        super().__init__()
        self.image = self.imgs[angle]
        self.image = pg.transform.rotozoom(self.image, angle, 2)
        self.rect = self.image.get_rect()
        # 画像の大きさが2倍なので調整する
        self.rect.x = center[0] - self.image.get_width() // 2
        self.rect.y = center[1] - self.image.get_height() // 2
        self.initial_pos = self.rect.x, self.rect.y

        self.reach = 300  # 扇風機の効果範囲(直線距離)
        self.angle = angle  # 風が吹く方向
        self.vx, self.vy = 5, 5  # 風の強さ

        self.instances.add(self)

    def update(self, vx: int = 0, doReset: bool = False):
        """
        扇風機の位置を更新する
        引数: vx: x方向の移動量, doReset: 初期位置に戻すかどうか
        """
        if doReset:
            self.rect.x, self.rect.y = self.initial_pos
        else:
            self.rect.x += vx
                