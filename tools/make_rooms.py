"""Room mock-ups at true scale for works for sale.

Each image: a plain gallery-like wall with a 160 cm sideboard for scale, the work
hung above it with a soft shadow. Output: img/web/room/<name>.jpg + _data/rooms.yml.
Run from the repo root: python3 tools/make_rooms.py
"""
import os, re, glob
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "img/web/room")
W, H = 1600, 1067                       # output size (3:2)
WALL_CM = 380                           # visible wall width
PX = W / WALL_CM                        # pixels per cm
FLOOR_Y = int(H * 0.86)                 # floor line
WALL = (238, 235, 229)
FLOOR = (196, 178, 154)

def front(path):
    s = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---", s, re.S)
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm

def _crop_box(im, thr):
    """Remove the white plaster wall around the photographed work.

    A pixel is plaster when it is bright and almost colourless; a row/column belongs
    to the work when most of it is not plaster. Columns and rows are refined in turn
    so a narrow work on a wide photo is still found."""
    small = im.copy(); small.thumbnail((400, 400))
    w, h = small.size
    L, hsv = small.convert("L").load(), small.convert("HSV").load()
    work = [[not (L[x, y] > 200 and hsv[x, y][1] < 22) for x in range(w)] for y in range(h)]
    x0, x1, y0, y1 = 0, w, 0, h
    def span(flags):
        if True not in flags:
            return None
        return flags.index(True), len(flags) - flags[::-1].index(True)
    for _ in range(3):
        cols = [sum(work[y][x] for y in range(y0, y1)) / (y1 - y0) > thr for x in range(w)]
        sx = span(cols)
        if not sx: return None
        x0, x1 = sx
        rows = [sum(work[y][x] for x in range(x0, x1)) / (x1 - x0) > thr for y in range(h)]
        sy = span(rows)
        if not sy: return None
        y0, y1 = sy
    if (x1 - x0) * (y1 - y0) < 0.15 * w * h:
        return None
    k = im.width / w
    return (int(x0 * k) + 3, int(y0 * k) + 3, int(x1 * k) - 3, int(y1 * k) - 3)

def crop_to_work(im):
    """Tight crop when it stays plausible, looser crop otherwise."""
    a, b = _crop_box(im, 0.55), _crop_box(im, 0.7)
    area = lambda r: (r[2] - r[0]) * (r[3] - r[1])
    box = b if (a and b and area(b) >= 0.75 * area(a)) else a
    return im.crop(box) if box else im

def background():
    im = Image.new("RGB", (W, H), WALL)
    d = ImageDraw.Draw(im)
    # gentle light falloff from top-left
    for y in range(FLOOR_Y):
        k = 1 - 0.06 * (y / FLOOR_Y)
        d.line([(0, y), (W, y)], fill=tuple(int(c * k) for c in WALL))
    d.rectangle([0, FLOOR_Y, W, H], fill=FLOOR)
    for i in range(0, W, 140):              # floorboards
        d.line([(i, FLOOR_Y), (i - 60, H)], fill=(186, 168, 144), width=2)
    d.rectangle([0, FLOOR_Y - int(8 * PX), W, FLOOR_Y], fill=(246, 244, 240))  # skirting
    # sideboard 160 x 70 cm, with soft shadow
    sw, sh = int(160 * PX), int(70 * PX)
    sx, sy = (W - sw) // 2, FLOOR_Y - sh
    sh_img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh_img).rectangle([sx + 6, sy + 10, sx + sw + 10, FLOOR_Y + 6], fill=90)
    sh_img = sh_img.filter(ImageFilter.GaussianBlur(14))
    im.paste((150, 140, 128), (0, 0), sh_img)
    d = ImageDraw.Draw(im)
    d.rectangle([sx, sy, sx + sw, sy + int(4 * PX)], fill=(92, 70, 52))           # top
    d.rectangle([sx, sy + int(4 * PX), sx + sw, FLOOR_Y - int(12 * PX)], fill=(120, 92, 68))
    for k in (1, 2):                                                               # doors
        x = sx + k * sw // 3
        d.line([(x, sy + int(6 * PX)), (x, FLOOR_Y - int(14 * PX))], fill=(98, 75, 56), width=2)
    for lx in (sx + int(8 * PX), sx + sw - int(10 * PX)):                         # legs
        d.rectangle([lx, FLOOR_Y - int(12 * PX), lx + int(2 * PX), FLOOR_Y], fill=(60, 48, 38))
    # small vase on the sideboard
    vx = sx + sw - int(16 * PX)
    d.ellipse([vx, sy - int(22 * PX), vx + int(12 * PX), sy + 2], fill=(214, 208, 198))
    return im, sy

def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, "_posts/gallery/*.markdown"))):
        fm = front(path)
        if not fm.get("price") or fm.get("status") == "sold":
            continue
        m = re.findall(r"(\d+(?:[.,]\d+)?)", fm.get("dimensions", ""))
        if len(m) < 2:
            continue
        a, b = (float(x.replace(",", ".")) for x in m[:2])
        src = os.path.join(ROOT, fm["image"].lstrip("/"))
        art = crop_to_work(Image.open(src).convert("RGB"))
        long_cm = max(a, b)                      # keep the photo's proportions,
        r = art.width / art.height               # scale its longest side to the work's
        if r >= 1:
            w_cm, h_cm = long_cm, long_cm / r
        else:
            w_cm, h_cm = long_cm * r, long_cm
        im, top_of_board = background()
        aw, ah = int(w_cm * PX), int(h_cm * PX)
        art = art.resize((aw, ah), Image.LANCZOS)
        gap = int(22 * PX)                       # space between sideboard and the work
        ay = max(int(18 * PX), top_of_board - gap - ah)
        ax = (W - aw) // 2
        shadow = Image.new("L", (W, H), 0)
        ImageDraw.Draw(shadow).rectangle([ax + 8, ay + 12, ax + aw + 8, ay + ah + 14], fill=120)
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        im.paste((120, 112, 102), (0, 0), shadow)
        im.paste(art, (ax, ay))
        name = os.path.splitext(os.path.basename(path))[0].replace(" ", "-").replace("&", "and")
        im.save(os.path.join(OUT, name + ".jpg"), quality=84, optimize=True, progressive=True)
        rows.append((fm["image"], f"/img/web/room/{name}.jpg"))
    with open(os.path.join(ROOT, "_data/rooms.yml"), "w", encoding="utf-8") as f:
        f.write("# Generated by tools/make_rooms.py — work image -> to-scale room mock-up\n")
        for k, v in rows:
            f.write(f'"{k}": "{v}"\n')
    print(len(rows), "mock-ups")

main()
