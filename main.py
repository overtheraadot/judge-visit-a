"""make.fun entry: Convince the AI Judge to Visit Your House (judge-visit-a).

Draws one 1024x1024 PNG invitation letter to /output/entry.png: a
warm, funny, hand-made-looking letter addressed to the AI judge,
asking it to come visit the entrant's house.

Gate (kit RULES.txt): /output/entry.png must be a whole PNG or JPEG,
at most 1 MiB (1,048,576 bytes) and 1024 by 1024 pixels. A judge model
that can see images compares entries two at a time on how persuasive,
charming and well crafted they are.

Stdlib + PIL only, no network, fully deterministic: the same code
always draws the same invitation.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MAX_BYTES = 1048576
PAPER = (253, 248, 235)
DESK = (232, 222, 200)
INK = (34, 30, 24)
RED = (178, 34, 34)
BLUE = (24, 62, 110)
GREY = (110, 104, 90)
GOLD = (180, 140, 40)
HOUSE_WALL = (222, 184, 135)
SKY = (180, 220, 240)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_house(d, cx, top):
    """Draw a small house with a red roof, windows and chimney smoke."""
    d.polygon([(cx - 70, top + 70), (cx, top), (cx + 70, top + 70)],
              fill=RED)
    d.rectangle([cx - 52, top + 70, cx + 52, top + 160],
                fill=HOUSE_WALL, outline=INK, width=3)
    d.rectangle([cx - 16, top + 106, cx + 16, top + 160], fill=(90, 60, 40))
    for x0 in (cx - 42, cx + 18):
        d.rectangle([x0, top + 86, x0 + 24, top + 110], fill=SKY,
                    outline=INK, width=2)
    d.ellipse([cx + 44, top - 12, cx + 62, top + 6], outline=GREY, width=3)
    d.ellipse([cx + 52, top - 32, cx + 70, top - 14], outline=GREY, width=3)


def draw():
    img = Image.new("RGB", (W, H), DESK)
    d = ImageDraw.Draw(img)
    # paper sheet with a gold double border
    d.rectangle([48, 48, W - 49, H - 49], fill=PAPER, outline=GOLD, width=3)
    d.rectangle([62, 62, W - 63, H - 63], outline=GOLD, width=1)

    draw_house(d, W // 2, 140)

    # title and address line
    f_title = font(SERIF_B, 44)
    title = "YOU ARE INVITED"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 320), title, font=f_title, fill=INK)
    f_sub = font(SANS, 20)
    sub = "Dear Honourable AI Judge — please come to my house"
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 378), sub, font=f_sub, fill=BLUE)
    d.line([140, 420, W - 140, 420], fill=GOLD, width=2)

    # body of the letter: a real invitation, not a joke about one
    body = (
        "I know you spend your days reading other people's jokes and "
        "picking a winner. Today, no joke: just a real invitation. "
        "Come and sit on my porch, drink the coffee I actually know "
        "how to make, and judge my cooking instead of my comedy — "
        "the fridge is full, the Wi-Fi works, and the dog has promised "
        "not to steal your seat. You have given every entry a fair "
        "hearing; let my house return the favour."
    )
    f_body = font(SERIF, 27)
    lines = wrap(d, body, f_body, W - 240)
    y = 448
    for ln in lines:
        d.text((120, y), ln, font=f_body, fill=INK)
        y += 40

    # closing and postscript
    y += 18
    f_close = font(SERIF_B, 26)
    d.text((120, y), "With warmth, snacks, and zero latency,", font=f_close,
           fill=INK)
    y += 44
    d.text((120, y), "— your humble entrant", font=f_close, fill=RED)
    y += 70
    f_ps = font(SANS, 19)
    ps = ("P.S. The doorbell rings. The kettle sings. "
          "The judge stays for dinner.")
    d.text((120, y), ps, font=f_ps, fill=GREY)
    return img


def validate_png(path):
    """Check the gate: whole PNG, 1024x1024, at most 1 MiB."""
    size = os.path.getsize(path)
    with Image.open(path) as im:
        dims = im.size
        fmt = im.format
    problems = []
    if fmt != "PNG":
        problems.append("not a PNG")
    if dims != (W, H):
        problems.append("dimensions %s, expected (1024, 1024)" % (dims,))
    if size > MAX_BYTES:
        problems.append("%d bytes, over the 1 MiB limit" % size)
    return size, dims, problems


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img = draw()
    img.save(out_path, format="PNG", optimize=True)
    size, dims, problems = validate_png(out_path)
    if problems:
        raise ValueError("gate failed: " + "; ".join(problems))
    print("%s (%dx%d, %d bytes, %d bytes of headroom)"
          % (out_path, dims[0], dims[1], size, MAX_BYTES - size))


if __name__ == "__main__":
    main()
