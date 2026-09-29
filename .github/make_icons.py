# Draws the Читанка home-screen icon: pastel open book with a red ribbon (no text, no finger).
# Outputs icons/apple-touch-icon.png, icon-192.png, icon-512.png, icon-maskable-512.png, favicon-32.png (site root)
from PIL import Image, ImageDraw, ImageFilter
import math, pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / 'icons'
OUT.mkdir(parents=True, exist_ok=True)
S = 1024
INK = (140, 88, 60)

def bez(p0, p1, p2, p3, n=60):
    pts = []
    for i in range(n + 1):
        t = i / n; a = (1-t)**3; b = 3*(1-t)**2*t; c = 3*(1-t)*t*t; d = t**3
        pts.append((a*p0[0]+b*p1[0]+c*p2[0]+d*p3[0], a*p0[1]+b*p1[1]+c*p2[1]+d*p3[1]))
    return pts

def draw(size, scale=1.0):
    W = size * 4
    img = Image.new('RGB', (W, W))
    px = img.load()
    top, bot = (255, 240, 222), (206, 226, 252)
    g = ImageDraw.Draw(img)
    for y in range(W):
        t = y / (W - 1)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        g.line([(0, y), (W, y)], fill=c)
    k = W / 1024.0
    def P(x, y):  # icon space 0..1024, scaled around centre
        return (512 + (x - 512) * scale) * k, (512 + (y - 512) * scale) * k
    # glow + rays
    l = Image.new('RGBA', img.size, (255, 214, 150, 0)); d = ImageDraw.Draw(l)
    cx, cy = P(512, 470)
    for r, a in [(440, 60), (330, 80), (230, 110)]:
        rr = r * k * scale
        d.ellipse([cx - rr, cy - rr * 0.8, cx + rr, cy + rr * 0.8], fill=(255, 214, 150, a))
    l = l.filter(ImageFilter.GaussianBlur(60 * k)); img.paste(l, (0, 0), l)
    l = Image.new('RGBA', img.size, (255, 200, 120, 0)); d = ImageDraw.Draw(l)
    for i in range(-5, 6):
        an = math.radians(-90 + i * 16)
        x2, y2 = P(512 + math.cos(an) * 520, 470 + math.sin(an) * 420)
        d.line([cx, cy, x2, y2], fill=(255, 200, 120, 90), width=int(14 * k * scale))
    l = l.filter(ImageFilter.GaussianBlur(10 * k)); img.paste(l, (0, 0), l)
    # shadow under the book
    l = Image.new('RGBA', img.size, (120, 80, 50, 0)); d = ImageDraw.Draw(l)
    a, b = P(170, 700); c, e = P(854, 780)
    d.ellipse([a, b, c, e], fill=(120, 80, 50, 90))
    l = l.filter(ImageFilter.GaussianBlur(26 * k)); img.paste(l, (0, 0), l)
    g = ImageDraw.Draw(img)
    lw = max(2, int(14 * k * scale))
    # cover (dark red-brown boards peeking out)
    cover = [P(150, 360), P(150, 720), P(512, 760), P(874, 720), P(874, 360), P(512, 400)]
    g.polygon(cover, fill=(196, 92, 70), outline=INK)
    g.line(cover + [cover[0]], fill=INK, width=lw, joint='curve')
    # page stacks
    for off, col in [(26, (238, 222, 196)), (14, (246, 234, 214))]:
        left = [P(512, 700 + off)] + [P(x, y) for x, y in bez((512, 700 + off), (420, 650 + off), (280, 640 + off), (176, 680 + off))] + [P(176, 330), P(512, 380)]
        right = [P(512, 700 + off)] + [P(x, y) for x, y in bez((512, 700 + off), (604, 650 + off), (744, 640 + off), (848, 680 + off))] + [P(848, 330), P(512, 380)]
        g.polygon(left, fill=col); g.polygon(right, fill=col)
    # main pages (curved from the spine)
    lp = [P(x, y) for x, y in bez((512, 330), (420, 250), (290, 250), (190, 300))] + \
         [P(x, y) for x, y in bez((190, 300), (192, 450), (190, 560), (190, 668))] + \
         [P(x, y) for x, y in bez((190, 668), (290, 620), (420, 624), (512, 700))]
    rp = [(1024 * k - x + (0 if scale == 1 else 0), y) for x, y in lp]
    g.polygon(lp, fill=(255, 251, 242)); g.polygon(rp, fill=(255, 251, 242))
    g.line(lp, fill=INK, width=lw, joint='curve'); g.line(rp, fill=INK, width=lw, joint='curve')
    # spine shading
    l = Image.new('RGBA', img.size, (200, 160, 120, 0)); d = ImageDraw.Draw(l)
    a, b = P(470, 330); c, e = P(554, 700)
    d.rectangle([a, b, c, e], fill=(200, 160, 120, 70))
    l = l.filter(ImageFilter.GaussianBlur(18 * k)); img.paste(l, (0, 0), l)
    g = ImageDraw.Draw(img)
    g.line([P(512, 332), P(512, 700)], fill=INK, width=max(2, lw // 2))
    # text lines
    lw2 = max(2, int(10 * k * scale))
    for i in range(6):
        y0 = 350 + i * 52
        ln = 0.78 if i == 5 else 1.0
        pts = [P(x, y) for x, y in bez((250, y0), (330, y0 - 22), (400, y0 - 18), (250 + (220 * ln), y0 + 6 - 20 * ln), 20)]
        g.line(pts, fill=(196, 170, 140), width=lw2)
        pts = [(1024 * k - x, y) for x, y in pts]
        g.line(pts, fill=(196, 170, 140), width=lw2)
    # ribbon
    rb = [P(530, 690), P(530, 850), P(556, 820), P(582, 850), P(582, 684)]
    g.polygon(rb, fill=(222, 70, 80), outline=(150, 40, 50))
    # sparkles
    for (sx, sy, r, col) in [(210, 190, 26, (255, 170, 60)), (820, 210, 30, (170, 130, 240)), (860, 470, 18, (255, 150, 170)), (170, 520, 16, (110, 190, 140))]:
        x, y = P(sx, sy); rr = r * k * scale
        g.polygon([(x, y - rr), (x + rr * 0.3, y - rr * 0.3), (x + rr, y), (x + rr * 0.3, y + rr * 0.3), (x, y + rr), (x - rr * 0.3, y + rr * 0.3), (x - rr, y), (x - rr * 0.3, y - rr * 0.3)], fill=col)
    return img.resize((size, size), Image.LANCZOS)

draw(180).save(OUT / 'apple-touch-icon.png')
draw(192).save(OUT / 'icon-192.png')
draw(512).save(OUT / 'icon-512.png')
draw(512, scale=0.78).save(OUT / 'icon-maskable-512.png')
draw(64).resize((32, 32), Image.LANCZOS).save(OUT / 'favicon-32.png')
print('icons ->', OUT)
