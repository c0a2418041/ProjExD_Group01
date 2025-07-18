import pygame as pg


class Spring(pg.sprite.Sprite):
    """
    ばねの設置
    """
    instances = pg.sprite.Group()

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = pg.image.load("fig/bane.gif")
        self.rect = self.image.get_rect(topleft=pos)
        self.initial_pos = self.rect.x, self.rect.y
        self.instances.add(self)

    def update(self, vx: int = 0, doReset: bool = False):
        if doReset:
            self.rect.x, self.rect.y = self.initial_pos
        else:
            self.rect.x += vx