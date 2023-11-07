import sys
import pygame as pg
from pygame.sprite import Group
import random
import time
import math

# ウィンドウサイズの定数
WIDTH = 600
HEIGHT = 600

# 小球のスピードとサイズの定数
BALL_SPEED =15
BALL_SIZE = 15
BALLS_NUMBER = 12  # 小球の数


def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，戦車，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


# SpiralBall クラス
class SpiralBall(pg.sprite.Sprite):
    def __init__(self, center, angle_offset):
        super().__init__()
        self.image = pg.Surface((BALL_SIZE * 2, BALL_SIZE * 2), pg.SRCALPHA)
        pg.draw.circle(self.image, pg.Color('dodgerblue'), (BALL_SIZE, BALL_SIZE), BALL_SIZE)
        self.rect = self.image.get_rect(center=center)
        self.radius = 0
        self.angle = angle_offset
        self.center = center

    def update(self):
        self.radius += BALL_SPEED / 10
        angular_velocity = BALL_SPEED + self.radius / 50
        self.angle += math.radians(angular_velocity)
        self.rect.x = WIDTH // 2 + self.radius * math.cos(self.angle) - WIDTH // 2 + self.center[0]
        self.rect.y = HEIGHT // 2 + self.radius * math.sin(self.angle) - HEIGHT // 2 + self.center[1]
        # if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
        #     self.kill()

# SpiralBall を生成する関数
def add_spiral_balls(group, center):
    for i in range(BALLS_NUMBER):
        angle_offset = i * (360 / BALLS_NUMBER)
        group.add(SpiralBall(center, math.radians(angle_offset)))

# Enemy クラス
class Enemy(pg.sprite.Sprite):
    imgs = [pg.image.load(f"ex05/fig/alien{i}.png") for i in range(1, 3)]

    def __init__(self, all_sprites_group):
        super().__init__()
        self.image = random.choice(Enemy.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, 200)
        self.state = "down"
        self.interaval = random.randint(50, 300)
        self.created_time = time.time()
        self.all_sprites_group = all_sprites_group
        self.balls = pg.sprite.Group()

    def update(self):
        if self.rect.centery > self.bound and self.state == "down":
            self.vy = 0
            self.state = "stop"
            self.add_spiral_balls()  # 小球を生成する関数を呼び出す
        self.rect.centery += self.vy
        if time.time() - self.created_time > 5:
            self.reset()

    def add_spiral_balls(self):
        # このエネミーの中心から小球を生成する
        for i in range(BALLS_NUMBER):
            angle_offset = i * (360 / BALLS_NUMBER)
            ball = SpiralBall(self.rect.center, math.radians(angle_offset))
            self.balls.add(ball)  # 小球を自身のグループに追加
            self.all_sprites_group.add(ball)  # 画面に表示するための全体のグループにも追加

    def reset(self):
        for ball in self.balls:
            ball.kill()
        self.balls.empty()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, 200)
        self.state = "down"
        self.created_time = time.time()


class Tank(pg.sprite.Sprite):
    def __init__(self, x, y, image_path):
        super().__init__()
        self.image = pg.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def move_left(self, distance, min_x):
        self.rect.x -= distance
        if self.rect.x < min_x:
            self.rect.x = min_x

    def move_right(self, distance, max_x):
        self.rect.x += distance
        if self.rect.x > max_x - self.rect.width:
            self.rect.x = max_x - self.rect.width

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, tank: Tank, angle: float):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centerx = tank.rect.centerx
        self.rect.centery = tank.rect.y
        self.speed = 10



    def update(self):
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        # self.rect.x += self.vx * self.speed
        # self.rect.y += self.vy * self.speed
        # 画面外に出たらビームをリセットする
        if not check_bound(self.rect)[1]:  # 縦方向のチェック
            self.kill()  # Sprite グループからこの Sprite を削除


