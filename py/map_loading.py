import pygame as pg
from Block import Block
from Goal import Goal
from Key import Key
from Player import Player
from OptionalBlock import OptionalBlock
from Switch_Button import Switch_Button
from Turret import Turret
from Spike import Spike
from Spring import Spring
from Wind import Wind
from const import BLOCK_WIDTH, BLOCK_HEIGHT


def map_loading(filename: str):
    """
    ./map/filename.txt からマップを読み込み、ブロック等のインスタンスを生成する\n
    引数: filename
    """
    # 各プレイヤーに割り当てるID. 最大5人
    player_ids = "abcde"
    wind_ids = "wxyz"
    turret_ids = "ABCDEFGH"

    # File Loading
    f = open(filename, "r", encoding="UTF-8")
    data = f.readlines()
    data = [row.replace("\n", "") for row in data]
    
    # Generating Sprites
    blocks = pg.sprite.Group()
    blocks_optional = pg.sprite.Group()
    blocks_button = pg.sprite.Group()
    turrets = pg.sprite.Group()
    spikes = pg.sprite.Group()
    springs = pg.sprite.Group()
    winds = pg.sprite.Group()
    keys = pg.sprite.Group()
    goals = pg.sprite.Group()
    players = pg.sprite.Group()

    for i, row in enumerate(data):            
        for j, char in enumerate(row):
            # 地面・壁
            if char == "1":
                blocks.add(Block((225, 150, 0),
                    (BLOCK_WIDTH * j,
                     BLOCK_HEIGHT * i, 
                     BLOCK_WIDTH * (j+1), 
                     BLOCK_HEIGHT * (i+1))))
                
            # 可視ブロック（オン）
            elif char == "2":
                blocks_optional.add(OptionalBlock(True, (BLOCK_WIDTH * j, BLOCK_HEIGHT * i)))
            
            # 可視ブロック（オフ）
            elif char == "3":
                blocks_optional.add(OptionalBlock(False, (BLOCK_WIDTH * j, BLOCK_HEIGHT * i)))
            
            # スイッチ（オン）
            elif char == "4":
                blocks_button.add(Switch_Button("ON", (BLOCK_WIDTH * j, BLOCK_HEIGHT * i)))
            
            # スイッチ（オフ）
            elif char == "5":
                blocks_button.add(Switch_Button("OFF", (BLOCK_WIDTH * j, BLOCK_HEIGHT * i)))

            # 棘
            elif char == "6":
                spikes.add(Spike((BLOCK_WIDTH * j, BLOCK_HEIGHT * i)))

            # ばね
            elif char == "7":
                springs.add(Spring((BLOCK_WIDTH * j, BLOCK_HEIGHT * i)))
            
            # 鍵
            elif char == "K":
                keys.add(Key((BLOCK_WIDTH * j, BLOCK_HEIGHT * i, BLOCK_WIDTH * (j+1), BLOCK_HEIGHT * (i+1))))

            # ゴール
            elif char == "G":
                goals.add(Goal((BLOCK_WIDTH * j, BLOCK_HEIGHT * i, BLOCK_WIDTH * (j+1), BLOCK_HEIGHT * (i+1))))
            
            # 砲台
            elif char in turret_ids:
                turrets.add(Turret((BLOCK_WIDTH * j, BLOCK_HEIGHT * i), 45 * turret_ids.index(char)))

            # 扇風機
            elif char in wind_ids:
                winds.add(Wind((BLOCK_WIDTH * j, BLOCK_HEIGHT * i), 90 * wind_ids.index(char)))

            # プレイヤー
            elif char in player_ids:
                players.add(Player((BLOCK_WIDTH * j, BLOCK_HEIGHT * i), player_ids.index(char)))
            
    f.close()