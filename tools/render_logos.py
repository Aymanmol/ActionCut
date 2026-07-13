"""Render ActionCut logo concept mockups (108dp adaptive-icon scale) on the dark theme
with the red->coral->gold brand gradient. Outputs individual PNGs + a contact sheet."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

R = 864  # hi-res render, downscaled to 432
OUT = os.path.join("tools", "logo_concepts")
os.makedirs(OUT, exist_ok=True)


def brand_grad():
    yy, xx = np.mgrid[0:R, 0:R].astype(float)
    t = np.clip((xx + yy) / (2 * R - 2), 0, 1)[..., None]
    c0 = np.array([255, 46, 77.]); c1 = np.array([255, 107, 61.]); c2 = np.array([255, 194, 71.])
    out = np.where(t < 0.5, c0 + (c1 - c0) * (t * 2), c1 + (c2 - c1) * ((t - 0.5) * 2))
    return Image.fromarray(out.astype("uint8"), "RGB").convert("RGBA")


def warm_bg():
    yy, xx = np.mgrid[0:R, 0:R].astype(float)
    t = np.clip((xx + yy) / (2 * R - 2), 0, 1)[..., None]
    c0 = np.array([21, 10, 12.]); c1 = np.array([38, 16, 20.])
    return Image.fromarray((c0 + (c1 - c0) * t).astype("uint8"), "RGB").convert("RGBA")


def grad_from_mask(mask_L):
    layer = Image.new("RGBA", (R, R), (0, 0, 0, 0))
    layer.paste(brand_grad(), (0, 0), mask_L)
    return layer


def compose(mark_rgba):
    bg = warm_bg()
    bg.alpha_composite(mark_rgba)
    rm = Image.new("L", (R, R), 0)
    ImageDraw.Draw(rm).rounded_rectangle([0, 0, R - 1, R - 1], radius=int(R * 0.24), fill=255)
    out = Image.new("RGBA", (R, R), (0, 0, 0, 0))
    out.paste(bg, (0, 0), rm)
    return out.resize((432, 432), Image.LANCZOS)


def concept_split_play():
    tri = Image.new("L", (R, R), 0)
    ImageDraw.Draw(tri).polygon([(300, 250), (600, 432), (300, 614)], fill=255)
    t = np.array(tri) > 0
    yy, xx = np.mgrid[0:R, 0:R]
    side = (xx + yy) < R
    a = t & side
    b = t & ~side
    k = 17
    a = np.roll(np.roll(a, -k, 0), -k, 1)
    b = np.roll(np.roll(b, k, 0), k, 1)
    alpha = ((a | b) * 255).astype("uint8")
    return compose(grad_from_mask(Image.fromarray(alpha, "L")))


def concept_ligature():
    yy, xx = np.mgrid[0:R, 0:R].astype(float)
    dx = xx - 432; dy = yy - 432
    r = np.sqrt(dx * dx + dy * dy)
    ang = np.degrees(np.arctan2(dy, dx))
    ring = (r >= 200) & (r <= 300) & ~((ang > -46) & (ang < 46))
    tri = Image.new("L", (R, R), 0)
    ImageDraw.Draw(tri).polygon([(372, 312), (566, 432), (372, 552)], fill=255)
    alpha = ((ring | (np.array(tri) > 0)) * 255).astype("uint8")
    return compose(grad_from_mask(Image.fromarray(alpha, "L")))


def concept_snap():
    layer = Image.new("RGBA", (R, R), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([R * 0.17, R * 0.50, R * 0.83, R * 0.82], radius=42, fill=(244, 244, 248, 255))
    # play triangle on the board (gradient)
    tri = Image.new("L", (R, R), 0)
    ImageDraw.Draw(tri).polygon([(R * 0.42, R * 0.58), (R * 0.64, R * 0.66), (R * 0.42, R * 0.74)], fill=255)
    layer.alpha_composite(grad_from_mask(Image.fromarray(np.array(tri), "L")))
    # clapper arm + stripes on its own layer, then rotate open
    arm = Image.new("RGBA", (R, R), (0, 0, 0, 0))
    ad = ImageDraw.Draw(arm)
    ad.rounded_rectangle([R * 0.15, R * 0.33, R * 0.83, R * 0.47], radius=18, fill=(22, 18, 26, 255))
    for x0 in (0.17, 0.28, 0.39, 0.50, 0.61, 0.72):
        x = R * x0
        ad.polygon([(x, R * 0.47), (x + R * 0.05, R * 0.47), (x + R * 0.09, R * 0.33), (x + R * 0.04, R * 0.33)],
                   fill=(244, 244, 248, 255))
    arm = arm.rotate(22, center=(R * 0.17, R * 0.47), resample=Image.BICUBIC)
    layer.alpha_composite(arm)
    # motion streaks near the hinge (gradient)
    streaks = Image.new("L", (R, R), 0)
    sd = ImageDraw.Draw(streaks)
    for y0, ln in ((0.20, 0.11), (0.27, 0.08), (0.15, 0.07)):
        sd.line([(R * 0.05, R * y0), (R * (0.05 + ln), R * y0)], fill=255, width=12)
    layer.alpha_composite(grad_from_mask(Image.fromarray(np.array(streaks), "L")))
    return compose(layer)


concepts = [
    ("1_split_play", "Split-Play", concept_split_play()),
    ("2_ac_ligature", "AC Ligature", concept_ligature()),
    ("3_snap", "Snap!", concept_snap()),
]
for fid, _, img in concepts:
    img.save(os.path.join(OUT, f"{fid}.png"))

# Contact sheet
pad, label_h = 40, 70
sheet = Image.new("RGB", (432 * 3 + pad * 4, 432 + label_h + pad * 2), (12, 10, 12))
draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("arial.ttf", 34)
except Exception:
    font = ImageFont.load_default()
for i, (_, name, img) in enumerate(concepts):
    x = pad + i * (432 + pad)
    sheet.paste(img.convert("RGB"), (x, pad))
    w = draw.textlength(name, font=font)
    draw.text((x + 216 - w / 2, pad + 432 + 16), name, fill=(240, 240, 240), font=font)
sheet.save(os.path.join(OUT, "contact_sheet.png"))
print("wrote", OUT, [c[0] for c in concepts])
