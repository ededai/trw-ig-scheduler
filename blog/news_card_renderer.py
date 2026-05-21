#!/usr/bin/env python3
"""
TRW News Card Renderer
======================
Renders branded news blog cards by compositing text onto base templates.
No external API calls. Free per run after one-time base template generation.

Base templates (2624×1632 px):
  assets/card-bases/base-coe.png  — dark card + upward bar chart
  assets/card-bases/base-lta.png  — dark card + ERP gantry icon
  assets/card-bases/logo-light.png — TRW horizontal wordmark (white/transparent)

Usage (CLI):
  python3 news_card_renderer.py coe \
      --label "SINGAPORE COE UPDATE" \
      --headline "Cat A COE May 2026" \
      --stat "Up 21% year on year" \
      --out /tmp/coe-card.png

  python3 news_card_renderer.py lta \
      --label "SINGAPORE LTA UPDATE" \
      --headline "ERP 2.0 OBU Now Mandatory" \
      --stat "From 1 Jan 2026" \
      --out /tmp/lta-card.png

Usage (module):
  from news_card_renderer import render_news_card
  path = render_news_card(
      card_type="coe",
      label="SINGAPORE COE UPDATE",
      headline="Cat A COE May 2026",
      stat="Up 21% year on year",
      out_path="/tmp/card.png",
  )
"""
from __future__ import annotations
import argparse
import os
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).parent / "assets" / "card-bases"

# Card dimensions (matches generated base templates)
W, H = 2624, 1632

# Colour palette
BG       = (36, 40, 52)       # dark card background
ORANGE   = (255, 107, 33)
WHITE    = (255, 255, 255)

# Text layout — left-side text zone, 130px left margin
MARGIN_L = 130

# Per-template config: text_zone_w, headline_font_size, headline_font_size_sm
# coe: bar chart starts at ~x=1350 → 1280px safe zone; short headline so 230px fits
# lta: gantry starts at ~x=1100 → 950px safe zone; longer headlines need smaller font
CARD_CONFIG = {
    "coe": {"zone": 1280, "font": 230, "font_sm": 195, "y_shift":  0},
    "lta": {"zone":  950, "font": 185, "font_sm": 155, "y_shift": 50},
}
CARD_CONFIG_DEFAULT = {"zone": 1100, "font": 200, "font_sm": 165, "y_shift": 0}

# Vertical positions (absolute px on 2624×1632 canvas)
Y_LABEL    = 90                # small eyebrow label
Y_HEADLINE = 210               # large headline starts here
Y_STAT     = 1150              # stat / subline
# Logo and cover are baked into base templates — no runtime compositing needed


# ── font helpers ──────────────────────────────────────────────────────────────

def _find_font(bold: bool = True) -> str:
    """Return path to a usable sans-serif TTF, platform-aware."""
    candidates = []
    if bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",    # macOS
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Ubuntu
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Ubuntu fallback
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return ""  # Pillow will use its built-in bitmap font as last resort


def _load(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


# ── text wrapping ─────────────────────────────────────────────────────────────

def _wrap_headline(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Wrap headline to fit within max_w pixels, max 2 lines.
    Any overflow beyond 2 lines is merged onto line 2 (no words dropped)."""
    words = text.split()
    lines: list[str] = []
    current = ""
    tmp_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    for word in words:
        test = (current + " " + word).strip()
        bbox = tmp_draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_w:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    # Enforce max 3 lines — merge any overflow onto line 3.
    # 2-line max caused merged lines to exceed text_zone_w on narrow zones.
    if len(lines) > 3:
        lines = [lines[0], lines[1], " ".join(lines[2:])]
    return lines or [text]


# ── main renderer ─────────────────────────────────────────────────────────────

def render_news_card(
    card_type: str,
    label: str,
    headline: str,
    stat: str,
    out_path: str | Path,
) -> str:
    """
    Render a news card PNG.

    Args:
        card_type:  "coe" | "lta"
        label:      Small eyebrow text, e.g. "SINGAPORE COE UPDATE"
        headline:   Main headline, e.g. "Cat A COE May 2026"
        stat:       Orange subline, e.g. "Up 21% year on year"
        out_path:   Output PNG path

    Returns:
        Absolute path to the saved PNG.
    """
    card_type = card_type.lower().strip()
    cfg = CARD_CONFIG.get(card_type, CARD_CONFIG_DEFAULT)
    text_zone_w = cfg["zone"]
    y_shift     = cfg["y_shift"]
    base_file = ASSETS / f"base-{card_type}.png"
    if not base_file.exists():
        raise FileNotFoundError(
            f"Base template not found: {base_file}\n"
            f"Available types: {[p.stem.replace('base-','') for p in ASSETS.glob('base-*.png')]}"
        )

    # Load base template (logo + cover already baked in by patch script)
    card = Image.open(base_file).convert("RGBA")
    draw = ImageDraw.Draw(card)

    # 1. Load fonts
    bold_font_path   = _find_font(bold=True)
    label_font       = _load(bold_font_path, 68)
    headline_font    = _load(bold_font_path, cfg["font"])
    headline_font_sm = _load(bold_font_path, cfg["font_sm"])
    stat_font        = _load(bold_font_path, 88)

    # 4. Draw label (small white caps eyebrow)
    draw.text((MARGIN_L, Y_LABEL + y_shift), label.upper(), font=label_font, fill=WHITE)

    # 5. Draw headline (wrap to text_zone_w, reduce font if needed)
    lines = _wrap_headline(headline, headline_font, text_zone_w)
    # If any line exceeds zone, shrink font and re-wrap once
    tmp_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    if any(tmp_draw.textbbox((0,0), ln, font=headline_font)[2] > text_zone_w for ln in lines):
        headline_font = headline_font_sm
        lines = _wrap_headline(headline, headline_font, text_zone_w)

    line_h = int(headline_font.size * 1.1)
    y = Y_HEADLINE + y_shift
    for ln in lines:
        draw.text((MARGIN_L, y), ln, font=headline_font, fill=WHITE)
        y += line_h

    # 6. Draw stat line in orange
    draw.text((MARGIN_L, Y_STAT + y_shift), stat, font=stat_font, fill=ORANGE)

    # 7. Save
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    card.convert("RGB").save(str(out), "PNG", optimize=False)
    return str(out.resolve())


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Render a TRW news blog card PNG without any API calls."
    )
    ap.add_argument("card_type", choices=["coe", "lta"],
                    help="Base template to use")
    ap.add_argument("--label",    required=True, help="Small eyebrow label (caps)")
    ap.add_argument("--headline", required=True, help="Main headline text")
    ap.add_argument("--stat",     required=True, help="Orange stat/subline text")
    ap.add_argument("--out",      required=True, help="Output PNG path")
    args = ap.parse_args()

    try:
        path = render_news_card(
            card_type=args.card_type,
            label=args.label,
            headline=args.headline,
            stat=args.stat,
            out_path=args.out,
        )
        print(f"Saved: {path}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
