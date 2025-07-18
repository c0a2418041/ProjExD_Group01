import pygame as pg


class Spike(pg.sprite.Sprite):
    """
    棘の設置
    """
    img = pg.image.load("fig/toge.gif")
    imgs = {
        0:img,
        90: pg.transform.rotozoom(img, 90, 0),
        180: pg.transform.flip(img, True, False),
        270: pg.transform.rotozoom(img, 270, 0)
    }
    instances = pg.sprite.Group()

    def __init__(self, pos: tuple[int, int], direction: int = 0):
        super().__init__()
        self.image = self.imgs[direction]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.initial_pos = self.rect.x, self.rect.y
        self.instances.add(self)

    def update(self, vx: int = 0, doReset: bool = False):
        if doReset:
            self.rect.x, self.rect.y = self.initial_pos
        else:
            self.rect.x += vx