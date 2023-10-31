import sys
import pygame as pg

def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((600, 600))
    clock  = pg.time.Clock()
    bg_img = pg.image.load("ex05/fig/background.png")
    bg_fimg = pg.transform.flip(bg_img, True, False)


    tmr = 0
    x = 0
    count = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: return

        screen.blit(bg_img, [0, 0])
        pg.display.update()
        tmr += 1
        x += 1
        clock.tick(100)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
