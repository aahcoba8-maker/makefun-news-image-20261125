#!/usr/bin/env python3
"""The World in One Day - Wednesday 25 November 2026.

Draws a 1024x1024 broadsheet PNG summing up the day's world news:
50 dated stories across 7 regions, 3 drawn lead panels, a numbered
pin map, a UTC timeline band and a date-check footer.

Stdlib only at the top level. Pillow is imported lazily; if it is not
available the program copies the pre-rendered image bundled in
assets/entry.png instead. No network, no randomness, no clock reads:
the same input always produces the same bytes.

Output: $MAKEFUN_OUTPUT_DIR/entry.png when that variable is set,
otherwise ./output/entry.png next to this script.
"""

import os
import shutil
import sys

W, H = 1024, 1024

# ---------------------------------------------------------------- data
# (number, dateline city, latitude, longitude, region, headline, source, date)
# Headlines are kept short so they fit one grid line. Every story is dated
# 24 or 25 November 2026 and carries its reporting source.
STORIES = [
    (1, "Riyadh", 24.7136, 46.6753, "ME",
     "Houthi drone hits Riyadh PIF Tower; 11 hurt", "REUTERS", "24 NOV"),
    (2, "Aden", 12.7855, 45.0187, "ME",
     "Houthis 60 km from Aden; army says city holds", "REUTERS", "25 NOV"),
    (3, "Hormuz", 26.5000, 56.2500, "ME",
     "IRGC mines hit three tankers in Hormuz", "REUTERS", "25 NOV"),
    (4, "Sanaa", 15.3694, 44.1910, "ME",
     "Houthis report dozens dead in Saudi airstrikes", "HORIZON", "24 NOV"),
    (5, "Abu Dhabi", 24.4539, 54.3773, "ME",
     "UAE condemns Houthi attack on Riyadh tower", "REUTERS", "25 NOV"),
    (6, "Qeshm", 26.8000, 55.9000, "ME",
     "Blast over Iran's Qeshm Island; defences blamed", "JPOST", "25 NOV"),
    (7, "Gaza", 31.5000, 34.4700, "ME",
     "Oxfam: Gaza turned into a 'toxic land'", "HORIZON", "24 NOV"),
    (8, "Doha", 25.2854, 51.5310, "ME",
     "US and Qatar discuss strategic cooperation", "JAGRAN JOSH", "25 NOV"),
    (9, "Tehran", 35.6892, 51.3890, "ME",
     "Iran strikes Gulf sites, sues for $290bn", "SPYGLASS", "24 NOV"),
    (10, "Ras al-Khaimah", 25.6744, 55.9804, "ME",
     "Coach crash kills 11 in Ras al-Khaimah", "HORIZON", "24 NOV"),
    (11, "Benghazi", 32.1200, 20.0700, "AFR",
     "Ukraine sinks Russian warship Merkury off Libya", "REUTERS", "24 NOV"),
    (12, "Tripoli", 32.8872, 13.1913, "AFR",
     "Libya demands answers from Kyiv over ship strikes", "HORIZON", "24 NOV"),
    (13, "Tripoli", 32.8872, 13.1913, "AFR",
     "Libya's frozen conflict risks new flare-ups", "REUTERS", "25 NOV"),
    (14, "Maiduguri", 11.8333, 13.1500, "AFR",
     "Borno school enrolment nearly doubles", "HORIZON", "24 NOV"),
    (15, "Kyiv", 50.4501, 30.5234, "EUR",
     "Russian drone attack on Kyiv town kills 11", "SPYGLASS", "24 NOV"),
    (16, "Gulf of Finland", 59.9000, 25.0000, "EUR",
     "Zelenskiy confirms hit on Russian cargo ship", "REUTERS", "25 NOV"),
    (17, "Berlin", 52.5200, 13.4050, "EUR",
     "Most Germans now oppose military aid to Ukraine", "REUTERS", "25 NOV"),
    (18, "Moscow", 55.7558, 37.6173, "EUR",
     "Putin vows retaliation over refinery strikes", "REUTERS", "25 NOV"),
    (19, "Brussels", 50.8503, 4.3517, "EUR",
     "EU announces new sanctions against Russia", "JAGRAN JOSH", "25 NOV"),
    (20, "Sandringham", 52.8300, 0.5100, "EUR",
     "Intruders breach Anmer Hall on royal estate", "TRUE STORY", "25 NOV"),
    (21, "London", 51.5074, -0.1278, "EUR",
     "England launches largest AI cancer trial", "SPYGLASS", "24 NOV"),
    (22, "Madrid", 40.4168, -3.7038, "EUR",
     "Spain's right set to oust Sanchez in Nov 29 vote", "SPYGLASS", "24 NOV"),
    (23, "Helsinki", 60.1699, 24.9384, "EUR",
     "Finland summons envoy over airspace breach", "SPYGLASS", "24 NOV"),
    (24, "Warsaw", 52.2297, 21.0122, "EUR",
     "NATO plans early-warning jets for Poland", "JAGRAN JOSH", "25 NOV"),
    (25, "Burgas", 42.5048, 27.4626, "EUR",
     "Santas wash ashore from drone-hit container", "REUTERS", "25 NOV"),
]