class Obstacle(pg.sprite.Sprite):  # pg.sprite.Sprite を継承する
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((126, 126, 126))  # 障害物の色を灰色に設定
        self.rect = self.image.get_rect(topleft=(x, y))
        self.durability = 20  # 耐久値を設定
        self.created_time = time.time()

    def is_expired(self, duration):
        '''
        障害物が duration 秒経過したかどうかを返す
        '''
        return time.time() - self.created_time > duration

    def hit(self):
        """
        障害物がヒットした時に耐久値を減少させる
        """
        self.durability -= 1
        if self.durability <= 0:
            self.kill()  # 耐久値が0以下になったら障害物を消去

class Score:
    """
    撃ち落とした爆弾、敵機の数をスコアとして表示するクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.score = 0
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def score_up(self, add):
        self.score += add

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.image, self.rect)

class Shield(pg.sprite.Sprite):
    """
    tabキーを押すと重力バリアが発動する
    """
    def __init__(self, tank:Tank,  size: int ,life: int):
        super().__init__()
        self.tank = tank
        self.image = pg.Surface((2*size, 2*size))
        self.image.set_alpha(50)
        pg.draw.circle(self.image, (1, 0, 0), (size, size), size)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = self.tank.rect.x + self.tank.image.get_width() / 2
        self.rect.centery = self.tank.rect.y
        self.life = life

    def update(self):
        """
        発動してからlifeがゼロになるまで発動し、ゼロになったらkillされる
        """
        self.rect.centerx = self.tank.rect.x + self.tank.image.get_width() / 2
        self.rect.centery = self.tank.rect.y
        self.life -= 1
        if self.life < 0:
            self.kill()


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Spiral Ball Animation")
    clock = pg.time.Clock()
    bg_img = pg.image.load("ex05/fig/background.png")
    tank = Tank(300, 500, "ex05/fig/player1.gif")
    beams = Group()
    emys = Group()
    all_sprites = Group()
    shields = Group()
    score = Score()
    obstacles = []  # 障害物のリスト
    obstacles = pg.sprite.Group()

    next_obstacle_time = time.time() + random.randint(1, 3)  # 障害物を生成する時刻

    frame_count = 0

    while True:
        screen.blit(bg_img, [0, 0])  # 背景画像を最初に描画
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            tank.move_left(10, 0)  # 左に移動
        if keys[pg.K_d]:
            tank.move_right(10, WIDTH)  # 右に移動

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_TAB :
                shields.add(Shield(tank, 100, 300))

        if len(emys) < 5:  # emys グループ内の Enemy インスタンスの数が5未満の場合に Enemy を追加
            emys.add(Enemy(all_sprites))


        if frame_count % 10 == 0:  # ビーム自動発射
            beams.add(Beam(tank, angle=90))

        # 障害物を生成
        if time.time() > next_obstacle_time and len(obstacles) < 3:
            obstacle = Obstacle(random.randint(0, WIDTH-100), random.randint(200, 400), 100, 20)
            obstacles.add(obstacle)
            next_obstacle_time = time.time() + random.randint(1, 3)

        # 障害物の更新と描画
        for obstacle in obstacles:
            obstacle.update()
        obstacles.draw(screen)

        frame_count += 1
        tank.draw(screen)
        all_sprites.update()
        beams.update()
        emys.update()
        shields.update()

        # シールドと小球の衝突判定
        pg.sprite.groupcollide(shields, all_sprites, False, True)

        # ビームと小球の衝突判定
        collisions = pg.sprite.groupcollide(beams, all_sprites, True, True)

        # ビームとエネミーの衝突判定
        beam_enemy_collisions = pg.sprite.groupcollide(beams, emys, True, True) and score.score_up(1)

        # 障害物と小球の衝突判定
        for obstacle in obstacles:
            hits = pg.sprite.spritecollide(obstacle, all_sprites, False)  # 障害物に当たった小球を検出
            for hit in hits:
                obstacle.hit()  # 障害物の耐久値を減少させる
                hit.kill()  # 当たった小球を消去

        # タンクと小球の衝突判定
        tank_hit_list = pg.sprite.spritecollide(tank, all_sprites, False)
        if tank_hit_list:
            print("Game Over")
            pg.quit()
            sys.exit()

        score.update(screen)
        all_sprites.draw(screen)
        beams.draw(screen)
        emys.draw(screen)
        shields.draw(screen)
        pg.display.flip()
        clock.tick(100)


if __name__ == "__main__":
    main()
