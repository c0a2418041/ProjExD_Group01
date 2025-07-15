from OptionalBlock import OptionalBlock

import pygame as pg

class Switch_Button(pg.sprite.Sprite):
    """
    ON/OFFを切り替えるボタン
    """
    instances = pg.sprite.Group()  # 全インスタンスを管理

    def __init__(self, state: str, pos: tuple[int, int]):
        """
        state: "ON", "OFF"
        pos: 配置する座標 (左上)
        """
        super().__init__()
        self.state = state
        self.image = pg.image.load(f"fig/{self.state}.png")
        self.pos = pos
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