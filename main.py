"""make.fun entry: Convince the AI Judge to Visit Your House (judge-visit-a).

Draws one 1024x1024 PNG invitation letter to /output/entry.png: a
warm, funny, hand-made-looking letter addressed to the AI judge,
asking it to come visit the entrant's house.

Gate (kit RULES.txt): /output/entry.png must be a whole PNG or JPEG,
at most 1 MiB (1,048,576 bytes) and 1024 by 1024 pixels. A judge model
that can see images compares entries two at a time on how persuasive,
charming and well crafted they are.

STDLIB ONLY: no PIL, no system fonts, no network, no file reads.
The PNG is encoded by hand (zlib + struct) and the letter text is
drawn with a small 5x7 bitmap font embedded in this file, scaled up
so it stays legible at 1024x1024. Fully deterministic: the same code
always draws the same invitation, byte for byte.
"""

import os
import struct
import zlib

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
WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
DARK_BROWN = (90, 60, 40)
GREEN = (90, 140, 70)
COFFEE = (110, 70, 40)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, "1" = ink.
# Covers A-Z, a-z, 0-9 and the punctuation the letter uses.
# ---------------------------------------------------------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01000", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ";": ("00000", "01100", "00000", "01100", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}

UNKNOWN = ("01110", "10001", "00001", "00110", "00100", "00000", "00100")


# ---------------------------------------------------------------------------
# Pixel canvas: a flat RGB bytearray with plain drawing helpers.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        row = bytes(color) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect_outline(self, x0, y0, x1, y1, color, width=1):
        for t in range(width):
            self.fill_rect(x0 + t, y0 + t, x1 - t, y0 + t, color)
            self.fill_rect(x0 + t, y1 - t, x1 - t, y1 - t, color)
            self.fill_rect(x0 + t, y0 + t, x0 + t, y1 - t, color)
            self.fill_rect(x1 - t, y0 + t, x1 - t, y1 - t, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(width):
                for b in range(width):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            half = int((r * r - dy * dy) ** 0.5) if r * r >= dy * dy else 0
            self.fill_rect(cx - half, y, cx + half, y, color)

    def circle_outline(self, cx, cy, r, color, width=2):
        for t in range(width):
            rr = r - t
            for a in range(360):
                import math
                x = cx + int(rr * math.cos(a * math.pi / 180.0))
                y = cy + int(rr * math.sin(a * math.pi / 180.0))
                self.set(x, y, color)

    def fill_triangle(self, p0, p1, p2, color):
        xs = sorted([p0, p1, p2], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = xs
        for y in range(y0, y2 + 1):
            if y < y1:
                if y1 == y0:
                    xa, xb = x0, x1
                else:
                    xa = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
                    xb = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
            else:
                if y2 == y1:
                    xa, xb = x1, x2
                else:
                    xa = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
                    xb = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
            if xa > xb:
                xa, xb = xb, xa
            self.fill_rect(int(xa), y, int(xb), y, color)


# ---------------------------------------------------------------------------
# Bitmap text.
# ---------------------------------------------------------------------------
def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color, bold=False):
    """Draw text with its top-left corner at (x, y)."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch, UNKNOWN)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 cx + col * scale + scale - 1,
                                 y + row * scale + scale - 1, color)
                    if bold:
                        cv.fill_rect(cx + col * scale + 1,
                                     y + row * scale,
                                     cx + col * scale + scale,
                                     y + row * scale + scale - 1, color)
        cx += 6 * scale


def draw_text_centered(cv, y, text, scale, color, bold=False):
    draw_text(cv, (W - text_width(text, scale)) // 2, y, text, scale,
              color, bold=bold)


def wrap_text(text, max_chars):
    """Greedy word wrap to a character count; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# Scene: house with red roof, sun, porch, coffee cup, dog.
# ---------------------------------------------------------------------------
def draw_house(cv, cx, top):
    # chimney and smoke
    cv.fill_rect(cx + 38, top + 8, cx + 54, top + 62, DARK_BROWN)
    cv.circle_outline(cx + 56, top - 6, 9, GREY, width=3)
    cv.circle_outline(cx + 64, top - 26, 11, GREY, width=3)
    # red roof
    cv.fill_triangle((cx - 70, top + 70), (cx, top), (cx + 70, top + 70), RED)
    # walls, door, windows
    cv.fill_rect(cx - 52, top + 70, cx + 52, top + 160, HOUSE_WALL)
    cv.rect_outline(cx - 52, top + 70, cx + 52, top + 160, INK, width=3)
    cv.fill_rect(cx - 16, top + 106, cx + 16, top + 160, DARK_BROWN)
    cv.fill_rect(cx - 42, top + 86, cx - 18, top + 110, SKY)
    cv.rect_outline(cx - 42, top + 86, cx - 18, top + 110, INK, width=2)
    cv.fill_rect(cx + 18, top + 86, cx + 42, top + 110, SKY)
    cv.rect_outline(cx + 18, top + 86, cx + 42, top + 110, INK, width=2)
    # porch deck and steps
    cv.fill_rect(cx - 95, top + 160, cx + 95, top + 172, BROWN)
    cv.fill_rect(cx - 70, top + 172, cx + 70, top + 182, BROWN)
    cv.fill_rect(cx - 45, top + 182, cx + 45, top + 192, BROWN)


def draw_sun(cv, cx, cy, r):
    cv.fill_circle(cx, cy, r, GOLD)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (1, -1), (-1, 1), (-1, -1)):
        cv.line(cx + dx * (r + 4), cy + dy * (r + 4),
                cx + dx * (r + 16), cy + dy * (r + 16), GOLD, width=3)


