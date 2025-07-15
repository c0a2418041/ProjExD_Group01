import math

import pygame as pg


class Wind(pg.sprite.Sprite):
    """
    扇風機に関するクラス
    """
    img = pg.transform.rotozoom(pg.image.load("fig/wind.gif"), 0, 2)  # 50*50の画像を2倍に拡大
    img2 = pg.transform.rotozoom(pg.image.load("fig/wind2.gif"), 0, 4)  # 25*25の画像を4倍に拡大
    imgs = {
        0:img,
        90:img2,
        180:pg.transform.flip(img, True, False),
        270:pg.transform.flip(img2, False, True)
    }

    instances = pg.sprite.Group()  # 全てのWindインスタンスを管理するグループ

    def __init__(self, center: tuple[int], angle: int = 0, vel: list[int] = [5, 5], reach: int = 300):
        """
        扇風機の初期位置を設定\n
        引数: center: 扇風機の初期x,y座標
        """
        super().__init__()
        self.image = self.imgs[angle]
        self.rect = self.image.get_rect()
        # 画像の大きさが2倍なので調整する
        self.rect.x = center[0] - self.image.get_width() // 2
        self.rect.y = center[1] - self.image.get_height() // 2
        self.initial_pos = self.rect.x, self.rect.y

        self.reach = reach  # 扇風機の効果範囲(直線距離)
        self.angle = angle  # 風が吹く方向
        # 風の強さ
        self.vx = vel[0] * math.cos(math.radians(self.angle))
        self.vy = vel[1] * math.sin(math.radians(self.angle))

        self.instances.add(self)

    def update(self, vx: int = 0, doReset: bool = False):
        """
        扇風機の位置を更新する\n
        引数: vx: x方向の移動量, doReset: 初期位置に戻すかどうか
        """
        if doReset:
            self.rect.x, self.rect.y = self.initial_pos
        else:
            self.rect.x += vx
                