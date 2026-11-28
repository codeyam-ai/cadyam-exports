"""Sticker pictures for Nadia's Field Notes: one emoji on a soft white disc, transparent PNG."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
STICKERS = {
    "notebook": "📓", "software": "💻", "north-star": "⭐", "new-york": "🗽",
    "travel": "✈", "runner": "🏃", "climb": "🧗", "surf": "🏄",
    "curious": "🔍", "car": "🚗", "graduate": "🎓", "fencing": "🤺", "rocket": "🚀",
}
font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 160)
S = 400
os.makedirs("stickers", exist_ok=True)
for name, ch in STICKERS.items():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((40, 52, S - 40, S - 28), fill=(0, 0, 0, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.ellipse((36, 36, S - 36, S - 36), fill=(255, 255, 255, 250))
    d.ellipse((50, 50, S - 50, S - 50), outline=(255, 212, 0, 255), width=8)
    e = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    ImageDraw.Draw(e).text((100, 100), ch, font=font, embedded_color=True, anchor="mm")
    e = e.crop(e.getbbox()) if e.getbbox() else e
    k = 210 / max(e.size)
    e = e.resize((round(e.width * k), round(e.height * k)), Image.LANCZOS)
    im.alpha_composite(e, ((S - e.width) // 2, (S - e.height) // 2))
    im.save(f"stickers/{name}.png")
print("ok", len(STICKERS))
