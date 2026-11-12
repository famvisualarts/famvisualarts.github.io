# Room mock-ups used on works for sale. Base room: Pexels photo 6083149 (free licence), frames removed -> wall-contemporain.jpg.
# Kept as a record of the settings (ppc 6.28 px/cm, sideboard 180 cm); paths inside are from the working session.
import os, re, glob, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
ns = {'__file__': '/home/claude/fam-live/tools/make_rooms.py'}
exec(open('old_make_rooms.py').read().split('\ndef background')[0], ns)
ROOT = '/home/claude/fam-live'

def extend_top(im, add):
    """Grow the plain wall upwards by `add` px (continues the top rows, light noise)."""
    a = np.asarray(im).astype(float)
    top = a[:30].mean(axis=0)                     # (W,3) colour of the wall near the top
    grad = np.linspace(0.985, 1.0, add)[:, None, None]
    ext = top[None] * grad + np.random.default_rng(1).normal(0, 1.2, (add, a.shape[1], 1))
    out = np.vstack([ext, a])
    img = Image.fromarray(np.uint8(np.clip(out, 0, 255)))
    band = img.crop((0, add - 12, img.width, add + 12)).filter(ImageFilter.GaussianBlur(6))
    img.paste(band, (0, add - 12))
    return img

ROOMS = {
  'modern': dict(file='wall_g.jpg', ppc=6.28, cx=1025, base=674, gap=18, add=340),
  # px per cm, centre x, y of the sofa back (art bottom = that line minus gap), gap in cm, extra wall on top
  'small': dict(file='room_a.jpg', ppc=5.4, cx=478, base=495, gap=16, add=0),
  'large': dict(file='room_e.jpg', ppc=4.8, cx=905, base=585, gap=14, add=300),
}

def place(room, art, w_cm, h_cm):
    R = ROOMS[room]
    im = Image.open(R['file']).convert('RGB')
    if R['add']: im = extend_top(im, R['add'])
    ppc = R['ppc']; aw, ah = round(w_cm * ppc), round(h_cm * ppc)
    bottom = R['base'] + R['add'] - round(R['gap'] * ppc)
    x0, y0 = round(R['cx'] - aw / 2), bottom - ah
    # match the room: slightly lower contrast, a touch of the room's warmth
    art = art.resize((aw, ah), Image.LANCZOS)
    art = ImageEnhance.Contrast(art).enhance(0.94)
    wall = np.asarray(im.crop((x0 - 40, y0 - 40, x0 + aw + 40, y0))).reshape(-1, 3).mean(0)
    tint = Image.new('RGB', art.size, tuple(int(v) for v in wall))
    art = Image.blend(art, tint, 0.05)
    # soft light falloff across the canvas (light from the top-left)
    g = np.linspace(1.02, 0.95, ah)[:, None] * np.linspace(1.01, 0.97, aw)[None, :]
    art = Image.fromarray(np.uint8(np.clip(np.asarray(art) * g[..., None], 0, 255)))
    # shadows: tight contact shadow + wide soft drop shadow below/right
    depth = max(2, round(2.2 * ppc / 5))          # ~2 cm stretcher depth
    for off, blur, alpha in ((depth, 2, 150), (round(depth * 2.5), round(ppc * 3), 95)):
        s = Image.new('L', im.size, 0)
        ImageDraw.Draw(s).rectangle([x0 + off // 2, y0 + off, x0 + aw + off // 2, y0 + ah + off], fill=alpha)
        im.paste((60, 55, 50), (0, 0), s.filter(ImageFilter.GaussianBlur(blur)))
    im.paste(art, (x0, y0))
    d = ImageDraw.Draw(im)
    d.line([(x0, y0 + ah - 1), (x0 + aw, y0 + ah - 1)], fill=(70, 64, 58), width=1)   # canvas bottom edge
    return im

def trim_edges(im, limit=0.25, run=8):
    """Drop leftover plaster bands on any side, even if a thin shadow line sits on the edge."""
    a = np.asarray(im.convert('HSV')).astype(int); l = np.asarray(im.convert('L')).astype(int)
    plaster = (l > 205) & (a[..., 1] < 25)
    def cut(frac):                     # frac: plaster fraction per line, from the edge inwards
        n = len(frac); lim = int(n * limit); k = 0
        while k < lim:
            if frac[k:k + run].mean() > .6:          # a plaster band starts here
                j = k
                while j < lim and frac[j] <= .5: j += 1     # skip the thin edge line
                s0 = j
                while j < lim and frac[j] > .5: j += 1
                return j if j > s0 + run else 0
            k += 1
            if k > 6: break                          # only allow a few non-plaster edge lines
        return 0
    rows, cols = plaster.mean(1), plaster.mean(0)
    t = cut(rows); b = len(rows) - cut(rows[::-1]); lf = cut(cols); r = len(cols) - cut(cols[::-1])
    return im.crop((lf, t, r, b))

def build(post):
    fm = ns['front'](os.path.join(ROOT, '_posts/gallery', post))
    a, b = (float(v.replace(',', '.')) for v in re.findall(r'(\d+(?:[.,]\d+)?)', fm['dimensions'])[:2])
    art = ns['crop_to_work'](Image.open(os.path.join(ROOT, fm['image'].lstrip('/'))).convert('RGB'))
    art = trim_edges(art)
    L = max(a, b); r = art.width / art.height
    w_cm, h_cm = (L, L / r) if r >= 1 else (L * r, L)
    im = place('modern', art, w_cm, h_cm)
    R = ROOMS['modern']; ah = round(h_cm * R['ppc'])
    top = R['base'] + R['add'] - round(R['gap'] * R['ppc']) - ah     # top of the work
    y = min(R['add'], max(0, top - 110))                              # keep ~18 cm of wall above
    im = im.crop((0, y, im.width, y + 1234))
    im.thumbnail((1600, 1600))
    return im, fm

if __name__ == '__main__':
    for p in sys.argv[1:]:
        im, fm = build(p); im.save('sample_' + p.split('.')[0].replace(' ', '-') + '.jpg', quality=86)