STORIES += [
    (26, "Geneva", 46.2044, 6.1432, "EUR",
     "UN: AI risks need global rules within a year", "HORIZON", "24 NOV"),
    (27, "London", 51.5074, -0.1278, "EUR",
     "England beat Australia by 8 wickets in 2nd T20", "JAGRAN JOSH", "25 NOV"),
    (28, "Washington", 38.9072, -77.0369, "NA",
     "CIA, ODNI hit by breach of unclassified system", "REUTERS", "25 NOV"),
    (29, "New York", 40.7128, -74.0060, "NA",
     "Huawei guilty on 10 of 12 counts in US trial", "REUTERS", "24 NOV"),
    (30, "New York", 40.7128, -74.0060, "NA",
     "Nvidia reinstates Huang as CEO; shares jump 37%", "SPYGLASS", "24 NOV"),
    (31, "Washington", 38.9072, -77.0369, "NA",
     "US blacklists Singapore chip firm Megaspeed", "SPYGLASS", "24 NOV"),
    (32, "Fort Hood", 31.1300, -97.7700, "NA",
     "Fort Hood gunman seeks stay of execution", "REUTERS", "25 NOV"),
    (33, "Washington", 38.9072, -77.0369, "NA",
     "Trump awards Giuliani Medal of Freedom", "HUDDLEWORLD", "25 NOV"),
    (34, "Iowa", 41.8780, -93.0970, "NA",
     "US Army to detonate 4 tonnes of lead azide", "TRUE STORY", "25 NOV"),
    (35, "Pennsylvania", 40.0000, -77.5000, "NA",
     "Measles outbreak claims ninth death in Pa.", "HORIZON", "24 NOV"),
    (36, "Ottawa", 45.4215, -75.6972, "NA",
     "Canada among 14 backing ICJ Rohingya ruling", "HORIZON", "24 NOV"),
    (37, "Cartagena", 10.3910, -75.4790, "LATAM",
     "Gunmen hold 25 hostages in Cartagena market", "REUTERS", "25 NOV"),
    (38, "Caracas", 10.4806, -66.9036, "LATAM",
     "Venezuela reports $237.5bn public debt", "REUTERS", "25 NOV"),
    (39, "Villavicencio", 4.1500, -73.6300, "LATAM",
     "Car bomb wrecks buildings; no victims confirmed", "HORIZON", "24 NOV"),
    (40, "Havana", 23.1136, -82.3666, "LATAM",
     "WHO chief visits Cuba's ailing health system", "HORIZON", "24 NOV"),
    (41, "Havana", 23.1136, -82.3666, "LATAM",
     "WHO chief urges US to lift Cuba oil blockade", "REUTERS", "25 NOV"),
    (42, "Beijing", 39.9042, 116.4074, "ASIA",
     "China launches Shenzhou-24 with Pakistani astronaut", "TRUE STORY", "25 NOV"),
    (43, "Seoul", 37.5665, 126.9780, "ASIA",
     "Russian jets enter S. Korea air zone; alert issued", "REUTERS", "25 NOV"),
    (44, "Kathmandu", 27.7172, 85.3240, "ASIA",
     "5.6 quake strikes Nepal near China border", "HORIZON", "24 NOV"),
    (45, "New Delhi", 28.6139, 77.2090, "ASIA",
     "India pledges Rs 15,000cr aid to Nepal", "JAGRAN JOSH", "25 NOV"),
    (46, "Chandigarh", 30.7333, 76.7794, "ASIA",
     "BJP, Akali Dal reunite for Punjab 2027 polls", "JAGRAN JOSH", "25 NOV"),
    (47, "Yangon", 16.8409, 96.1735, "ASIA",
     "14 nations back ICJ ruling on Rohingya genocide", "HORIZON", "24 NOV"),
    (48, "New Delhi", 28.6139, 77.2090, "ASIA",
     "Gukesh to face Sindarov in world chess title", "JAGRAN JOSH", "25 NOV"),
    (49, "Canberra", -35.2809, 149.1300, "OCE",
     "Australia CPI jumps to 4.9%; RBA hike risk", "ABS / 9NEWS", "25 NOV"),
    (50, "Sydney", -33.8688, 151.2093, "OCE",
     "Australia jobless 4.9%, worst since Oct 2021", "HCA MAG", "25 NOV"),
]

