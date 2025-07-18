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


def goal(screen: pg.Surface) -> None:
    """
    ゴール画面を表示、状態を初期化する関数\n
    引数: screen: 描画先のSurface
    """
    # テキストの設定
    font = pg.font.Font(None, 74)
    text = font.render("GOAL!!!", True, (0, 200, 0))
    text_rect = text.get_rect(center=(0, screen.get_height() // 2))

    white = pg.Surface((text_rect.width, text_rect.height))
    white.fill((255, 255, 255))
    
    # 画面左端から中央までテキストを移動する
    for i in range(0, screen.get_width() // 2, 5):
        screen.blit(white, text_rect)
        text_rect.x += 5
        screen.blit(text, text_rect)
        pg.display.update()
        pg.time.delay(10)  # 少し待つことでアニメーション効果を出す
            
    pg.time.delay(2000)  # 2秒間表示