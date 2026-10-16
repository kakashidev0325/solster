"""Build Solana Roadster image assets from the supplied logo and banner."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import os

ROOT = r"E:\pack\solana\solster"
SRC = r"C:\Users\Alita\.cursor\projects\e-pack-solana-solster\assets"
OUT = os.path.join(ROOT, "assets")
PRE = os.path.join(ROOT, "_preview")

USER_BANNER = os.path.join(
    SRC,
    "c__Users_Alita_AppData_Roaming_Cursor_User_workspaceStorage_f4db127723baa2f8f30c8deee752d258_images_banner-a2fdd30c-1f4f-4ebd-ab45-0d27424915d6.png",
)
USER_LOGO = os.path.join(
    SRC,
    "c__Users_Alita_AppData_Roaming_Cursor_User_workspaceStorage_f4db127723baa2f8f30c8deee752d258_images_logo-f4a712b9-ab47-4c22-9b64-90b9382f2578.png",
)
MARK_SRC = os.path.join(SRC, "solster-mark.jpg")
PORT_SRC = os.path.join(SRC, "solster-portrait-text.jpg")
GREEN_SRC = os.path.join(SRC, "solster-mascot-green.jpg")

FONT_LIGHT = r"C:\Windows\Fonts\segoeuil.ttf"
FONT_SEMI = r"C:\Windows\Fonts\seguisb.ttf"


def cover(base, box, sample):
    """Replace a rectangle with a nearby texture. Center is fully opaque."""
    x0, y0, x1, y1 = box
    patch = base.crop(sample).resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    patch = patch.filter(ImageFilter.GaussianBlur(0.8))
    mask = Image.new("L", patch.size, 0)
    d = ImageDraw.Draw(mask)
    d.rectangle((0, 0, patch.size[0] - 1, patch.size[1] - 1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    d.rectangle((4, 4, patch.size[0] - 5, patch.size[1] - 5), fill=255)
    base.paste(patch, (x0, y0), mask)


def dim_cyan(im, box):
    """Knock out bright cyan lettering on a tower without repainting the facade."""
    x0, y0, x1, y1 = box
    px = im.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if b > 165 and g > 145 and b > r + 25 and g > r + 8:
                px[x, y] = (int(r * 0.32), int(g * 0.22), int(b * 0.26))


def tracked(draw, text, xy, font, fill, tracking, anchor="mm"):
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x, y = xy
    if "m" in anchor[0]:
        x -= total / 2
    elif "r" in anchor[0]:
        x -= total
    # vertical: use font bbox of a capital
    bbox = font.getbbox("Hg")
    h = bbox[3] - bbox[1]
    if anchor[1] == "m":
        y -= h / 2
    elif anchor[1] == "b":
        y -= h
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return total


def build_banner():
    im = Image.open(USER_BANNER).convert("RGB")
    # Hide the old wall tagline under the SOLANA wordmark.
    cover(im, (136, 124, 336, 192), (62, 158, 124, 198))
    # Hide the right-hand slogan stack in the sky.
    cover(im, (900, 18, 1018, 142), (760, 8, 880, 70))
    # Hide the "BUILD ON SOLANA" tower sign.
    dim_cyan(im, (708, 96, 802, 172))

    im = im.resize((1500, 500), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(im)
    sx, sy = 1500 / 1024, 500 / 341

    wall = ImageFont.truetype(FONT_LIGHT, 15)
    sky = ImageFont.truetype(FONT_LIGHT, 15)
    wall_fill = (198, 204, 220)
    sky_fill = (232, 236, 246)

    cx = int(228 * sx)
    y = int(136 * sy)
    for line in ("ROADSTER", "$SOLSTER"):
        tracked(draw, line, (cx, y), wall, wall_fill, 3.4, "mt")
        y += 20

    rx = int(968 * sx)
    ry = int(36 * sy)
    draw.line((rx - 18, ry, rx + 18, ry), fill=sky_fill, width=1)
    ry += 12
    for line in ("SOLANA", "ROADSTER", "$SOLSTER"):
        tracked(draw, line, (rx, ry), sky, sky_fill, 3.6, "mt")
        ry += 20

    im.save(os.path.join(OUT, "banner.png"), "PNG", optimize=True)
    im.save(os.path.join(ROOT, "banner.png"), "PNG", optimize=True)

    # Social card: blurred full-bleed behind the sharp banner.
    bg = im.resize((1200, 630), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    sharp = im.resize((1200, 400), Image.Resampling.LANCZOS)
    bg.paste(sharp, (0, 115))
    bg.save(os.path.join(OUT, "og.jpg"), "JPEG", quality=88, optimize=True)
    return im


def build_mark_and_portrait():
    mark = Image.open(MARK_SRC).convert("RGB").resize((1024, 1024), Image.Resampling.LANCZOS)
    mark.save(os.path.join(OUT, "mark.png"), "PNG", optimize=True)

    port = Image.open(PORT_SRC).convert("RGB")
    dim_cyan(port, (680, 390, 840, 500))
    port.save(os.path.join(OUT, "portrait.png"), "PNG", optimize=True)


def build_mascot():
    im = Image.open(GREEN_SRC).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if g > 70 and g > r * 1.22 and g > b * 1.22:
                gap = g - max(r, b)
                t = max(0.0, min(1.0, (gap - 12) / 80.0))
                # despill: pull green down toward the other channels
                ng = int(min(g, max(r, b)))
                px[x, y] = (r, ng, b, int(255 * (1 - t)))
    # trim to the car and pad back to a square
    bbox = im.getbbox()
    if bbox:
        car = im.crop(bbox)
        side = max(car.size)
        pad = int(side * 0.08)
        canvas = Image.new("RGBA", (side + pad * 2, side + pad * 2), (0, 0, 0, 0))
        canvas.paste(car, ((canvas.size[0] - car.size[0]) // 2, (canvas.size[1] - car.size[1]) // 2), car)
        im = canvas
    im = im.resize((1024, 1024), Image.Resampling.LANCZOS)
    im.save(os.path.join(OUT, "mascot.png"), "PNG")

    # QA on a checker and on the site navy
    chk = Image.new("RGBA", (512, 512), (12, 16, 32, 255))
    d = ImageDraw.Draw(chk)
    for y in range(0, 512, 32):
        for x in range(0, 512, 32):
            if (x // 32 + y // 32) % 2 == 0:
                d.rectangle((x, y, x + 32, y + 32), fill=(28, 34, 58, 255))
    chk.alpha_composite(im.resize((512, 512), Image.Resampling.LANCZOS))
    chk.convert("RGB").save(os.path.join(PRE, "mascot-check.png"))


def build_icons():
    src = Image.open(MARK_SRC).convert("RGB")
    # The glowing bars sit on the upper-left wall of the hero mark.
    px = src.load()
    w, h = src.size
    xs, ys = [], []
    for y in range(0, int(h * 0.48)):
        for x in range(0, int(w * 0.48)):
            r, g, b = px[x, y]
            mx, mn = max(r, g, b), min(r, g, b)
            cyan = g > 150 and b > 140 and g > r + 20
            purple = b > 140 and r > 90 and r > g + 15 and b > g
            if mx > 150 and (mx - mn) > 60 and (cyan or purple):
                xs.append(x)
                ys.append(y)
    if not xs:
        raise SystemExit("logo bars not found")
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    # pad the crop so the glow is included
    pad = int(max(x1 - x0, y1 - y0) * 0.28)
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(w, x1 + pad), min(h, y1 + pad)
    # square crop centered on the bars
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    side = max(x1 - x0, y1 - y0)
    # extra margin so a circular nav crop does not clip the bars
    side = int(side * 1.35)
    half = side // 2
    crop = src.crop((cx - half, cy - half, cx + half, cy + half))
    crop.save(os.path.join(PRE, "icon-source.png"))

    def save_icon(size, path):
        icon = crop.resize((size, size), Image.Resampling.LANCZOS)
        icon.save(path, "PNG", optimize=True)

    save_icon(512, os.path.join(OUT, "icon-512.png"))
    save_icon(512, os.path.join(ROOT, "logo.png"))
    save_icon(256, os.path.join(OUT, "logo-nav.png"))
    save_icon(180, os.path.join(OUT, "apple-touch-icon.png"))
    save_icon(32, os.path.join(OUT, "favicon-32.png"))


if __name__ == "__main__":
    build_banner()
    build_mark_and_portrait()
    build_mascot()
    build_icons()
    print("done")