# (key, label, colour) - order is the legend order.
REGIONS = [
    ("ME", "MIDDLE EAST", (193, 18, 31)),
    ("EUR", "EUROPE", (29, 78, 216)),
    ("NA", "NORTH AMERICA", (14, 116, 144)),
    ("LATAM", "LATIN AMERICA", (21, 128, 61)),
    ("AFR", "AFRICA", (180, 83, 9)),
    ("ASIA", "ASIA", (124, 58, 237)),
    ("OCE", "OCEANIA", (190, 24, 93)),
]
REGION_COLOR = {k: c for k, _label, c in REGIONS}

# Three leads, drawn as illustrated panels.
LEADS = [
    {
        "num": 1, "art": "tower", "kicker": "MIDDLE EAST  ·  RIYADH",
        "head": "Houthi drone hits Riyadh tower",
        "body": "Second strike on the PIF Tower in a week; 11 hurt, Saudi Civil Defence says.",
        "tag": "REUTERS  ·  24 NOV",
    },
    {
        "num": 49, "art": "chart", "kicker": "OCEANIA  ·  CANBERRA",
        "head": "Australia inflation hits 4.9%",
        "body": "CPI up from 4.3% as fuel and food climb; trimmed mean 3.8%.",
        "tag": "ABS  ·  25 NOV",
    },
    {
        "num": 29, "art": "court", "kicker": "NORTH AMERICA  ·  NEW YORK",
        "head": "Huawei guilty on 10 of 12 counts",
        "body": "Brooklyn jury convicts on trade secrets and bank fraud.",
        "tag": "REUTERS / BBC  ·  24 NOV",
    },
]

# Simplified continent outlines, (lon, lat) pairs, equirectangular.
NORTH_AMERICA = [(-168, 66), (-158, 58), (-140, 60), (-130, 54), (-124, 40),
    (-117, 32), (-108, 25), (-97, 16), (-90, 14), (-83, 9), (-79, 9),
    (-83, 15), (-88, 16), (-91, 19), (-97, 26), (-90, 29), (-84, 30),
    (-81, 26), (-76, 35), (-70, 42), (-65, 44), (-60, 47), (-55, 52),
    (-60, 55), (-65, 59), (-75, 62), (-85, 66), (-95, 69), (-110, 68),
    (-125, 70), (-145, 70), (-160, 71), (-168, 66)]
GREENLAND = [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70),
    (-25, 76), (-40, 80), (-55, 80), (-58, 76), (-58, 70), (-55, 60)]
SOUTH_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
    (-72, -18), (-70, -23), (-70, -30), (-73, -44), (-70, -54), (-66, -55),
    (-64, -41), (-58, -35), (-52, -32), (-48, -27), (-41, -23), (-39, -17),
    (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4),
    (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-76, 10), (-79, 9)]
AFRICA = [(-17, 15), (-15, 20), (-13, 27), (-9, 32), (-5, 35), (0, 36),
    (10, 37), (11, 34), (19, 32), (25, 32), (30, 31), (32, 31), (34, 27),
    (37, 20), (39, 15), (43, 12), (48, 11), (51, 12), (48, 7), (42, 0),
    (40, -6), (38, -12), (36, -18), (33, -26), (28, -33), (20, -35),
    (17, -30), (14, -22), (12, -12), (13, -6), (9, 4), (4, 6), (-3, 5),
    (-8, 5), (-13, 8), (-17, 12), (-17, 15)]
