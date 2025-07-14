import pygame as pg
from Block import Block
from Player import Player
from Wind import Wind
from const import BLOCK_WIDTH, BLOCK_HEIGHT


def map_loading(filename: str):
    """
    ./map/filename.txt からマップを読み込み、ブロック等のインスタンスを生成する\n
    引数: filename
    """
    # 各プレイヤーに割り当てるID. 最大5人
    player_ids = "abcde"

    # File Loading
    f = open(filename, "r", encoding="UTF-8")
    data = f.readlines()
    data = [row.replace("\n", "") for row in data]
    
    # Generating Sprites
    blocks = pg.sprite.Group()
    winds = pg.sprite.Group()
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
            
            # 扇風機
            elif char == "w":
                winds.add(Wind((BLOCK_WIDTH * j, BLOCK_HEIGHT * i)))

            # プレイヤー
            elif char in player_ids:
                players.add(Player((BLOCK_WIDTH * j, BLOCK_HEIGHT * i), player_ids.index(char)))
    f.close()