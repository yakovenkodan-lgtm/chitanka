# Draws the phone banner img/banner-phone.jpg: warm pastel hand-drawn-style open book (curved pages from the spine, page stack,
# turning pages, curl, ribbon), soft glow, sparkles, vines. No text, no people.
from PIL import Image, ImageDraw, ImageFilter
import math, random, pathlib
S = 4
W, H = 2400, 260
BG = (253, 246, 236)
INK = (150, 98, 70)
random.seed(7)
img = Image.new('RGB', (W * S, H * S), BG)

def bez(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n; a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t * t; d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out
def sc(pts): return [(x * S, y * S) for x, y in pts]
def jitter(pts, amt=0.6):
    return [(x + random.uniform(-amt, amt), y + random.uniform(-amt, amt)) for x, y in pts]
def layer(base=(255, 214, 150)):
    l = Image.new('RGBA', img.size, base + (0,)); return l, ImageDraw.Draw(l)
def paste(l, blur=0):
    global img
    if blur: l = l.filter(ImageFilter.GaussianBlur(blur * S))
    img.paste(l, (0, 0), l)

cx = W / 2
ty, by, bw = 84, 214, 320     # spine top / bottom, half width

# glow
l, g = layer()
for rx, ry, a in [(700, 150, 26), (520, 120, 40), (380, 95, 55)]:
    g.ellipse([(cx - rx) * S, (140 - ry) * S, (cx + rx) * S, (140 + ry) * S], fill=(255, 212, 150, a))
paste(l, 60)
# rays
l, g = layer()
for k in range(-7, 8):
    an = math.radians(-90 + k * 11)
    g.line([cx * S, 120 * S, (cx + math.cos(an) * 520) * S, (120 + math.sin(an) * 150) * S], fill=(255, 198, 120, 110), width=5 * S)
paste(l, 3)
# hills
d = ImageDraw.Draw(img)
def hill(y0, amp, period, col, phase):
    pts = [(0, H)] + [(x, y0 + amp * math.sin(x / period + phase)) for x in range(0, W + 1, 6)] + [(W, H)]
    d.polygon(sc(pts), fill=col)
hill(236, 7, 150, (230, 214, 250), 0.5)
hill(246, 6, 115, (205, 240, 212), 2.0)
hill(255, 4, 95, (205, 226, 255), 4.0)
# shadow under the book
l, g = layer((120, 80, 50))
g.ellipse([(cx - bw - 60) * S, (by - 4) * S, (cx + bw + 60) * S, (by + 34) * S], fill=(120, 80, 50, 90))
paste(l, 10)

def half(sgn, dy=0.0, dx=0.0, lift=0.0):
    """Page outline for one half: top curve from spine, outer edge, bottom curve back to spine."""
    o = cx + sgn * (bw + dx)
    top = bez((cx, ty + 10 + dy), (cx + sgn * bw * 0.22, ty - 26 + dy - lift), (cx + sgn * bw * 0.68, ty - 16 + dy - lift * 0.8), (o, ty + 4 + dy - lift * 0.4))
    bot = bez((cx, by + dy), (cx + sgn * bw * 0.25, by - 22 + dy - lift), (cx + sgn * bw * 0.72, by - 14 + dy - lift * 0.8), (o, by - 8 + dy - lift * 0.4))
    return top, bot

d = ImageDraw.Draw(img)
# hard cover
for sgn in (-1, 1):
    top, bot = half(sgn, dy=12, dx=16)
    poly = top + list(reversed(bot))
    d.polygon(sc(poly), fill=(206, 122, 92))
    d.line(sc(jitter(top + [bot[-1]] + list(reversed(bot)))), fill=(160, 84, 62), width=int(2.2 * S))
# page stack: several layers slightly lower / wider -> visible page edges
stack_cols = [(234, 214, 186), (240, 224, 200), (244, 231, 210), (248, 238, 220), (251, 244, 230)]
for k, col in zip(range(5, 0, -1), stack_cols):
    for sgn in (-1, 1):
        top, bot = half(sgn, dy=k * 2.0, dx=k * 2.0)
        d.polygon(sc(top + list(reversed(bot))), fill=col)
        d.line(sc(jitter(bot[8:] + [top[-1]], 0.4)), fill=(205, 170, 130), width=int(1.3 * S))
# top pages
pages = {}
for sgn in (-1, 1):
    top, bot = half(sgn)
    pages[sgn] = (top, bot)
    d.polygon(sc(top + list(reversed(bot))), fill=(255, 251, 242))
# gutter shading near the spine
l, g = layer((170, 120, 80))
for sgn in (-1, 1):
    top, bot = pages[sgn]
    for i, a in [(10, 26), (6, 34), (3, 44)]:
        poly = top[:i] + list(reversed(bot[:i]))
        g.polygon(sc(poly), fill=(170, 120, 80, a))
paste(l, 3)
d = ImageDraw.Draw(img)
# text-like wavy lines following the page curve
for sgn in (-1, 1):
    top, bot = pages[sgn]
    for j in range(8):
        f = 0.16 + j * 0.095
        seg = []
        for i in range(5, 37):
            x = top[i][0] + (bot[i][0] - top[i][0]) * f
            y = top[i][1] + (bot[i][1] - top[i][1]) * f
            seg.append((x, y))
        if j == 7: seg = seg[:18]
        d.line(sc(jitter(seg, 0.3)), fill=(208, 188, 160), width=int(2.2 * S))
# outlines of the top pages (hand drawn)
for sgn in (-1, 1):
    top, bot = pages[sgn]
    d.line(sc(jitter(top)), fill=INK, width=int(2.4 * S))
    d.line(sc(jitter([top[-1], bot[-1]])), fill=INK, width=int(2.2 * S))
    d.line(sc(jitter(bot)), fill=INK, width=int(2.4 * S))
# spine crease
d.line(sc(jitter(bez((cx, ty + 10), (cx - 1, ty + 60), (cx + 1, by - 60), (cx, by)), 0.4)), fill=(170, 120, 86), width=int(2.4 * S))
# two turning pages fanning up from the spine (right side)
for lift, alpha, ow in [(26, 225, 0.86), (10, 240, 0.93)]:
    top = bez((cx, ty + 10), (cx + bw * 0.18, ty - 28 - lift), (cx + bw * 0.55, ty - 30 - lift), (cx + bw * ow, ty - 4 - lift * 0.9))
    bot = bez((cx, by), (cx + bw * 0.22, by - 30 - lift), (cx + bw * 0.6, by - 30 - lift), (cx + bw * ow, by - 14 - lift * 0.9))
    l, g = layer((255, 252, 245))
    g.polygon(sc(top + list(reversed(bot))), fill=(255, 252, 245, alpha))
    paste(l)
    l, g = layer((190, 150, 110))   # soft shadow on the underside near the spine
    g.polygon(sc(top[:14] + list(reversed(bot[:14]))), fill=(190, 150, 110, 40))
    paste(l, 4)
    d = ImageDraw.Draw(img)
    d.line(sc(jitter(top)), fill=INK, width=int(2.0 * S))
    d.line(sc(jitter([top[-1], bot[-1]])), fill=INK, width=int(2.0 * S))
    d.line(sc(jitter(bot)), fill=INK, width=int(2.0 * S))
    if lift == 10:
        for j in range(7):
            f = 0.18 + j * 0.1
            seg = [(top[i][0] + (bot[i][0] - top[i][0]) * f, top[i][1] + (bot[i][1] - top[i][1]) * f) for i in range(6, 36)]
            if j == 6: seg = seg[:16]
            d.line(sc(jitter(seg, 0.3)), fill=(208, 188, 160), width=int(2.2 * S))
# page curl on the lower outer corner of the left page
top, bot = pages[-1]
c = bot[-1]
curl = [(c[0] + 2, c[1] - 30), (c[0] + 34, c[1] - 6), (c[0] + 6, c[1] + 1)]
d.polygon(sc([(c[0], c[1] - 30), (c[0] + 34, c[1] - 2), (c[0], c[1])]), fill=(236, 220, 196))
d.polygon(sc(curl), fill=(255, 247, 232))
d.line(sc(jitter(curl + [curl[0]], 0.3)), fill=INK, width=int(1.8 * S))
# ribbon bookmark from the spine
rib = bez((cx + 6, by - 4), (cx + 14, by + 16), (cx - 2, by + 26), (cx + 12, by + 40), 20)
ribL = [(x - 6, y) for x, y in rib]; ribR = [(x + 6, y) for x, y in rib]
end = rib[-1]
poly = ribL + [(end[0] - 6, end[1] + 6), (end[0], end[1] - 2), (end[0] + 6, end[1] + 6)] + list(reversed(ribR))
d.polygon(sc(poly), fill=(226, 96, 104))
d.line(sc(jitter(poly + [poly[0]], 0.3)), fill=(170, 60, 70), width=int(1.4 * S))

# sparkles
def star(x, y, r, col):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.33
        an = math.radians(k * 45 - 90)
        pts.append(((x + math.cos(an) * rr) * S, (y + math.sin(an) * rr) * S))
    d.polygon(pts, fill=col)
random.seed(11)
for _ in range(36):
    side = random.choice((-1, 1))
    star(cx + side * random.randint(430, 1130), random.randint(24, 190), random.randint(5, 11),
         random.choice([(255, 186, 90), (244, 150, 132), (176, 150, 232), (120, 186, 230)]))
# vines with leaves and flowers
def leaf(x, y, ang, L, col):
    a = math.radians(ang)
    tip = (x + math.cos(a) * L, y + math.sin(a) * L)
    n = (math.cos(a + math.pi / 2) * L * 0.33, math.sin(a + math.pi / 2) * L * 0.33)
    mid = ((x + tip[0]) / 2, (y + tip[1]) / 2)
    d.polygon(sc([(x, y), (mid[0] + n[0], mid[1] + n[1]), tip, (mid[0] - n[0], mid[1] - n[1])]), fill=col)
for side in (-1, 1):
    pts = [(cx + side * (470 + u / 100 * 640), 170 + 24 * math.sin(u / 100 * 7.0)) for u in range(101)]
    d.line(sc(pts), fill=(130, 180, 120), width=3 * S)
    for i in range(4, 100, 8):
        x, y = pts[i]
        leaf(x, y, (-60 if (i // 8) % 2 else 60) + (0 if side > 0 else 180), 22, (150, 204, 140))
    for i in range(12, 100, 24):
        x, y = pts[i]
        for k in range(5):
            an = math.radians(k * 72)
            d.ellipse(sc([(x + math.cos(an) * 7 - 5, y + math.sin(an) * 7 - 5), (x + math.cos(an) * 7 + 5, y + math.sin(an) * 7 + 5)]), fill=(246, 164, 150))
        d.ellipse(sc([(x - 4, y - 4), (x + 4, y + 4)]), fill=(255, 205, 100))
# fade edges
mask = Image.new('L', img.size, 0)
m = ImageDraw.Draw(mask)
fw = 260 * S
for i in range(fw):
    a = int(255 * i / fw)
    m.line([i, 0, i, H * S], fill=a); m.line([W * S - 1 - i, 0, W * S - 1 - i, H * S], fill=a)
m.rectangle([fw, 0, W * S - fw, H * S], fill=255)
img = Image.composite(img, Image.new('RGB', img.size, BG), mask)
out = img.resize((W, H), Image.LANCZOS)
# phone header: centre 900x260 -> 720x208 JPEG (small, sits behind the title at 72% opacity)
p = pathlib.Path(__file__).resolve().parent.parent / 'img' / 'banner-phone.jpg'
p.parent.mkdir(parents=True, exist_ok=True)
out.crop((750, 0, 1650, 260)).resize((720, 208), Image.LANCZOS).save(p, quality=55, optimize=True, progressive=True)
print(p, p.stat().st_size)