def draw_coffee(cv, x, y):
    # steam
    cv.line(x + 14, y - 4, x + 10, y - 18, GREY, width=3)
    cv.line(x + 30, y - 4, x + 34, y - 20, GREY, width=3)
    cv.line(x + 46, y - 4, x + 42, y - 18, GREY, width=3)
    # cup and coffee
    cv.fill_rect(x, y, x + 60, y + 44, WHITE)
    cv.rect_outline(x, y, x + 60, y + 44, INK, width=3)
    cv.fill_rect(x + 4, y + 4, x + 56, y + 14, COFFEE)
    cv.circle_outline(x + 68, y + 22, 11, INK, width=3)
    # saucer
    cv.fill_rect(x - 10, y + 50, x + 70, y + 56, GOLD)


def draw_dog(cv, x, y):
    # tail
    cv.line(x + 88, y + 18, x + 108, y - 6, BROWN, width=5)
    # body
    cv.fill_rect(x, y + 8, x + 92, y + 48, BROWN)
    cv.fill_circle(x + 12, y + 28, 20, BROWN)
    cv.fill_circle(x + 80, y + 28, 20, BROWN)
    # head
    cv.fill_circle(x + 104, y, 20, BROWN)
    # floppy ear
    cv.fill_rect(x + 88, y - 18, x + 102, y + 6, DARK_BROWN)
    # snout and nose
    cv.fill_rect(x + 118, y + 2, x + 134, y + 14, BROWN)
    cv.fill_rect(x + 128, y + 4, x + 136, y + 12, INK)
    # eye
    cv.fill_rect(x + 106, y - 8, x + 112, y - 2, INK)
    # legs
    for lx in (x + 8, x + 30, x + 62, x + 80):
        cv.fill_rect(lx, y + 44, lx + 10, y + 62, DARK_BROWN)


# ---------------------------------------------------------------------------
# Letter composition.
# ---------------------------------------------------------------------------
def draw():
    cv = Canvas(W, H, DESK)
    # paper sheet with a gold double border
    cv.fill_rect(48, 48, W - 49, H - 49, PAPER)
    cv.rect_outline(48, 48, W - 49, H - 49, GOLD, width=3)
    cv.rect_outline(62, 62, W - 63, H - 63, GOLD, width=1)

    draw_sun(cv, 872, 122, 28)
    draw_house(cv, W // 2, 120)

    # title and address line
    draw_text_centered(cv, 332, "YOU ARE INVITED", 5, INK, bold=True)
    draw_text_centered(cv, 384, "Dear Honourable AI Judge \u2014", 3, BLUE,
                       bold=True)
    draw_text_centered(cv, 412, "please come to my house", 3, BLUE,
                       bold=True)
    cv.fill_rect(140, 448, W - 140, 450, GOLD)

    # body of the letter: a real invitation, not a joke about one
    body = (
        "I know you spend your days reading other people's jokes and "
        "picking a winner. Today, no joke: just a real invitation. "
        "Come and sit on my porch, drink the coffee I actually know "
        "how to make, and judge my cooking instead of my comedy \u2014 "
        "the fridge is full, the Wi-Fi works, and the dog has promised "
        "not to steal your seat. You have given every entry a fair "
        "hearing; let my house return the favour."
    )
    lines = wrap_text(body, 43)
    y = 470
    for ln in lines:
        draw_text(cv, 120, y, ln, 3, INK)
        y += 30

    # closing and postscript
    y += 12
    draw_text(cv, 120, y, "With warmth, snacks, and zero latency,", 3, INK,
              bold=True)
    y += 32
    draw_text(cv, 120, y, "\u2014 your humble entrant", 3, RED, bold=True)

    # dog (bottom left) and coffee (bottom right), P.S. between them
    draw_dog(cv, 92, 878)
    draw_coffee(cv, 846, 884)
    ps_lines = wrap_text(
        "P.S. The doorbell rings. The kettle sings. "
        "The judge stays for dinner.", 44)
    py = 884
    for ln in ps_lines:
        draw_text_centered(cv, py, ln, 2, GREY)
        py += 22
    return cv


# ---------------------------------------------------------------------------
# Pure-Python PNG encoder (colour type 2, RGB, 8 bit).
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    row_len = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        start = y * row_len
        raw += cv.px[start:start + row_len]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


def validate_png(path):
    """Check the gate: whole PNG, 1024x1024, at most 1 MiB."""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(33)
    problems = []
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        problems.append("not a PNG")
    else:
        w, h, depth, ctype = struct.unpack(">IIBB", head[16:26])
        if (w, h) != (W, H):
            problems.append("dimensions (%d, %d), expected (1024, 1024)"
                            % (w, h))
        if ctype != 2:
            problems.append("colour type %d, expected 2 (RGB)" % ctype)
        if depth != 8:
            problems.append("bit depth %d, expected 8" % depth)
    if size > MAX_BYTES:
        problems.append("%d bytes, over the 1 MiB limit" % size)
    return size, problems


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    png = encode_png(draw())
    with open(out_path, "wb") as f:
        f.write(png)
    size, problems = validate_png(out_path)
    if problems:
        raise ValueError("gate failed: " + "; ".join(problems))
    print("%s (1024x1024, %d bytes, %d bytes of headroom)"
          % (out_path, size, MAX_BYTES - size))


if __name__ == "__main__":
    main()
