import pygame as pg
from Block import Block
from Turret import Turret
from Spike import Spike
from Spring import Spring
from Goal import Goal
from Key import Key
from OptionalBlock import OptionalBlock
from Switch_Button import Switch_Button
from Wind import Wind
from const import SPEED_WALK, SPEED_JUMP, SPEED_GRAVITY, WIDTH


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

        # Goal
        self.font = pg.font.Font(None, 60)
        self.key_image = pg.image.load("fig/key.png")
        self.key_rect = self.key_image.get_rect()
        self.key_rect.centerx = WIDTH - 100
        self.key_rect.centery = 100
        self.show_goal = False  # ゴール表示フラグ
        self.has_key = False  # 鍵取得フラグ

        # Flags
        self.is_alive = True
        self.is_ground = True
        self.is_jumping = True
        self.is_on_turret = False
        self.is_on_button = False

        # Speed
        self.vx, self.vy = 0, 0
        self.walk_speed = SPEED_WALK
        self.jump_speed = SPEED_JUMP
        self.gravity = SPEED_GRAVITY

        self.instances.add(self)
    
    def wall(self, dx: int, dy: int, screen: pg.Surface) -> list[int]:
        """
        壁との衝突判定と位置調整を行う\n
        引数: dx, dy: プレイヤーが移動しようとした量
        """
        # x方向の衝突判定
        is_collide = False

        self.rect.x += dx
        collides_x = get_collision_sprites(self)

        # 鍵
        if collides_x["key"]:
            self.has_key = True
            for key in collides_x["key"]:
                key.image.fill((255,255,255))
                key.image.set_colorkey((255, 255, 255))

        # ゴール
        if collides_x["goal"] and self.has_key:
            self.show_goal = True

        # ブロックとの衝突
        for block in collides_x["blocks"]:
            is_collide = True
            if dx > 0:
                self.rect.right = block.rect.left
            elif dx < 0:
                self.rect.left = block.rect.right
            self.vx = 0
            self.is_on_turret = False
        
        # 他のプレイヤーとの衝突
        for player in collides_x["player"]:
            is_collide = True
            if dx > 0:
                self.rect.right = player.rect.left
            elif dx < 0:
                self.rect.left = player.rect.right
            self.vx = 0
            self.is_on_turret = False

        # y方向の衝突判定
        self.rect.y += dy
        collides_y = get_collision_sprites(self)

        # ボタンに触れているか
        if not collides_y["button"]:
            self.is_on_button = False
        
        # 鍵
        if collides_y["key"]:
            self.has_key = True
            for key in collides_y["key"]:
                key.image.fill((255,255,255))
                key.image.set_colorkey((255, 255, 255))

        # ゴール
        if collides_y["goal"] and self.has_key:
            self.show_goal = True

        # ブロックとの衝突
        for block in collides_y["blocks"]:
            is_collide = True
            if dy > 0:
                self.rect.bottom = block.rect.top
                self.is_jumping = False
                self.is_ground = True
                self.is_on_turret = False
            elif dy < 0:
                self.rect.top = block.rect.bottom
            self.vy = 0

            # 砲台
            if block in collides_y["turret"]:
                self.is_on_turret = True
                if dy > 0:  # 上から衝突
                    for turret in collides_y["turret"]:
                        self.vx = turret.vx
                        self.vy = turret.vy

            # トゲ
            if block in collides_y["spike"]:
                self.is_alive = False

            # スイッチに触れたとき
            if block in collides_y["button"]:
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
        for player in collides_y["player"]:
            is_collide = True
            if dy > 0:
                self.rect.bottom = player.rect.top
                self.is_jumping = False
                self.is_ground = True
                self.is_on_turret = False
            elif dy < 0:
                self.rect.top = player.rect.bottom
            self.vy = 0
        
        # ばね
        if collides_y["spring"]:
            for spring in collides_y["spring"]:
                self.vy = spring.vy
        
        if not is_collide:
            self.is_ground = False

        self.true_pos[0] += self.vx
        self.true_pos[1] += self.vy

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        キーボード操作, 画面への表示
        """
        if key_lst is not None and not self.is_on_turret:
            if key_lst[pg.K_a]:
                self.vx = self.delta[pg.K_a] * self.walk_speed
            elif key_lst[pg.K_d]:
                self.vx = self.delta[pg.K_d] * self.walk_speed
            else:
                self.vx = 0
        
        if self.is_jumping:
            self.vy += self.gravity
            self.is_ground = False

        self.wall(self.vx, self.vy, screen)
        screen.blit(self.image, self.rect)

        # 鍵取得していれば右上に表示
        if self.has_key:
            screen.blit(self.key_image, self.key_rect)


def get_collision_sprites(player: Player) -> dict[str, list]:
    """
    playerと衝突したすべてのspriteを得る関数\n
    引数: playerインスタンス\n
    戻り値: dict[sprite名, spritecollide]
    """
    result = {
        "block": pg.sprite.spritecollide(player, Block.instances, False),
        "blocks": pg.sprite.spritecollide(player, Block.instances, False),
        "button": pg.sprite.spritecollide(player, Switch_Button.instances, False),
        "goal": pg.sprite.spritecollide(player, Goal.instances, False),
        "key": pg.sprite.spritecollide(player, Key.instances, False),
        "opt": pg.sprite.spritecollide(player, OptionalBlock.instances, False),
        "player": pg.sprite.spritecollide(player, Player.instances, False),
        "spike": pg.sprite.spritecollide(player, Spike.instances, False),
        "spring": pg.sprite.spritecollide(player, Spring.instances, False),
        "turret": pg.sprite.spritecollide(player, Turret.instances, False),
        "wind": pg.sprite.spritecollide(player, Wind.instances, False),
    }

    result["opt"] = [opt for opt in result["opt"] if opt.visible]
    result["player"].remove(player)
    result["blocks"].extend(result["button"])
    result["blocks"].extend(result["opt"])
    result["blocks"].extend(result["spike"])
    result["blocks"].extend(result["spring"])
    result["blocks"].extend(result["turret"])

    return result


def game_over(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示、状態を初期化する関数\n
    引数: screen: 描画先のSurface
    """
    # 更新するsprite
    render = pg.sprite.RenderUpdates()
    render.add(Block.instances, Wind.instances, Turret.instances, 
            Spike.instances, Spring.instances, OptionalBlock.instances,
            Switch_Button.instances, Key.instances, Goal.instances)

    # テキストの設定
    font = pg.font.Font(None, 74)
    text = font.render("Game Over", True, (255, 0, 0))
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

    # 位置情報と状態の初期化
    for player in Player.instances:
        player.vx, player.vy = 0, 0
        player.is_jumping = False
        player.is_ground = True
        player.rect.x, player.rect.y = player.initial_pos
        player.true_pos = [player.rect.x, player.rect.y]

    render.update(doReset=True)

def goal(screen: pg.Surface) -> None:
    """
    ゴール画面を表示、状態を初期化する関数\n
    引数: screen: 描画先のSurface
    """
    # 更新するsprite
    render = pg.sprite.RenderUpdates()
    render.add(Block.instances, Wind.instances, Turret.instances, 
            Spike.instances, Spring.instances, OptionalBlock.instances,
            Switch_Button.instances, Key.instances, Goal.instances)
    
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

    # 位置情報と状態の初期化
    for player in Player.instances:
        player.vx, player.vy = 0, 0
        player.is_jumping = False
        player.is_ground = True
        player.rect.x, player.rect.y = player.initial_pos
        player.true_pos = [player.rect.x, player.rect.y]

    render.update(doReset=True)