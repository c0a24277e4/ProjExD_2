import os
import random
import sys
import pygame as pg
import time


WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))
DELTA = {
    pg.K_UP:(0, -5),
    pg.K_DOWN:(0, +5),
    pg.K_LEFT:(-5, 0),
    pg.K_RIGHT:(+5, 0)
}


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectまたは爆弾Rect
    戻り値：判定結果タプル（横方向、縦方向）
    画面内ならTrue, 画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right: #横はみだしチェック
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: #縦はみだしチェック
        tate = False
    return yoko, tate


def game_over(screen: pg.Surface) -> None:
    """
    画面を暗転し，泣いているこうかとんとGame Overを5秒表示する
    """
    #黒い矩形のSurfaceを作成
    black_surf = pg.Surface((WIDTH, HEIGHT))
    black_surf.fill((0, 0, 0))
    black_surf.set_alpha(150)  # 半透明

    #まず画面に暗転レイヤーをblit
    screen.blit(black_surf, (0, 0))

    #Game Over文字を作成
    font = pg.font.Font(None, 80)
    txt_surf = font.render("Game Over", True, (255, 255, 255))
    txt_rect = txt_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))

    #泣いているこうかとん画像のロード
    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.5)
    cry_left_rect = cry_img.get_rect(center=(txt_rect.left - 50, txt_rect.centery))
    cry_right_rect = cry_img.get_rect(center=(txt_rect.right + 50, txt_rect.centery))

    #黒いSurfaceに文字と画像をblit
    screen.blit(txt_surf, txt_rect)
    screen.blit(cry_img, cry_left_rect)
    screen.blit(cry_img, cry_right_rect)

    pg.display.update()
    time.sleep(5)


#爆弾の画像リスト & 加速度リスト作成関数
def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]

    for r in range(1, 11):  # 1〜10段階
        size = 20 * r
        bb_img = pg.Surface((size, size))
        pg.draw.circle(bb_img, (255, 0, 0), (size//2, size//2), size//2)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)

    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """移動量タプル → こうかとん画像 を返す辞書を作成"""
    base_img = pg.image.load("fig/3.png")

    kk_imgs = {}

    # 8方向分の角度指定
    angle_map = {
        (0, 0): 0,        # 静止
        (+5, 0): -90,     # 右
        (+5, -5): -45,    # 右上
        (0, -5): 0,       # 上
        (-5, -5): 45,     # 左上
        (-5, 0): 90,      # 左
        (-5, +5): 135,    # 左下
        (0, +5): 180,     # 下
        (+5, +5): -135    # 右下
    }

    for mv, ang in angle_map.items():
        kk_imgs[mv] = pg.transform.rotozoom(base_img, ang, 0.9)

    return kk_imgs

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20)) #空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10) #半径10の赤い円を描画
    bb_img.set_colorkey((0, 0, 0)) #黒色の透過色の背景
    bb_rct = bb_img.get_rect() #爆弾rect
    bb_rct.centerx = random.randint(0, WIDTH) #爆弾横座標
    bb_rct.centery = random.randint(0, HEIGHT) #爆弾縦座標
    vx, vy = +5, +5 # 爆弾の横速度，縦速度
    
    # while文の前に呼び出してSurfaceリストと加速度リストを取得
    bb_imgs, bb_accs = init_bb_imgs()
    
    kk_imgs = get_kk_imgs()

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        if kk_rct.colliderect(bb_rct): #こうかとんと爆弾が衝突したら
            game_over(screen)
            return
        
        screen.blit(bg_img, [0, 0]) 
        screen.blit(bb_img, bb_rct)
        
        
        # tmrはフレームタイマーなど
        idx = min(tmr // 500, 9)  # 0～9でSurfaceと加速度を選択
        bb_img = bb_imgs[idx]
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]

        # 爆弾Rectのサイズ更新
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        # 移動
        bb_rct.move_ip(avx, avy)

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        
        for key, mv  in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0] #横方向の移動量
                sum_mv[1] += mv[1] #縦方向の移動量 
        
        
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True): #画面外なら
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1]) #移動を無かったことにする
            
            
        screen.blit(kk_img, kk_rct)
        
        #爆弾の成長＆加速
        idx = min(tmr // 500, 9)  # 段階 0〜9
        bb_img = bb_imgs[idx]
        
        # サイズ更新
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        # 加速
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_rct.move_ip(avx, avy)
        
        # 反射        
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1 #横方向にはみ出てたら
        if not tate:
            vy *= -1 #縦方向にはみ出たら
        bb_rct.move_ip(vx, vy)
        
        # sum_mv をタプル化 → その方向のこうかとん画像に差し替え
        kk_img = kk_imgs.get((sum_mv[0], sum_mv[1]), kk_imgs[(0, 0)])
        screen.blit(kk_img, kk_rct)

        
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
