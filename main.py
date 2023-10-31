import sys
import pygame as pg
import random
import time

class Obstacle:
    def __init__(self, x, y, width, height):
        '''
        障害物を生成する
        '''
        self.rect = pg.Rect(x, y, width, height)
        self.created_time = time.time()

    def is_expired(self, duration):
        '''
        障害物が duration 秒経過したかどうかを返す
        '''
        return time.time() - self.created_time > duration

def main():
    pg.display.set_caption("弾幕ゲー")
    screen = pg.display.set_mode((600, 600))
    clock = pg.time.Clock()

    bg_img = pg.image.load("ex05/fig/background.png")
    tank_img = pg.image.load("ex05/fig/player1.gif")

    tmr = 0
    x = 300  # タンクの初期 x 座標
    y = 500  # タンクの初期 y 座標

    obstacles = [] # 障害物のリスト
    next_obstacle_time = time.time() + random.randint(1, 3) # 障害物を生成する時刻

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            x -= 10  # 左に移動
            if x < 0:  # 画面の左端を超えないように
                x = 0
        if keys[pg.K_d]:
            x += 10  # 右に移動
            if x > 600 - tank_img.get_width():
                x = 600 - tank_img.get_width()

        screen.blit(bg_img, [0, 0])
        screen.blit(tank_img, [x, y])

        # 障害物を生成
        if time.time() > next_obstacle_time and len(obstacles) < 5:
            obstacles.append(Obstacle(random.randint(0, 600), random.randint(200, 400), 100, 20))
            next_obstacle_time = time.time() + random.randint(1, 3) # 次の障害物を生成する時刻を更新

        # 障害物を描画
        for obstacle in obstacles[:]:
            pg.draw.rect(screen, (126, 126, 126), obstacle.rect)
            if obstacle.is_expired(15):
                obstacles.remove(obstacle)

        pg.display.update()
        tmr += 1
        clock.tick(100)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()