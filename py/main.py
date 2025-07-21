import os
import sys

import pygame as pg

from Block import Block
from Key import Key
from Goal import Goal
from Turret import Turret
from Player import Player
from Player import game_over
from Player import get_collision_sprites
from Player import goal
from OptionalBlock import OptionalBlock
from Switch_Button import Switch_Button
from Spike import Spike
from Spring import Spring
from Wind import Wind
from const import WIDTH, HEIGHT, HALF_WIDTH
from map_loading import map_loading


os.path.dirname(os.path.abspath(__file__))
pg.init()


# マップ読み込み
map_loading("map/stage1.txt")  # インスタンス生成


# インスタンスの取得
players: pg.sprite.Group = Player.instances  # 全プレイヤー
player_main: Player = players.sprites()[0]  # 操作キャラは, 初期はplayersの先頭にする
player_others: list[Player] = players.sprites()[1:]  # 操作キャラ以外
render = pg.sprite.RenderUpdates()
render.add(Block.instances, Wind.instances, Turret.instances, 
           Spike.instances, Spring.instances, OptionalBlock.instances,
           Switch_Button.instances, Key.instances, Goal.instances)


def check_collisions(player: Player, dx: int, dy: int) -> tuple[list]:
    """
    プレイヤーの衝突判定を行う\n
    引数: Playerインスタンス, xの移動量, yの移動量\n
    戻り値: x方向の衝突プレイヤーリスト, y方向の衝突プレイヤーリスト,\n
            x方向の衝突ブロックリスト, y方向の衝突ブロックリスト
    """
    # x方向の衝突判定
    player.rect.x += dx
    collides_x = get_collision_sprites(player)
    player.rect.x -= dx

    # y方向の衝突判定
    player.rect.y += dy
    collides_y = get_collision_sprites(player)
    player.rect.y -= dy

    return collides_x["player"], collides_y["player"], collides_x["blocks"], collides_y["blocks"]


def main():
    pg.display.set_caption("Test")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    global player_main  # キャラ切り替え時のUnBoundLocalError防止
    next_main_player = player_main
    current_screen_mid = HALF_WIDTH  # プレイヤーが画面中央を跨ぐと、画面スクロールが開始する

    # 初期の画面位置設定
    dx = -(next_main_player.rect.x - HALF_WIDTH)  # キャラが常に画面中央にくるよう調整
    render.update(dx)
    next_main_player.rect.x += dx
    current_screen_mid -= dx
    for other_player in player_others:
        other_player.rect.x += dx

    #時間計測用
    tmr = 0
    clock = pg.time.Clock()
    while True: 
        # イベント（キーボード操作）
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
                    if player_others:  # 他キャラがいるとき
                        next_main_player = player_others[0] if player_others else player_main
                        player_others.pop(0)
                        player_others.append(player_main)
                        player_main.vx = 0
                        # 画面スクロール
                        dx = -(next_main_player.rect.x - HALF_WIDTH)  # キャラが常に画面中央にくるよう調整
                        render.update(dx)
                        next_main_player.rect.x += dx
                        current_screen_mid -= dx
                        for other_player in player_others:
                            other_player.rect.x += dx
        
        player_main = next_main_player
        next_main_player = player_main
        
        # Game Over Check
        for player in players:
            if player.rect.y > HEIGHT:  # プレイヤーが奈落に落ちた場合
                player.is_alive = False
            
            if not player.is_alive:
                game_over(screen)
                return 0

            if player.show_goal:
                goal(screen)
                return 0
        
        # Clear Screen
        screen.fill((255, 255, 255))

        # 常に受ける力
        for player in players:
            # 重力
            player.vy += player.gravity
            
            # 扇風機
            for wind in Wind.instances:
                dx = player.rect.x - wind.rect.x
                dy = player.rect.y - wind.rect.y
                if wind.angle == 0:  # 右向きの風
                    if abs(dy) < 100:  # 100は扇風機の高さ
                        if 0 < dx < wind.reach:
                            player.rect.x += wind.vx
                            collisions = check_collisions(player, wind.vx, 0)

                            if not collisions[0] and not collisions[2]:  # 他のプレイヤーとブロックに衝突していない場合
                                player.true_pos[0] += wind.vx
                                player.vx += wind.vx
                            else:
                                player.rect.x -= wind.vx  # プレイヤーに当たったとき停止
                        else:
                            if player in player_others:  # 他プレイヤーが扇風機の範囲外に出たとき
                                player.vx = 0
                            
                elif wind.angle == 180:  # 左向きの風
                    if abs(dy) < 100:
                        if -wind.reach < dx < 0:
                            player.rect.x += wind.vx
                            collisions = check_collisions(player, wind.vx, 0)

                            if not collisions[0] and not collisions[2]:  # 他のプレイヤーとブロックに衝突していない場合
                                player.true_pos[0] += wind.vx
                                player.vx += wind.vx
                            else:
                                player.rect.x -= wind.vx  # プレイヤーに当たったとき停止
                        else:
                            if player in player_others:  # 他プレイヤーが扇風機の範囲外に出たとき
                                player.vx = 0
                
                elif wind.angle == 90:  # 上向きの風
                    if abs(dx) < 100:
                        if -wind.reach < dy < 0:
                            player.rect.y -= wind.vy
                            collisions = check_collisions(player, -wind.vy, 0)

                            if not collisions[1] and not collisions[3]:  # 他のプレイヤーとブロックに衝突していない場合
                                player.true_pos[1] += -wind.vy
                                player.vy += -wind.vy
                            else:
                                player.rect.y -= -wind.vy  # プレイヤーに当たったとき停止
                        else:
                            if player in player_others:  # 他プレイヤーが扇風機の範囲外に出たとき
                                player.vy = 0
                
                elif wind.angle == 270:  # 上向きの風
                    if abs(dx) < 100:
                        if 0 < dy < wind.reach:
                            player.rect.y -= wind.vy
                            collisions = check_collisions(player, -wind.vy, 0)

                            if not collisions[1] and not collisions[3]:  # 他のプレイヤーとブロックに衝突していない場合
                                player.true_pos[1] += -wind.vy
                                player.vy += -wind.vy
                            else:
                                player.rect.y -= -wind.vy  # プレイヤーに当たったとき停止
                        else:
                            if player in player_others:  # 他プレイヤーが扇風機の範囲外に出たとき
                                player.vy = 0
        
        # Update, Screen Scrolling
        if player_main.vx > 0:  # 右に移動するとき
            if player_main.true_pos[0] > current_screen_mid:
                render.update(-player_main.vx)

                player_main.rect.x -= player_main.vx
                current_screen_mid += player_main.vx

                for other_player in player_others:
                    other_player.rect.x -= player_main.vx
        
        elif player_main.vx < 0:  # 左に移動するとき
            if player_main.true_pos[0] < current_screen_mid:
                render.update(-player_main.vx)

                player_main.rect.x -= player_main.vx
                current_screen_mid += player_main.vx

                for other_player in player_others:
                    other_player.rect.x -= player_main.vx
                
        render.draw(screen)

        for player in players:
            if player == player_main:  # 操作キャラのみキーボード操作で移動可能
                player.update(key_lst, screen)
            else:  # 操作キャラ以外は停止
                player.update(key_lst=None, screen=screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
