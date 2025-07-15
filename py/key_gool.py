class Player(pg.sprite.Sprite):
    """
    プレイヤーに関するクラス
    """
    delta = {
        pg.K_a: -1,
        pg.K_d: +1,
    }

    def __init__(self, center: tuple[int, int], blocks: pg.sprite.Group, goals: pg.sprite.Group, keys: pg.sprite.Group):
        """
        初期位置などを決める
        """
        super().__init__()
        # Surface
        img_path = "fig/test.gif"
        self.image = pg.image.load(img_path)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.blocks = blocks
        self.goals = goals  # ゴールブロック参照用
        self.keys = keys  # 鍵ブロック参照用
        self.font = pg.font.SysFont(None, 60)
        self.show_goal = False  # ゴール表示フラグ
        self.has_key = False  # 鍵取得フラグ

        # 鍵画像
        key_img_path = "fig/key.png"
        self.key_image = pg.image.load(key_img_path)
        self.key_rect = self.key_image.get_rect(topleft=(WIDTH - 70, 10))

        # Flags
        self.is_ground = True
        self.is_jumping = True

        # Speed
        self.vx, self.vy = 0, 0
        self.walk_speed = SPEED_WALK
        self.jump_speed = SPEED_JUMP
        self.gravity = SPEED_GRAVITY

    def get_image(self):
        """
        プレイヤーの画像Surfaceを返す
        """
        return self.image

    def get_rect(self):
        """
        プレイヤーの矩形情報を返す
        """
        return self.rect

    def get_has_key(self):
        """
        鍵を持っているかどうかを返す
        """
        return self.has_key

    def get_show_goal(self):
        """
        ゴールに到達したかどうかを返す
        """
        return self.show_goal

    def wall(self, dx: int, dy: int) -> list[int]:
        """
        壁との衝突判定と位置調整を行う
        引数: dx, dy: プレイヤーが移動しようとした量
        """
        self.rect.x += dx
        hit_blocks = pg.sprite.spritecollide(self, self.blocks, False)
        for block in hit_blocks:
            if dx > 0:
                self.rect.right = block.rect.left
            elif dx < 0:
                self.rect.left = block.rect.right
            self.vx = 0
        
        self.rect.y += dy
        hit_blocks = pg.sprite.spritecollide(self, self.blocks, False)
        for block in hit_blocks:
            if dy > 0:
                self.rect.bottom = block.rect.top
                self.is_jumping = False
                self.is_ground = True
            elif dy < 0:
                self.rect.top = block.rect.bottom
            self.vy = 0

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        画面に表示する
        """
        self.vx = 0
        if key_lst[pg.K_a]:
            self.vx = self.delta[pg.K_a] * self.walk_speed
        if key_lst[pg.K_d]:
            self.vx = self.delta[pg.K_d] * self.walk_speed
        
        if self.is_jumping:
            self.vy += self.gravity
            self.is_ground = False

        self.wall(self.vx, self.vy)
        screen.blit(self.image, self.rect)

        # 鍵に触れたかチェック
        if not self.has_key and pg.sprite.spritecollide(self, self.keys, True):
            self.has_key = True

        # ゴールに触れたか判定（鍵を持っていないと無効）
        if self.has_key and pg.sprite.spritecollide(self, self.goals, False):
            self.show_goal = True
        
        # ゴールに触れたら表示
        if self.show_goal:
            text = self.font.render("gool", True, (255, 0, 0))
            screen.blit(text, (WIDTH // 2 - 50, HEIGHT // 4))

        # 鍵取得していれば右上に表示
        if self.has_key:
            screen.blit(self.key_image, self.key_rect)


class Block(pg.sprite.Sprite):
    """
    壁・地面に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rect: tuple[int]):
        """
        ブロックの色, 座標の設定
        """
        super().__init__()
        self.image = pg.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
        self.image.fill(color)  # 色設定
        self.rect = self.image.get_rect()
        self.rect.topleft = rect[:2]
        self.rect.bottomright = rect[2:]
    
    def update(self, vx: int = 0):
        self.rect.x += vx


class GoalBlock(pg.sprite.Sprite):
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        img_path = "fig/gool.png"
        self.image = pg.image.load(img_path)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
    def update(self, vx: int = 0):
        self.rect.x += vx


class KeyBlock(pg.sprite.Sprite):
    """
    鍵ブロックに関するクラス
    """
    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        img_path = "fig/key.png"
        self.image = pg.image.load(img_path)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self, vx: int = 0):
        self.rect.x += vx


def map_loading(filename: str) -> tuple[pg.sprite.Group, pg.sprite.Group, pg.sprite.Group]:
    # マップファイルの読み込み
    filepath = filename  # 相対パスのままでOK

    with open(filepath, "r", encoding="UTF-8") as f:
        data = [row.strip() for row in f]

    blocks = pg.sprite.Group()
    goals = pg.sprite.Group()
    keys = pg.sprite.Group()

    for i, row in enumerate(data):
        for j, char in enumerate(row):
            x = BLOCK_WIDTH * j
            y = BLOCK_HEIGHT * i
            if char == "1":
                blocks.add(Block((225, 150, 0), (x, y, x + BLOCK_WIDTH, y + BLOCK_HEIGHT)))
            elif char == "9":
                goals.add(GoalBlock((x, y)))
            elif char == "8":
                keys.add(KeyBlock((x, y)))
    
    return blocks, goals, keys


def main():
    pg.display.set_caption("Test")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    #インスタンス生成
    blocks, goals, keys = map_loading("map/stage1.txt")
    player = Player((150, HEIGHT - 150), blocks, goals, keys)
    half_screen = WIDTH // 2

    #時間計測用
    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE and not player.is_jumping:
                    player.is_jumping = True
                    player.vy = player.jump_speed
        
        # Clear Screen
        screen.fill((255, 255, 255))

        # なにかの処理
        player.vy += player.gravity        

        # Update
        if player.get_rect().x > half_screen:
            blocks.update(-player.vx) 
            goals.update(-player.vx)  # ゴールも一緒にスクロール
            keys.update(-player.vx)   # 鍵もスクロール
        else:
            blocks.update()
            goals.update()
            keys.update()
        blocks.draw(screen)
        goals.draw(screen)  # ゴールの描画
        keys.draw(screen)   # 鍵の描画
        player.update(key_lst, screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()