EURASIA = [(-10, 36), (-9, 37), (-9, 43), (-2, 44), (-1, 46), (3, 43),
    (7, 44), (12, 44), (16, 41), (19, 42), (23, 40), (26, 39), (28, 41),
    (30, 36), (33, 36), (36, 36), (36, 33), (35, 31), (34, 28), (38, 22),
    (42, 16), (44, 12), (48, 14), (52, 15), (55, 17), (58, 20), (60, 23),
    (58, 25), (56, 27), (52, 28), (49, 30), (48, 30), (44, 29), (40, 26),
    (37, 24), (35, 20), (32, 17), (28, 15), (24, 12), (21, 9), (18, 7),
    (15, 5), (12, 4), (10, 2), (8, 4), (5, 5), (2, 6), (0, 6), (-2, 5),
    (-5, 4), (-8, 5), (-10, 6), (-13, 8), (-16, 11), (-17, 14), (-17, 18),
    (-16, 22), (-15, 27), (-13, 31), (-10, 33), (-6, 35), (-10, 36)]

UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
    (1, 51), (-2, 50), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 35), (140, 38),
    (141, 41), (141, 44), (143, 43), (141, 40), (139, 37), (137, 36),
    (134, 34), (131, 33), (130, 31)]
AUSTRALIA = [(114, -22), (114, -30), (115, -35), (118, -35), (124, -33),
    (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38),
    (150, -37), (153, -32), (153, -27), (150, -23), (146, -19), (142, -15),
    (142, -11), (140, -17), (136, -15), (135, -12), (132, -11), (130, -13),
    (126, -14), (122, -17), (118, -20), (114, -22)]
NEW_ZEALAND = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
    (175, -41), (172, -43), (168, -46), (167, -45)]
BORNEO = [(109, 1), (111, -2), (114, -3), (117, -1), (119, 1), (117, 4),
    (114, 4), (110, 2), (109, 1)]
SUMATRA = [(95, 5), (98, 3), (100, 0), (103, -3), (105, -5), (104, -6),
    (102, -4), (100, -1), (97, 3), (95, 5)]
JAVA = [(105, -6), (108, -7), (111, -7), (114, -8), (112, -8), (109, -7),
    (106, -6), (105, -6)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -8),
    (147, -9), (143, -8), (140, -8), (136, -6), (132, -3), (131, -1)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (50, -20), (48, -24),
    (45, -25), (43, -22), (43, -18), (44, -16)]
LAND = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA, UK,
        JAPAN, AUSTRALIA, NEW_ZEALAND, BORNEO, SUMATRA, JAVA, NEW_GUINEA,
        MADAGASCAR]

# ---------------------------------------------------------------- style
PAPER = (247, 243, 234)
INK = (20, 33, 61)
INK_SOFT = (58, 68, 92)
RULE = (20, 33, 61)
RED = (193, 18, 31)
MUTED = (110, 108, 100)
CARD = (255, 255, 255)
CARD_LINE = (201, 194, 178)
MAP_BG = (214, 226, 236)
LAND_FILL = (233, 226, 208)
LAND_LINE = (178, 168, 143)
GRID_LINE = (226, 220, 205)
NIGHT = (16, 24, 48)
NIGHT2 = (28, 42, 84)

# Timeline markers: (story number, label, segment, hour or None).
# Segments: "late" = late Tuesday 24 Nov (UTC evening), "day" = 25 Nov UTC.
# Hours are shown only where the reporting time is confirmed.
TIMELINE = [
    (1, "RIYADH HIT", "late", None),
    (29, "HUAWEI VERDICT", "late", None),
    (49, "AU CPI 4.9%", "day", 0.5),
    (42, "SHENZHOU-24", "day", None),
    (43, "KOREA ALERT", "day", None),
    (37, "CARTAGENA", "day", None),
    (28, "CIA BREACH", "day", None),
    (2, "ADEN FRONT", "day", None),
]


def _here():
    return os.path.dirname(os.path.abspath(__file__))


