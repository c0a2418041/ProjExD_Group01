import os
import sys

import pygame as pg

from Player import Player
from const import WIDTH, HEIGHT, HALF_WIDTH
from map_loading import map_loading
from gameover import game_over


os.path.dirname(os.path.abspath(__file__))


# マップ読み込み
loaded = map_loading("map/stage1.txt")
blocks = loaded[0]
players = loaded[1]
player_main: Player = players.sprites()[0]  # 最初のプレイヤーをメインに設定
player_others = players.sprites()[1:]  # 他のプレイヤー


def main():
    pg.display.set_caption("Test")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    #インスタンス生成
    global player_main
    next_main_player = player_main

    #時間計測用
    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN:
                # ジャンプ
                if player_main.is_ground:
                    if event.key == pg.K_SPACE and not player_main.is_jumping:
                        player_main.is_jumping = True
                        player_main.is_ground = False
                        player_main.vy = player_main.jump_speed
                
                # 操作キャラ入れ替え
                if event.key == pg.K_f:
                    next_main_player = player_others[0] if player_others else player_main
                    player_others.pop(0)
                    player_others.append(player_main)
        
        player_main = next_main_player
        next_main_player = player_main
        
        # Game Over Check
        for player in players:
            if player.rect.y > HEIGHT:  # プレイヤーが奈落に落ちた場合
                game_over(screen)
                break
        
        # Clear Screen
        screen.fill((255, 255, 255))

	    # Update
        for player in players:
            player.vy += player.gravity

        # Screen Scrolling
        for player in players:
            if player == player_main:
                if player.vx > 0:
                    if player.rect.x > HALF_WIDTH:
                        blocks.update(-player.vx)
                        player.rect.x = HALF_WIDTH

                        for other_player in player_others:
                            other_player.rect.x -= player.vx

                elif player.vx < 0:
                    if player.rect.x >= HALF_WIDTH + player.vx:
                        if player.true_pos[0] > HALF_WIDTH:
                            blocks.update(-player.vx)
                            player.rect.x = HALF_WIDTH

                            for other_player in player_others:
                                other_player.rect.x -= player.vx
                        else:
                            blocks.update(doReset=True)
                
        blocks.draw(screen)

        # Update
        for player in players:
            if player == player_main:
                player.update(key_lst, screen)
            else:
                player.update(key_lst=None, screen=screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()