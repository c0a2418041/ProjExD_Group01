import pygame as pg
from Block import Block
from OptionalBlock import OptionalBlock
from Switch_Button import Switch_Button
from const import SPEED_WALK, SPEED_JUMP, SPEED_GRAVITY


class Player(pg.sprite.Sprite):
    """
    プレイヤーに関するクラス
    """
    delta = {
        pg.K_a: -1,
        pg.K_d: +1,
    }

    instances = pg.sprite.Group()  # 全てのPlayerインスタンスを管理するグループ

    def __init__(self, center: tuple[int, int], id: str):
        """
        初期位置、足の速さなどの決定
        """
        super().__init__()
        # Surface
        self.id = id
        self.image = pg.image.load(f"fig/{self.id}.gif")
        self.rect = self.image.get_rect()
        self.rect.x = center[0]
        self.rect.y = center[1]
        self.initial_pos = self.rect.x, self.rect.y
        self.true_pos = [self.rect.x, self.rect.y]

        # Flags
        self.is_ground = True
        self.is_jumping = True
        self.is_on_button = False

        # Speed
        self.vx, self.vy = 0, 0
        self.walk_speed = SPEED_WALK
        self.jump_speed = SPEED_JUMP
        self.gravity = SPEED_GRAVITY

        self.instances.add(self)
    
    def wall(self, dx: int, dy: int) -> list[int]:
        """
        壁との衝突判定と位置調整を行う\n
        引数: dx, dy: プレイヤーが移動しようとした量
        """
        # x方向の衝突判定
        is_collide = False

        self.rect.x += dx
        hit_blocks = pg.sprite.spritecollide(self, Block.instances, False)
        hit_opt = pg.sprite.spritecollide(self, OptionalBlock.instances, False)
        hit_opt = [blk for blk in hit_opt if blk.visible]  # 可視状態のブロックだけ取り出す
        hit_blocks.extend(hit_opt)
        hit_blocks.extend(pg.sprite.spritecollide(self, Switch_Button.instances, False))
        hit_players = pg.sprite.spritecollide(self, Player.instances, False)
        hit_players.remove(self)  # 自分自身を除外

        # ブロックとの衝突
        for block in hit_blocks:
            if dx > 0:
                self.rect.right = block.rect.left
                is_collide = True
            elif dx < 0:
                self.rect.left = block.rect.right
                is_collide = True
            self.vx = 0
        
        # 他のプレイヤーとの衝突
        for player in hit_players:
            if dx > 0:
                self.rect.right = player.rect.left
                is_collide = True
            elif dx < 0:
                self.rect.left = player.rect.right
                is_collide = True
            self.vx = 0

        self.rect.y += dy
        hit_blocks = pg.sprite.spritecollide(self, Block.instances, False)
        hit_button = pg.sprite.spritecollide(self, Switch_Button.instances, False)
        hit_opt = pg.sprite.spritecollide(self, OptionalBlock.instances, False)
        hit_opt = [blk for blk in hit_opt if blk.visible]  # 可視状態のブロックだけ取り出す
        hit_blocks.extend(hit_opt)
        hit_blocks.extend(hit_button)
        hit_players = pg.sprite.spritecollide(self, Player.instances, False)
        hit_players.remove(self)  # 自分自身を除外

        if not hit_button:
            self.is_on_button = False

        # ブロックとの衝突
        for block in hit_blocks:
            if dy > 0:
                self.rect.bottom = block.rect.top
                self.is_jumping = False
                self.is_ground = True
                is_collide = True
            elif dy < 0:
                self.rect.top = block.rect.bottom
                is_collide = True
            self.vy = 0

            if block in hit_button:
                if not self.is_on_button:
                    if block.state == "ON":
                        block.state = "OFF"
                    elif block.state == "OFF":
                        block.state = "ON"

                    block.image = pg.image.load(f"fig/{block.state}.png")
                    for opt_blk in OptionalBlock.instances:
                        opt_blk.visible = not opt_blk.visible
                        if opt_blk.visible:  # 可視状態
                            opt_blk.image.fill((255,0,0))
                        else:  # 不可視
                            opt_blk.image.fill((255,255,255))

                    self.is_on_button = True
        
        # 他のプレイヤーとの衝突
        for player in hit_players:
            if dy > 0:
                self.rect.bottom = player.rect.top
                self.is_jumping = False
                self.is_ground = True
                is_collide = True
            elif dy < 0:
                self.rect.top = player.rect.bottom
                is_collide = True
            self.vy = 0
        
        if not is_collide:
            self.is_ground = False

        self.true_pos[0] += self.vx
        self.true_pos[1] += self.vy

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        キーボード操作, 画面への表示
        """
        if key_lst is not None:
            if key_lst[pg.K_a]:
                self.vx = self.delta[pg.K_a] * self.walk_speed
            elif key_lst[pg.K_d]:
                self.vx = self.delta[pg.K_d] * self.walk_speed
            else:
                self.vx = 0
        
        if self.is_jumping:
            self.vy += self.gravity
            self.is_ground = False

        self.wall(self.vx, self.vy)
        screen.blit(self.image, self.rect)