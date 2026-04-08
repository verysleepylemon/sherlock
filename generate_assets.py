"""Generate demo assets for README: terminal GIF + UI mockup PNG."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(DIR, 'assets')
os.makedirs(ASSETS, exist_ok=True)

# ═══════════════════════════════════════════════════════════
#  Colors
# ═══════════════════════════════════════════════════════════
BG      = (10, 13, 20)
BG2     = (13, 17, 23)
GOLD    = (230, 180, 80)
BLUE    = (88, 166, 255)
GREEN   = (63, 185, 80)
RED     = (248, 81, 73)
PINK    = (233, 30, 99)
PURPLE  = (156, 39, 176)
CYAN    = (0, 188, 212)
ORANGE  = (255, 152, 0)
GRAY    = (139, 148, 158)
DIM     = (72, 79, 88)
WHITE   = (201, 209, 217)
BORDER  = (33, 38, 45)

def get_font(size):
    """Try Consolas, Courier New, then default."""
    for name in ['consola.ttf', 'consolab.ttf', 'cour.ttf', 'lucon.ttf']:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.truetype('C:/Windows/Fonts/consola.ttf', size)
    except (OSError, IOError):
        return ImageFont.load_default()

FONT    = get_font(14)
FONT_B  = get_font(15)
FONT_SM = get_font(11)
FONT_T  = get_font(18)

# ═══════════════════════════════════════════════════════════
#  1. Terminal Animation GIF
# ═══════════════════════════════════════════════════════════
def draw_terminal_frame(lines, cursor_line=None):
    """Draw a terminal window with given lines."""
    W, H = 780, 520
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # Title bar
    d.rectangle([0, 0, W, 32], fill=(30, 33, 40))
    d.ellipse([12, 10, 24, 22], fill=(255, 95, 87))
    d.ellipse([30, 10, 42, 22], fill=(255, 189, 46))
    d.ellipse([48, 10, 60, 22], fill=(39, 201, 63))
    d.text((W//2 - 80, 7), '线索网 — Clue Web', fill=GRAY, font=FONT_SM)

    # Content area
    y = 42
    for i, (text, color) in enumerate(lines):
        if cursor_line is not None and i == cursor_line:
            d.rectangle([8, y-1, W-8, y+17], fill=(22, 27, 34))
        d.text((16, y), text, fill=color, font=FONT)
        y += 19
        if y > H - 20:
            break

    return img

# Build frames
frames = []

# Frame 1: Command input
f1_lines = [
    ('$ python investigate.py sleepy_lemonade --timeout 15', GREEN),
    ('', WHITE),
]
frames.append((draw_terminal_frame(f1_lines, 0), 1200))

# Frame 2: Header appears
f2_lines = [
    ('$ python investigate.py sleepy_lemonade --timeout 15', GREEN),
    ('', WHITE),
    ('══════════════════════════════════════════════════════════', GOLD),
    ('  线索网  ·  Clue Web Investigation', GOLD),
    ('══════════════════════════════════════════════════════════', GOLD),
    ('  Target     : sleepy_lemonade', WHITE),
    ('  Variations : sleepy_lemonade, sleepylemonade,', WHITE),
    ('               sleepy.lemonade, sleepy-lemonade, ...', DIM),
    ('  Timeout    : 15s / site', WHITE),
    ('──────────────────────────────────────────────────────────', DIM),
]
frames.append((draw_terminal_frame(f2_lines), 800))

# Frames 3-6: Variations running
variations = [
    ("  [1/5] 'sleepy_lemonade'      ", 89, 42),
    ("  [2/5] 'sleepylemonade'       ", 74, 38),
    ("  [3/5] 'sleepy.lemonade'      ", 62, 35),
    ("  [4/5] 'sleepy-lemonade'      ", 58, 33),
    ("  [5/5] 'sleepyLemonade'       ", 45, 31),
]

for vi, (prefix, found, elapsed) in enumerate(variations):
    running_lines = list(f2_lines)
    # Add completed variations
    for j in range(vi):
        vp, vf, ve = variations[j]
        running_lines.append((f'{vp}→  {vf} found   ({ve}s)', BLUE))
    # Add current running with spinner
    running_lines.append((f'{prefix}→  searching...', GOLD))
    frames.append((draw_terminal_frame(running_lines, len(running_lines)-1), 600))

    # Completed
    done_lines = list(f2_lines)
    for j in range(vi + 1):
        vp, vf, ve = variations[j]
        done_lines.append((f'{vp}→  {vf} found   ({ve}s)', BLUE))
    frames.append((draw_terminal_frame(done_lines), 300))

# Final frame: Summary
final_lines = list(f2_lines)
for vp, vf, ve in variations:
    final_lines.append((f'{vp}→  {vf} found   ({ve}s)', BLUE))
final_lines += [
    ('──────────────────────────────────────────────────────────', DIM),
    ('  Unique platforms : 242', WHITE),
    ('  Total elapsed    : 179s', WHITE),
    ('══════════════════════════════════════════════════════════', GOLD),
    ('', WHITE),
    ('  Clue web → sleepy_lemonade_clue_web.html', GREEN),
    ('', WHITE),
    ('  ✓ Opened in browser automatically', GREEN),
]
frames.append((draw_terminal_frame(final_lines), 3000))

# Save as GIF
gif_path = os.path.join(ASSETS, 'demo_terminal.gif')
imgs = [f[0] for f in frames]
durs = [f[1] for f in frames]
imgs[0].save(gif_path, save_all=True, append_images=imgs[1:],
             duration=durs, loop=0, optimize=True)
print(f'✓ Terminal GIF → {gif_path}')


# ═══════════════════════════════════════════════════════════
#  2. Clue Web UI Mockup PNG
# ═══════════════════════════════════════════════════════════
random.seed(42)

def draw_ui_mockup():
    W, H = 1200, 700
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    LP = 210  # left panel
    TB = 52   # top bar
    BB = 44   # bottom bar
    RP = 280  # right panel

    # Top bar
    d.rectangle([0, 0, W, TB], fill=BG2)
    d.line([(0, TB), (W, TB)], fill=BORDER, width=1)
    d.text((16, 16), '线索网', fill=GOLD, font=FONT_T)
    d.text((90, 20), '│', fill=BORDER, font=FONT)
    d.text((106, 18), 'sleepy_lemonade', fill=WHITE, font=FONT_B)
    # Stats chips
    chips = [('Platforms', '242', GOLD), ('Categories', '7', GOLD),
             ('Variants', '5', GOLD), ('Elapsed', '179s', GOLD)]
    cx = 320
    for label, val, col in chips:
        d.rounded_rectangle([cx, 14, cx+110, 38], radius=12, fill=(22,27,34), outline=BORDER)
        d.text((cx+8, 17), f'{label} ', fill=GRAY, font=FONT_SM)
        d.text((cx+70, 17), val, fill=col, font=FONT_SM)
        cx += 118
    # Search box
    d.rounded_rectangle([W-RP-200, 14, W-RP-20, 38], radius=5, fill=(22,27,34), outline=BORDER)
    d.text((W-RP-190, 17), 'Search platforms…', fill=DIM, font=FONT_SM)
    # Buttons
    for bx, label in [(W-RP-10-140, '⬇ Export'), (W-RP-10-64, '⊙ Fit')]:
        d.rounded_rectangle([bx, 14, bx+60, 38], radius=5, fill=(22,27,34), outline=BORDER)
        d.text((bx+6, 17), label, fill=GRAY, font=FONT_SM)

    # Left panel
    d.rectangle([0, TB, LP, H-BB], fill=BG2)
    d.line([(LP, TB), (LP, H-BB)], fill=BORDER, width=1)

    # View mode
    y = TB + 10
    d.text((12, y), 'VIEW', fill=DIM, font=FONT_SM)
    y += 20
    for i, label in enumerate(['Web', 'Radial', 'Focus']):
        bx = 10 + i*64
        col = BLUE if i == 0 else DIM
        d.rounded_rectangle([bx, y, bx+58, y+22], radius=4,
                            fill=(31, 111, 235, 34) if i==0 else (22,27,34), outline=col if i==0 else BORDER)
        d.text((bx+12, y+4), label, fill=col, font=FONT_SM)
    y += 34

    # Variants
    d.text((12, y), 'VARIANTS', fill=DIM, font=FONT_SM)
    d.text((LP-60, y), 'click to isolate', fill=(48,54,64), font=FONT_SM)
    y += 20
    variants = [('sleepy_lemonade', 89, True), ('sleepylemonade', 74, False),
                ('sleepy.lemonade', 62, False), ('sleepy-lemonade', 58, False),
                ('sleepyLemonade', 45, False)]
    for name, count, active in variants:
        outline = BLUE if active else BORDER
        bg = (31, 111, 235, 34) if active else (22,27,34)
        d.rounded_rectangle([8, y, LP-8, y+22], radius=4, fill=bg, outline=outline)
        d.text((14, y+4), name, fill=BLUE if active else GRAY, font=FONT_SM)
        d.text((LP-36, y+4), str(count), fill=GOLD, font=FONT_SM)
        y += 26

    # Categories
    y += 8
    d.text((12, y), 'CATEGORIES', fill=DIM, font=FONT_SM)
    y += 20
    cats = [('Social', PINK, 89), ('Gaming', PURPLE, 42), ('Tech', BLUE, 38),
            ('Creative', ORANGE, 31), ('Finance', GREEN, 18), ('Forums', CYAN, 15),
            ('Academic', (255,112,67), 9)]
    for name, color, count in cats:
        d.rounded_rectangle([10, y+2, 20, y+12], radius=2, fill=(63,185,80,50), outline=(63,185,80,80))
        d.text((16, y+1), '✓', fill=GREEN, font=FONT_SM)
        d.ellipse([26, y+3, 34, y+11], fill=color)
        d.text((40, y), name, fill=GRAY, font=FONT_SM)
        d.text((LP-30, y), str(count), fill=DIM, font=FONT_SM)
        y += 20

    # Canvas area
    cx_start, cy_start = LP, TB
    cx_end, cy_end = W - RP, H - BB
    cw, ch = cx_end - cx_start, cy_end - cy_start

    # Grid
    for gx in range(cx_start, cx_end, 48):
        d.line([(gx, cy_start), (gx, cy_end)], fill=(255,255,255,5), width=1)
    for gy in range(cy_start, cy_end, 48):
        d.line([(cx_start, gy), (cx_end, gy)], fill=(255,255,255,5), width=1)

    # Draw mock graph
    center_x = cx_start + cw // 2
    center_y = cy_start + ch // 2

    # Target node (hexagon)
    def draw_hex_on(draw, cx, cy, r, fillc, outlinec):
        pts = []
        for i in range(6):
            a = (i / 6) * math.pi * 2 - math.pi / 6
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        draw.polygon(pts, fill=fillc, outline=outlinec)

    draw_hex_on(d, center_x, center_y, 28, (100, 78, 30), GOLD)
    d.text((center_x-52, center_y-6), 'sleepy_lemonade', fill=GOLD, font=FONT_SM)

    # Variant nodes
    var_positions = []
    for i in range(5):
        a = (i / 5) * math.pi * 2 - math.pi / 2
        vx = center_x + int(80 * math.cos(a))
        vy = center_y + int(80 * math.sin(a))
        var_positions.append((vx, vy))
        d.line([(center_x, center_y), (vx, vy)], fill=(88,166,255,100), width=1)
        d.ellipse([vx-10, vy-10, vx+10, vy+10], fill=(25,50,90), outline=BLUE)

    # Category nodes (diamonds)
    cat_positions = []
    cat_colors_list = [PINK, PURPLE, BLUE, ORANGE, GREEN, CYAN, (255,112,67)]
    for i in range(7):
        a = (i / 7) * math.pi * 2 - math.pi / 2
        kx = center_x + int(180 * math.cos(a))
        ky = center_y + int(180 * math.sin(a))
        cat_positions.append((kx, ky))
        col = cat_colors_list[i]
        d.line([(center_x, center_y), (kx, ky)], fill=(col[0], col[1], col[2], 60), width=1)
        # Diamond
        r = 14
        pts = [(kx, ky-r), (kx+int(r*0.85), ky), (kx, ky+r), (kx-int(r*0.85), ky)]
        d.polygon(pts, fill=(col[0]//3, col[1]//3, col[2]//3), outline=col)

    # Site nodes
    for ci, (kx, ky) in enumerate(cat_positions):
        col = cat_colors_list[ci]
        n_sites = [15, 8, 7, 5, 3, 3, 2][ci]
        spread = min(0.9, n_sites * 0.12)
        base_a = (ci / 7) * math.pi * 2 - math.pi / 2
        for si in range(n_sites):
            t = si / max(1, n_sites - 1) if n_sites > 1 else 0.5
            sa = base_a + (t - 0.5) * spread
            sr = 280 + (si % 3 - 1) * 15
            sx = center_x + int(sr * math.cos(sa))
            sy = center_y + int(sr * math.sin(sa))
            if cx_start+5 < sx < cx_end-5 and cy_start+5 < sy < cy_end-5:
                d.line([(kx, ky), (sx, sy)], fill=(col[0], col[1], col[2], 40), width=1)
                d.ellipse([sx-4, sy-4, sx+4, sy+4], fill=(col[0]//2, col[1]//2, col[2]//2), outline=col)

    # Glow effect on center
    for r in range(60, 10, -5):
        a = max(1, int(12 * (1 - r/60)))
        d.ellipse([center_x-r, center_y-r, center_x+r, center_y+r],
                  outline=(230,180,80, a))

    # Right panel
    d.rectangle([W-RP, TB, W, H-BB], fill=BG2)
    d.line([(W-RP, TB), (W-RP, H-BB)], fill=BORDER, width=1)

    # Context panel content (as if "Social" category is selected)
    rp_x = W - RP + 12
    ry = TB + 12
    d.text((rp_x, ry), '◈', fill=PINK, font=FONT_T)
    d.text((rp_x + 28, ry + 2), 'Social', fill=WHITE, font=FONT_B)
    d.rounded_rectangle([W-50, ry+2, W-12, ry+18], radius=3,
                        fill=(233,30,99,30), outline=(233,30,99,60))
    d.text((W-46, ry+3), 'CAT', fill=PINK, font=FONT_SM)
    ry += 36
    d.line([(W-RP+8, ry), (W-8, ry)], fill=BORDER, width=1)
    ry += 8

    d.text((rp_x, ry), 'CATEGORY INFO', fill=DIM, font=FONT_SM)
    ry += 20
    d.text((rp_x, ry), 'Platforms in category', fill=GRAY, font=FONT_SM)
    d.text((W-40, ry), '89', fill=WHITE, font=FONT_SM)
    ry += 18
    d.text((rp_x, ry), 'Variants that found any', fill=GRAY, font=FONT_SM)
    d.text((W-30, ry), '5', fill=WHITE, font=FONT_SM)
    ry += 28
    d.line([(W-RP+8, ry), (W-8, ry)], fill=BORDER, width=1)
    ry += 8

    d.text((rp_x, ry), 'SITES (89) — click to open', fill=DIM, font=FONT_SM)
    ry += 20
    sites = ['TikTok', 'Instagram', 'Twitter', 'Facebook', 'Snapchat',
             'LinkedIn', 'Pinterest', 'Tumblr', 'VK', 'Mastodon']
    for s in sites:
        d.ellipse([rp_x, ry+3, rp_x+6, ry+9], fill=PINK)
        d.text((rp_x+12, ry), s, fill=GRAY, font=FONT_SM)
        src = random.choice(variants[:3])[0]
        d.text((W-90, ry), src[:12], fill=(48,54,64), font=FONT_SM)
        ry += 18
        if ry > H - BB - 60:
            d.text((rp_x, ry), '+79 more', fill=DIM, font=FONT_SM)
            break

    # Bottom bar
    d.rectangle([0, H-BB, W, H], fill=BG2)
    d.line([(0, H-BB), (W, H-BB)], fill=BORDER, width=1)

    # Breadcrumb
    bc = [('sleepy_lemonade', GOLD), ('›', DIM), ('sleepy_lemonade', BLUE),
          ('›', DIM), ('Social', PINK)]
    bx = 16
    by = H - BB + 14
    for text, col in bc:
        d.text((bx, by), text, fill=col, font=FONT_SM)
        bx += len(text) * 7 + 6

    # Minimap placeholder
    mx, my = W - 176, H - BB + 6
    d.rounded_rectangle([mx, my, mx+160, my+32], radius=3, fill=(7,10,15), outline=BORDER)
    # Mini dots
    for _ in range(25):
        px = mx + random.randint(10, 150)
        py = my + random.randint(4, 28)
        col = random.choice([PINK, PURPLE, BLUE, ORANGE, GREEN, GOLD])
        d.ellipse([px-1, py-1, px+1, py+1], fill=col)
    # Viewport rect
    d.rectangle([mx+40, my+6, mx+110, my+26], outline=(88,166,255,80))

    return img

ui_img = draw_ui_mockup()
ui_path = os.path.join(ASSETS, 'clue_web_ui.png')
ui_img.save(ui_path, optimize=True)
print(f'✓ UI Mockup  → {ui_path}')

# ═══════════════════════════════════════════════════════════
#  3. Banner image
# ═══════════════════════════════════════════════════════════
def draw_banner():
    W, H = 1200, 300
    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # Background grid
    for x in range(0, W, 48):
        d.line([(x, 0), (x, H)], fill=(255,255,255,3), width=1)
    for y in range(0, H, 48):
        d.line([(0, y), (W, y)], fill=(255,255,255,3), width=1)

    # Radial glow
    for r in range(200, 20, -3):
        a = max(1, int(15 * (1 - r/200)))
        d.ellipse([W//2-r, H//2-r, W//2+r, H//2+r],
                  outline=(230, 180, 80, a))

    # Spider web lines from center
    cx, cy = W//2, H//2
    for i in range(24):
        a = (i / 24) * math.pi * 2
        ex = cx + int(220 * math.cos(a))
        ey = cy + int(140 * math.sin(a))
        col = [PINK, PURPLE, BLUE, ORANGE, GREEN, CYAN, GOLD][i % 7]
        d.line([(cx, cy), (ex, ey)], fill=(col[0], col[1], col[2], 30), width=1)
        # Small dot at end
        d.ellipse([ex-3, ey-3, ex+3, ey+3],
                  fill=(col[0]//2, col[1]//2, col[2]//2), outline=col)

    # Ring connections
    for ring_r in [80, 140]:
        pts = []
        for i in range(24):
            a = (i / 24) * math.pi * 2
            pts.append((cx + int(ring_r * math.cos(a)),
                        cy + int(ring_r * math.sin(a))))
        for i in range(len(pts)):
            d.line([pts[i], pts[(i+1) % len(pts)]],
                   fill=(88,166,255,20), width=1)

    # Center hex
    def draw_hex_banner(draw, cx, cy, r, fillc, outlinec):
        pts = []
        for i in range(6):
            a = (i / 6) * math.pi * 2 - math.pi / 6
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        draw.polygon(pts, fill=fillc, outline=outlinec)
    draw_hex_banner(d, cx, cy, 24, (100, 78, 30), GOLD)

    # Title text
    font_title = get_font(38)
    font_sub = get_font(16)
    d.text((cx + 50, cy - 30), '线索网', fill=GOLD, font=font_title)
    d.text((cx + 50, cy + 14), 'Clue Web — OSINT Investigation Platform', fill=GRAY, font=font_sub)
    d.text((cx + 50, cy + 36), 'Sherlock + GitNexus', fill=DIM, font=FONT_SM)

    # Left side text
    d.text((30, 30), 'Sherlock 🔍', fill=BLUE, font=font_sub)
    d.text((30, 54), '400+ platforms', fill=DIM, font=FONT_SM)
    d.text((30, H-60), 'GitNexus 🕷️', fill=GREEN, font=font_sub)
    d.text((30, H-36), '9 bugs fixed · UI inspired', fill=DIM, font=FONT_SM)

    return img

banner = draw_banner()
banner_path = os.path.join(ASSETS, 'banner.png')
banner.save(banner_path, optimize=True)
print(f'✓ Banner     → {banner_path}')

print('\n✅ All assets generated in assets/')
