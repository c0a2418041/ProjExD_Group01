import pygame as pg


class Turret(pg.sprite.Sprite):
    """
    砲台に関するクラス
    """
    img = pg.transform.rotozoom(pg.image.load("fig/houdai.gif"), 0, 2)  # 50*50の画像を2倍に拡大
    imgs = {
        0:img,
        180:pg.transform.flip(img, True, False),
    }
    instances = pg.sprite.Group()

    def __init__(self, center: tuple[int], direction: int):
        super().__init__()
        self.direction = direction
        self.image = self.imgs[direction]
        self.rect = self.image.get_rect()
        self.rect.x = center[0] - self.image.get_width() // 2
        self.rect.y = center[1] - self.image.get_height() // 2
        self.initial_pos = self.rect.x, self.rect.y
        self.timer = 0
        self.instances.add(self)

    def get_rect(self):
        return self.rect

    def get_direction(self):
        return self.direction

    def update(self, vx: int = 0, doReset: bool = False):
        """
        砲台の位置を更新する\n
        引数: vx: x方向の移動量, doReset: 初期位置に戻すかどうか
        """
        if doReset:
            self.rect.x, self.rect.y = self.initial_pos
        else:
            self.rect.x += vx