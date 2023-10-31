import sys
import pygame as pg

def main():
    pg.display.set_caption("弾幕ゲー")
    screen = pg.display.set_mode((600, 600))
    clock = pg.time.Clock()

    bg_img = pg.image.load("ex05/fig/background.png")
    tank_img = pg.image.load("ex05/fig/player1.gif")

    tmr = 0
    x = 300  # タンクの初期 x 座標
    y = 500  # タンクの初期 y 座標

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

        pg.display.update()
        tmr += 1
        clock.tick(100)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