def load_fonts():
    """Return {(bold, size): font}. Bundled subsets first, system DejaVu
    second, Pillow's built-in bitmap font last."""
    from PIL import ImageFont

    cache = {}

    def get(bold, size):
        key = (bold, size)
        if key in cache:
            return cache[key]
        names = []
        if bold:
            names = ["fonts/DejaVuSans-Bold.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        else:
            names = ["fonts/DejaVuSans.ttf",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        font = None
        for name in names:
            path = name if os.path.isabs(name) else os.path.join(_here(), name)
            try:
                font = ImageFont.truetype(path, size)
                break
            except Exception:
                continue
        if font is None:
            font = ImageFont.load_default()
        cache[key] = font
        return font

    return get


def text_w(draw, text, font):
    left, _top, right, _bot = draw.textbbox((0, 0), text, font=font)
    return right - left


def fit_text(draw, text, font, max_w):
    """Shorten text with an ellipsis until it fits max_w."""
    if text_w(draw, text, font) <= max_w:
        return text
    while len(text) > 4 and text_w(draw, text + "...", font) > max_w:
        text = text[:-1]
    return text + "..."


def wrap_text(draw, text, font, max_w):
    """Greedy word wrap, returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- leads
def draw_tower(draw, x, y, w, h):
    """Night skyline: the PIF Tower struck by a drone, drawn from shapes."""
    draw.rectangle([x, y, x + w, y + h], fill=NIGHT)
    for sx, sy in [(18, 14), (52, 26), (96, 10), (150, 22), (210, 12),
                   (262, 28), (296, 16)]:
        draw.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2],
                     fill=(240, 235, 210))
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=(10, 15, 34))
    # neighbouring blocks
    for bx, bw, bh in [(6, 26, 34), (40, 20, 46), (250, 24, 40), (284, 18, 30)]:
        draw.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26],
                       fill=NIGHT2)
        for wy in range(y + h - 22 - bh, y + h - 28, 8):
            draw.rectangle([x + bx + 5, wy, x + bx + 8, wy + 3],
                           fill=(240, 220, 120))
    # the tower: tapered, stepped crown, lit windows
    tx = x + w // 2
    draw.polygon([(tx - 26, y + h - 26), (tx - 13, y + 16), (tx + 13, y + 16),
                  (tx + 26, y + h - 26)], fill=(52, 66, 112))
    draw.polygon([(tx - 13, y + 16), (tx - 8, y + 6), (tx + 8, y + 6),
                  (tx + 13, y + 16)], fill=(72, 88, 140))
    draw.rectangle([tx - 2, y + 2, tx + 2, y + 8], fill=(240, 220, 120))
    for wy in range(y + 30, y + h - 34, 10):
        draw.rectangle([tx - 7, wy, tx - 3, wy + 4], fill=(240, 220, 120))
        draw.rectangle([tx + 3, wy, tx + 7, wy + 4], fill=(240, 220, 120))
    # drone + blast marks near the crown
    draw.ellipse([tx + 30, y + 20, tx + 36, y + 26], fill=(255, 90, 60))
    draw.line([tx + 24, y + 23, tx + 30, y + 23], fill=(255, 140, 90), width=2)
    draw.line([tx + 36, y + 23, tx + 42, y + 23], fill=(255, 140, 90), width=2)
    draw.line([tx + 33, y + 14, tx + 33, y + 20], fill=(255, 140, 90), width=2)
    draw.line([tx + 33, y + 26, tx + 33, y + 32], fill=(255, 140, 90), width=2)


def draw_chart(draw, x, y, w, h, get):
    """CPI chart: rising line, 4.9% callout, bar row."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 240, 244))
    draw.rectangle([x, y, x + w, y + 30], fill=INK)
    draw.text((x + 10, y + 7), "AUSTRALIA  ·  CPI, YEAR TO OCTOBER",
              font=get(True, 11), fill=(255, 255, 255))
    pts = [(x + 18, y + h - 30), (x + 62, y + h - 38), (x + 106, y + h - 34),
           (x + 150, y + h - 48), (x + 196, y + h - 56)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=RED, width=4)
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED)
    draw.line([x + 14, y + h - 26, x + w - 10, y + h - 26],
              fill=(150, 150, 150), width=1)
    draw.text((x + w - 108, y + 38), "4.9%", font=get(True, 40), fill=RED)
    draw.text((x + w - 118, y + 80), "from 4.3% in Sept",
              font=get(False, 11), fill=INK_SOFT)
    draw.text((x + 14, y + h - 20), "TRIMMED MEAN 3.8%",
              font=get(True, 10), fill=INK_SOFT)


def draw_court(draw, x, y, w, h, get):
    """Courthouse front: pediment, columns, verdict tag."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 228, 218))
    draw.rectangle([x, y, x + w, y + 30], fill=INK)
    draw.text((x + 10, y + 7), "UNITED STATES  ·  BROOKLYN",
              font=get(True, 11), fill=(255, 255, 255))
    cx = x + w // 2
    draw.polygon([(cx - 110, y + 52), (cx + 110, y + 52), (cx, y + 30)],
                 fill=(120, 116, 104))
    draw.ellipse([cx - 12, y + 40, cx + 12, y + 52], fill=(240, 220, 120))
    for i in range(4):
        colx = x + 52 + i * 62
        draw.rectangle([colx, y + 52, colx + 16, y + h - 8], fill=(250, 248, 242))
        draw.rectangle([colx - 3, y + 52, colx + 19, y + 58], fill=(120, 116, 104))
        draw.rectangle([colx - 3, y + h - 14, colx + 19, y + h - 8],
                       fill=(120, 116, 104))
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(120, 116, 104))
    draw.rectangle([cx - 68, y + h - 52, cx + 68, y + h - 22], fill=RED)
    draw.text((cx - 58, y + h - 46), "10 OF 12 COUNTS",
              font=get(True, 13), fill=(255, 255, 255))


def draw_lead(draw, lead, x, y, w, h, get):
    """One lead card: drawn art on top, headline + summary + tag below."""
    art_h = 110
    if lead["art"] == "tower":
        draw_tower(draw, x, y, w, art_h)
    elif lead["art"] == "chart":
        draw_chart(draw, x, y, w, art_h, get)
    else:
        draw_court(draw, x, y, w, art_h, get)
    draw.rectangle([x, y, x + w, y + h], outline=CARD_LINE, width=1)
    ty = y + art_h + 8
    draw.text((x + 10, ty), lead["kicker"], font=get(True, 10), fill=RED)
    ty += 15
    for line in wrap_text(draw, lead["head"], get(True, 14), w - 20):
        draw.text((x + 10, ty), line, font=get(True, 14), fill=INK)
        ty += 17
    body_lines = wrap_text(draw, lead["body"], get(False, 11), w - 20)[:2]
    for line in body_lines:
        draw.text((x + 10, ty), line, font=get(False, 11), fill=INK_SOFT)
        ty += 12
    draw.text((x + 10, y + h - 16), lead["tag"], font=get(True, 10),
              fill=MUTED)
    num = str(lead["num"])
    draw.ellipse([x + w - 30, y + h - 24, x + w - 8, y + h - 2],
                 fill=REGION_COLOR["ME"] if lead["num"] == 1 else
                 (REGION_COLOR["OCE"] if lead["num"] == 49 else
                  REGION_COLOR["NA"]))
    draw.text((x + w - 24, y + h - 21), num, font=get(True, 11),
              fill=(255, 255, 255))


def draw_masthead(draw, get):
    draw.rectangle([0, 0, W, 10], fill=INK)
    draw.text((16, 22), "THE WORLD IN ONE DAY", font=get(True, 40), fill=INK)
    date = "WEDNESDAY 25 NOVEMBER 2026"
    dw = text_w(draw, date, get(True, 20))
    draw.text((W - 16 - dw, 26), date, font=get(True, 20), fill=INK)
    sub = "50 STORIES  ·  7 REGIONS  ·  DATE-CHECKED"
    sw = text_w(draw, sub, get(True, 13))
    draw.text((W - 16 - sw, 52), sub, font=get(True, 13), fill=RED)
    draw.line([16, 78, W - 16, 78], fill=RULE, width=2)
    leads = ("LEADS:  RIYADH TOWER HIT  ·  AUSTRALIA CPI 4.9%  ·  "
             "HUAWEI GUILTY ON 10 OF 12 COUNTS")
    draw.text((16, 84), leads, font=get(True, 12), fill=INK_SOFT)


# ---------------------------------------------------------------- grid
def draw_section(draw, y, title, get):
    draw.text((16, y), title, font=get(True, 12), fill=RED)
    tw = text_w(draw, title, get(True, 12))
    draw.line([16 + tw + 10, y + 7, W - 16, y + 7], fill=CARD_LINE, width=1)


def draw_grid(draw, get):
    draw_section(draw, 308, "THE DAY IN 50 STORIES  —  ALL DATED, ALL SOURCED", get)
    for i, s in enumerate(STORIES):
        _n, city, _la, _lo, region, head, src, date = s
        col, row = (0, i) if i < 25 else (1, i - 25)
        x0 = 16 + col * 504
        y0 = 326 + row * 15
        if row % 2 == 0:
            draw.rectangle([x0 - 4, y0 - 1, x0 + 492, y0 + 13],
                           fill=(242, 238, 228))
        num = str(_n)
        draw.text((x0 + 20 - text_w(draw, num, get(True, 11)), y0),
                  num, font=get(True, 11), fill=REGION_COLOR[region])
        draw.text((x0 + 26, y0), fit_text(draw, head, get(False, 11), 322),
                  font=get(False, 11), fill=INK)
        draw.text((x0 + 352, y0), src, font=get(True, 8), fill=MUTED)
        draw.text((x0 + 440, y0), date, font=get(True, 8), fill=INK_SOFT)


# ---------------------------------------------------------------- map
def project(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 170.0) / 360.0 * mw
    y = my + (78.0 - lat) / 136.0 * mh
    return x, y


def draw_map(draw, get):
    draw_section(draw, 708, "WHERE IT HAPPENED  —  PIN MAP (PINS 1–50 MATCH THE STORIES)", get)
    mx, my, mw, mh = 16, 726, 992, 160
    draw.rectangle([mx, my, mx + mw, my + mh], fill=MAP_BG,
                   outline=CARD_LINE, width=1)
    for poly in LAND:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        draw.polygon(pts, fill=LAND_FILL, outline=LAND_LINE)
    placed = []
    offsets = [(0, 0), (0, -11), (0, 11), (-11, 0), (11, 0), (-11, -11),
               (11, -11), (-11, 11), (11, 11), (0, -22), (0, 22),
               (-22, 0), (22, 0), (-22, -22), (22, -22)]
    for s in STORIES:
        n, _city, lat, lon, region, _h, _s, _d = s
        bx, by = project(lon, lat, mx, my, mw, mh)
        px, py = bx, by
        for ox, oy in offsets:
            cx, cy = bx + ox, by + oy
            if all((cx - qx) ** 2 + (cy - qy) ** 2 >= 15.0 ** 2
                   for qx, qy in placed):
                px, py = cx, cy
                break
        placed.append((px, py))
        if abs(px - bx) > 3 or abs(py - by) > 3:
            draw.line([bx, by, px, py], fill=INK_SOFT, width=1)
        draw.ellipse([px - 8, py - 8, px + 8, py + 8],
                     fill=REGION_COLOR[region], outline=(255, 255, 255))
        label = str(n)
        lw = text_w(draw, label, get(True, 9))
        draw.text((px - lw / 2, py - 6), label, font=get(True, 9),
                  fill=(255, 255, 255))
    # legend strip
    ly = my + mh - 22
    draw.rectangle([mx, ly, mx + mw, my + mh], fill=(255, 255, 255))
    lx = mx + 8
    for key, label, color in REGIONS:
        draw.ellipse([lx, ly + 5, lx + 10, ly + 15], fill=color)
        cnt = sum(1 for s in STORIES if s[4] == key)
        text = "%s %d" % (label, cnt)
        draw.text((lx + 14, ly + 4), text, font=get(True, 9), fill=INK)
        lx += 14 + text_w(draw, text, get(True, 9)) + 16


# ---------------------------------------------------------------- timeline
def draw_timeline(draw, get):
    draw_section(draw, 900, "UTC TIMELINE  —  WHEN THE DAY BROKE", get)
    late_x, late_w = 16, 190
    day_x, day_w = 226, 782
    draw.text((late_x, 920), "LATE TUE 24 NOV", font=get(True, 10), fill=RED)
    draw.text((day_x, 920), "WED 25 NOV (UTC)", font=get(True, 10), fill=RED)
    bar_y = 946
    draw.rectangle([late_x, bar_y, late_x + late_w, bar_y + 8], fill=(220, 214, 198))
    draw.rectangle([day_x, bar_y, day_x + day_w, bar_y + 8], fill=(220, 214, 198))
    for h in (0, 6, 12, 18, 24):
        tx = day_x + h / 24.0 * day_w
        draw.line([tx, bar_y + 8, tx, bar_y + 13], fill=INK_SOFT, width=1)
        lab = "%02d:00" % h
        draw.text((tx - text_w(draw, lab, get(False, 8)) / 2, bar_y + 14),
                  lab, font=get(False, 8), fill=MUTED)
    late_marks = [t for t in TIMELINE if t[2] == "late"]
    for i, (n, lab, _seg, _h) in enumerate(late_marks):
        cx = late_x + (i + 1) * late_w / (len(late_marks) + 1)
        draw.ellipse([cx - 6, bar_y - 2, cx + 6, bar_y + 10],
                     fill=REGION_COLOR[STORIES[n - 1][4]])
        draw.text((cx - text_w(draw, str(n), get(True, 8)) / 2, bar_y - 14),
                  str(n), font=get(True, 8), fill=INK)
    for (n, lab, _seg, hour) in TIMELINE:
        if _seg != "day" or hour is None:
            continue
        cx = day_x + hour / 24.0 * day_w
        draw.ellipse([cx - 6, bar_y - 2, cx + 6, bar_y + 10],
                     fill=REGION_COLOR[STORIES[n - 1][4]])
        draw.text((cx - text_w(draw, str(n), get(True, 8)) / 2, bar_y - 14),
                  str(n), font=get(True, 8), fill=INK)
    chips = [t for t in TIMELINE if t[2] == "day" and t[3] is None]
    cx = day_x
    draw.text((day_x, 972), "REPORTED 25 NOV:",
              font=get(True, 9), fill=INK_SOFT)
    cx += text_w(draw, "REPORTED 25 NOV:", get(True, 9)) + 8
    for (n, lab, _seg, _h) in chips:
        tag = "#%d %s" % (n, lab)
        draw.text((cx, 972), tag, font=get(True, 9), fill=INK)
        cx += text_w(draw, tag, get(True, 9)) + 14


# ---------------------------------------------------------------- footer
def draw_footer(draw, get):
    n25 = sum(1 for s in STORIES if s[7] == "25 NOV")
    n24 = len(STORIES) - n25
    line1 = ("SOURCES: REUTERS · BBC · ABS · AL JAZEERA · HORIZON · SPYGLASS · "
             "THE TRUE STORY · JAGRAN JOSH · 9NEWS · HCA MAG")
    line2 = ("DATE CHECK: EVERY STORY DATED 24 OR 25 NOV 2026  ·  %d DATED 25 NOV  ·  "
             "%d DATED LATE 24 NOV  ·  PINS NUMBERED 1–50 TO MATCH THE STORIES"
             % (n25, n24))
    draw.text((16, 990), line1, font=get(False, 10), fill=INK_SOFT)
    draw.text((16, 1004), line2, font=get(True, 10), fill=INK)


# ---------------------------------------------------------------- render
def render_png():
    from PIL import Image, ImageDraw

    get = load_fonts()
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw, get)
    for i, lead in enumerate(LEADS):
        draw_lead(draw, lead, 16 + i * 336, 104, 320, 196, get)
    draw_grid(draw, get)
    draw_map(draw, get)
    draw_timeline(draw, get)
    draw_footer(draw, get)
    import io

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True, compress_level=9)
    return buf.getvalue()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = os.path.join(_here(), "output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    forced = os.environ.get("MAKEFUN_NO_PIL") == "1"
    data = None
    if not forced:
        try:
            data = render_png()
        except ImportError:
            data = None
    if data is None:
        bundled = os.path.join(_here(), "assets", "entry.png")
        shutil.copyfile(bundled, target)
        with open(target, "rb") as fh:
            data = fh.read()
    else:
        with open(target, "wb") as fh:
            fh.write(data)
    import hashlib

    print("wrote %s (%d bytes, sha256 %s)"
          % (target, len(data), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
