"""Download candidate photos listed in tools/candidate-photos.txt and save
square 360x360 JPGs to assets/img/candidates/<slug>.jpg (plus a full copy in
tools/photo-originals/ for re-cropping review)."""
import io, os, sys, urllib.request
from PIL import Image, ImageOps
OUT = 'assets/img/candidates'; ORIG = 'tools/photo-originals'
os.makedirs(OUT, exist_ok=True); os.makedirs(ORIG, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (PEPAC site build; contact info@peoplesempowermentpac.org)'}
fails = []
for line in open('tools/candidate-photos.txt'):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    slug, url, fy, fx = [p.strip() for p in line.split('|')]
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        im = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert('RGB')
        w, h = im.size
        small = im.copy(); small.thumbnail((900, 900)); small.save(f'{ORIG}/{slug}.jpg', quality=80)
        side = min(w, h)
        cx, cy = float(fx) * w, float(fy) * h
        left = int(min(max(cx - side / 2, 0), w - side))
        top = int(min(max(cy - side / 2, 0), h - side))
        sq = im.crop((left, top, left + side, top + side)).resize((360, 360), Image.LANCZOS)
        sq.save(f'{OUT}/{slug}.jpg', quality=82, optimize=True, progressive=True)
        print('ok', slug, (w, h))
    except Exception as e:
        print('FAILED', slug, e); fails.append(slug)
if fails:
    print('Failed:', fails)
