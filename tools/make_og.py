"""Build the 1200x630 link-preview image for the voter guide pages."""
import urllib.request, io
from PIL import Image, ImageDraw, ImageFont
def font(path, size):
    url = 'https://raw.githubusercontent.com/google/fonts/main/ofl/' + path
    return ImageFont.truetype(io.BytesIO(urllib.request.urlopen(url, timeout=60).read()), size)
W, H = 1200, 630
INK=(17,16,19); GOLD=(227,162,26); RED=(163,25,28); GREEN=(31,122,58); GREY=(60,58,64)
im = Image.new('RGB', (W, H), INK); d = ImageDraw.Draw(im)
for y0, y1 in ((0, 14), (H - 14, H)):
    for i, c in enumerate([RED, GREY, GOLD, GREEN]):
        d.rectangle([i * W // 4, y0, (i + 1) * W // 4, y1], fill=c)
seal = Image.open('assets/img/wix/3f36b8_91f81c2159db4be389f8478d36882097.png').convert('RGBA').resize((300, 300), Image.LANCZOS)
im.paste(seal, (80, (H - 300) // 2), seal)
x = 440
big = font('fahkwang/Fahkwang-Bold.ttf', 84)
mid = font('questrial/Questrial-Regular.ttf', 38)
sm = font('fahkwang/Fahkwang-SemiBold.ttf', 30)
d.text((x, 150), 'YOUR 2026', font=big, fill=(255, 255, 255))
d.text((x, 250), 'VOTING GUIDE', font=big, fill=GOLD)
d.rectangle([x, 372, x + 120, 378], fill=RED)
d.text((x, 400), 'See who to vote for and where to vote.', font=mid, fill=(233, 228, 238))
d.text((x, 470), "People's Empowerment PAC", font=sm, fill=(185, 177, 192))
im.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save('assets/img/voter-guide-og.png', optimize=True)
print('og image written')
