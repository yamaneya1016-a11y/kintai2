import sys
from PIL import Image, ImageDraw, ImageFont

RED   = (206, 8, 14)
BLACK = (34, 32, 32)
WHITE = (252, 252, 250)
HERO_BG = (248, 246, 245)

def fit_size(font_path, text, max_w=None, max_h=None, start=200, small=8):
    s = start
    while s > small:
        f = ImageFont.truetype(font_path, s)
        l, t, r, b = f.getbbox(text)
        w, h = r - l, b - t
        if (max_w is None or w <= max_w) and (max_h is None or h <= max_h):
            return s
        s -= 2
    return small

def draw_centered_v(draw, xy_center, text, font, fill, stroke_w=0, stroke_fill=None, anchor_left=None):
    # xy_center: (cx, cy). draw so glyph bbox centered vertically at cy; horizontally centered at cx unless anchor_left given
    l, t, r, b = font.getbbox(text)
    w, h = r - l, b - t
    cx, cy = xy_center
    x = anchor_left if anchor_left is not None else cx - w / 2
    px = x - l
    py = cy - h / 2 - t
    draw.text((px, py), text, font=font, fill=fill,
              stroke_width=stroke_w, stroke_fill=stroke_fill)
    return x, x + w  # return actual left/right

def make(symptom, font_path, out):
    im = Image.open('orig.png').convert('RGB')
    d = ImageDraw.Draw(im)
    px = im.load()

    # ---------- HERO line1: symptom(red) + の(black) ----------
    d.rectangle([286, 338, 838, 528], fill=HERO_BG)
    # symptom size: cap height target 150, but width <= 430
    s = fit_size(font_path, symptom, max_w=430, max_h=152, start=180)
    fbig = ImageFont.truetype(font_path, s)
    left = 302
    l, t, r, b = fbig.getbbox(symptom)
    sym_w = r - l
    stroke = max(3, int(s * 0.05))
    # draw white halo + red, center vertically at 430
    _, sym_right = draw_centered_v(d, (None, 430), symptom, fbig, RED,
                                   stroke_w=stroke, stroke_fill=(255, 255, 255),
                                   anchor_left=left)
    # の (black), smaller
    sn = int(s * 0.55)
    fno = ImageFont.truetype(font_path, sn)
    gap = int(s * 0.10)
    draw_centered_v(d, (None, 442), "の", fno, BLACK, anchor_left=sym_right + gap)

    # ---------- HEADER ----------
    # rebuild green background by tiling a clean green row (y=166) over text band
    band_top, band_bot = 50, 163
    src_row = 166
    for y in range(band_top, band_bot):
        for x in range(292, 1059):
            im.putpixel((x, y), px[x, src_row])
    header_txt = symptom + "の方限定の特別価格！"
    # tokens (text, is_small)
    toks = [(symptom, False), ("の", True), ("方限定", False),
            ("の", True), ("特別価格", False), ("！", False)]
    # choose big size to fit total width <= 748, cap height ~78
    big = 92
    while big > 20:
        fb = ImageFont.truetype(font_path, big)
        fs = ImageFont.truetype(font_path, int(big * 0.74))
        total = 0
        for txt, sm in toks:
            f = fs if sm else fb
            l, t, r, b = f.getbbox(txt)
            total += (r - l)
        total += int(big * 0.02) * (len(toks) - 1)
        if total <= 748:
            break
        big -= 2
    fb = ImageFont.truetype(font_path, big)
    fs = ImageFont.truetype(font_path, int(big * 0.74))
    x = 302
    cy = 101
    for txt, sm in toks:
        f = fs if sm else fb
        l, t, r, b = f.getbbox(txt)
        h = b - t
        py = cy - h / 2 - t
        # subtle shadow
        d.text((x - l + 2, py + 2), txt, font=f, fill=(0, 40, 12))
        d.text((x - l, py), txt, font=f, fill=WHITE)
        x += (r - l) + int(big * 0.02)

    # ---------- BOX label ----------
    d.rectangle([115, 983, 442, 1068], fill=(250, 250, 249))
    # redraw a clean box border rectangle
    d.rectangle([112, 981, 445, 1070], outline=(34, 32, 32), width=3)
    box_txt = symptom + "の方へ"
    bs = fit_size(font_path, box_txt, max_w=316, max_h=60, start=70)
    fbox = ImageFont.truetype(font_path, bs)
    draw_centered_v(d, (278, 1025), box_txt, fbox, BLACK)

    im.save(out)
    print("saved", out, "hero_size", s, "header_big", big, "box", bs)

if __name__ == "__main__":
    symptom = sys.argv[1]
    font = sys.argv[2]
    out = sys.argv[3]
    make(symptom, font, out)
