import os
import sys

import pygame as pg

from Block import Block
from Key import Key
from Goal import Goal
from Turret import Turret
from Player import Player
from OptionalBlock import OptionalBlock
from Switch_Button import Switch_Button
from Spike import Spike
from Spring import Spring
from Wind import Wind
from const import WIDTH, HEIGHT, HALF_WIDTH
from map_loading import map_loading
from gameover import game_over


os.path.dirname(os.path.abspath(__file__))
pg.init()

# マップ読み込み
map_loading("map/stage1.txt")  # インスタンス生成


# インスタンスの取得
blocks: pg.sprite.Group = Block.instances  # 全ブロック
blocks_optional: pg.sprite.Group = OptionalBlock.instances  # 全Optional Block
blocks_button: pg.sprite.Group = Switch_Button.instances  # 全スイッチ
players: pg.sprite.Group = Player.instances  # 全プレイヤー
player_main: Player = players.sprites()[0]  # 操作キャラは, 初期はplayersの先頭にする
player_others: pg.sprite.Group = players.sprites()[1:]  # 操作キャラ以外
winds: pg.sprite.Group = Wind.instances  # 全扇風機
keys: pg.sprite.Group = Key.instances  # 鍵の配列
goals: pg.sprite.Group = Goal.instances  # ゴールの配列
turrets: pg.sprite.Group = Turret.instances  # 砲台の配列
spikes: pg.sprite.Group = Spike.instances  # 棘の配列
springs: pg.sprite.Group = Spring.instances  # ばねの配列
render = pg.sprite.RenderUpdates()
render.add(blocks, winds, turrets, 
           spikes, springs, blocks_optional,
           blocks_button, keys, goals)


def check_collisions(player: Player, dx: int, dy: int) -> tuple[list]:
    """
    プレイヤーの衝突判定を行う\n
    引数: Playerインスタンス, xの移動量, yの移動量\n
    戻り値: x方向の衝突プレイヤーリスト, y方向の衝突プレイヤーリスト,\n
            x方向の衝突ブロックリスト, y方向の衝突ブロックリスト
    """
    hit_players_x = False
    hit_players_y = False
    hit_blocks_x = False
    hit_blocks_y = False

    # x方向の衝突判定
    player.rect.x += dx
    hit_blocks_x = pg.sprite.spritecollide(player, Block.instances, False)  # Block
    hit_opt = pg.sprite.spritecollide(player, OptionalBlock.instances, False)  # Optional Block
    hit_opt = [blk for blk in hit_opt if blk.visible]  # 可視状態のブロックだけ取り出す
    hit_spike = pg.sprite.spritecollide(player, Spike.instances, False)  # Spike
    hit_spring = pg.sprite.spritecollide(player, Spring.instances, False)  # Spring
    hit_players = pg.sprite.spritecollide(player, Player.instances, False)  # Player
    hit_players.remove(player)  # 自分自身を除外
    hit_blocks_x.extend(hit_opt)
    hit_blocks_x.extend(hit_spike)
    hit_blocks_x.extend(hit_spring)
    hit_blocks_x.extend(pg.sprite.spritecollide(player, Switch_Button.instances, False))
    player.rect.x -= dx

    # y方向の衝突判定
    player.rect.y += dy
    hit_blocks_y = pg.sprite.spritecollide(player, Block.instances, False)  # Block
    hit_opt = pg.sprite.spritecollide(player, OptionalBlock.instances, False)  # Optional Block
    hit_opt = [blk for blk in hit_opt if blk.visible]  # 可視状態のブロックだけ取り出す
    hit_spike = pg.sprite.spritecollide(player, Spike.instances, False)  # Spike
    hit_spring = pg.sprite.spritecollide(player, Spring.instances, False)  # Spring
    hit_players = pg.sprite.spritecollide(player, Player.instances, False)  # Player
    hit_players.remove(player)  # 自分自身を除外
    hit_blocks_y.extend(hit_opt)
    hit_blocks_y.extend(hit_spike)
    hit_blocks_y.extend(hit_spring)
    hit_blocks_y.extend(pg.sprite.spritecollide(player, Switch_Button.instances, False))
    player.rect.y -= dy

    return hit_players_x, hit_players_y, hit_blocks_x, hit_blocks_y


def main():
    pg.display.set_caption("Test")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    global player_main  # グローバル変数にしないと, キャラ入れ替えのときにUnBoundLocalErrorが起きる
    next_main_player = player_main
    current_screen_mid = HALF_WIDTH  # プレイヤーが画面中央を跨ぐと、画面スクロールが開始する

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
                    player_main.vx = 0
        
        player_main = next_main_player
        next_main_player = player_main
        
        # Game Over Check
        for player in players:
            if player.rect.y > HEIGHT:  # プレイヤーが奈落に落ちた場合
                game_over(screen)
                current_screen_mid = HALF_WIDTH
                tmr = 0
                break
        
        # Clear Screen
        screen.fill((255, 255, 255))

        # 常に受ける力
        for player in players:
            # 重力
            player.vy += player.gravity
            if player.is_on_turret:
                player.vx = 

            # 砲台
            if not player.is_on_turret:
                for turret in pg.sprite.spritecollide(player, turrets, False):
                    if not turret.direction:  # 右向き
                        player.vx, player.vy = 30, -10
                        player.is_on_turret = True
                    elif turret.direction == 180:  # 左向き
                        player.is_on_turret = True
            
            # 扇風機
            for wind in winds:
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
