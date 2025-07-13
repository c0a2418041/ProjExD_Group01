from Block import Block
from Player import Player

import pygame as pg

def game_over(screen: pg.Surface):
    """
    ゲームオーバー画面を表示する関数
    引数: screen: 描画先のSurface
    """
    # テキストの設定
    font = pg.font.Font(None, 74)
    text = font.render("GAME OVER", True, (255, 0, 0))
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

    # プレイヤーとブロックの位置を初期化
    for player in Player.instances:
        player.rect.x, player.rect.y = player.initial_pos
        player.true_pos = [player.rect.x, player.rect.y]

    for block in Block.instances:
        block.update(doReset=True)
