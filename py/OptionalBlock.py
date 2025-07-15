from const import BLOCK_HEIGHT, BLOCK_WIDTH

import pygame as pg


class OptionalBlock(pg.sprite.Sprite):
    """
    ON状態のときに表示される赤いブロック（当たり判定あり）
    """
    instances = pg.sprite.Group()

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
        self.image.fill((255, 0, 0))  # 赤
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.instances.add(self)
        self.visible = True

    def update(self, vx: int = 0):
        self.rect.x += vx

    def draw(self, screen: pg.Surface):
        if self.visible:
            screen.blit(self.image, self.rect)

    def set_visible(self, visible: bool):
        self.visible = visible

    def active_group(cls) -> pg.sprite.Group:
        """
        現在可視状態のブロックだけをグループにして返す
        """
        group = pg.sprite.Group()
        for block in cls.instances:
            if block.visible:
                group.add(block)
        return group