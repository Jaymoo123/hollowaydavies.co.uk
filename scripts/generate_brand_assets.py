"""
Generate brand assets for UK Business Accountants.

Outputs (overwrites existing):
  web/public/brand/primary-logo.png     wordmark "UK Business Accountants" + accent dot
  web/public/brand/logo.png             same wordmark, smaller
  web/public/brand/icon.png             square monogram "uba" with orange accent
  web/public/brand/icon-alt.png         alternative monogram (inverse: white on orange)
  web/public/favicon.ico                multi-size 16/32/48
  web/public/apple-touch-icon.png       180x180
  web/public/icon-192.png               PWA icon 192x192
  web/public/icon-512.png               PWA icon 512x512
  web/public/og-default.png             1200x630 default OG image

Also emits SVG sources (sharper at any size) to web/public/brand/.

Palette from generalist_design_system memory:
  Surface (off-white)        #fafaf7
  Ink (text)                 #0a0a0a
  Accent (orange)            #f97316

Typography: Geist Sans (loaded from web/node_modules/geist/dist/fonts/geist-sans/)
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
PUBLIC = WEB / "public"
BRAND_DIR = PUBLIC / "brand"
FONT_DIR = WEB / "node_modules" / "geist" / "dist" / "fonts" / "geist-sans"

# Locked design tokens
SURFACE = (250, 250, 247)   # #fafaf7
INK     = (10, 10, 10)      # #0a0a0a
ACCENT  = (249, 115, 22)    # #f97316 orange-500
INK_TRANSPARENT = SURFACE   # for transparent fallback we use surface


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    """Load Geist Sans at the requested weight."""
    file_map = {
        "regular": "Geist-Regular.ttf",
        "medium":  "Geist-Medium.ttf",
        "semibold": "Geist-SemiBold.ttf",
        "bold":    "Geist-Bold.ttf",
        "black":   "Geist-Black.ttf",
    }
    p = FONT_DIR / file_map[weight]
    return ImageFont.truetype(str(p), size)


# ---------------------------------------------------------------------------
# Wordmark
# ---------------------------------------------------------------------------

def make_wordmark(width: int = 1240, height: int = 280, transparent: bool = False) -> Image.Image:
    """Wordmark: small orange square + 'Holloway Davies' in Geist SemiBold ink."""
    bg = (0, 0, 0, 0) if transparent else SURFACE
    mode = "RGBA" if transparent else "RGB"
    img = Image.new(mode, (width, height), bg)
    draw = ImageDraw.Draw(img)

    text = "Holloway Davies"
    # Target the wordmark fills ~80% of width
    size = 96
    f = font("semibold", size)
    # Iteratively size down to fit
    while draw.textlength(text, font=f) > width * 0.80:
        size -= 2
        f = font("semibold", size)

    bbox = draw.textbbox((0, 0), text, font=f)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Layout: [orange-square] [wordmark]
    square_size = int(size * 0.55)
    gap = int(size * 0.30)
    total_w = square_size + gap + text_w

    x = (width - total_w) // 2
    y = (height - text_h) // 2 - bbox[1]  # adjust for font ascent

    # Orange accent square, baseline-aligned to the wordmark mid-line
    sq_y = y + bbox[1] + (text_h - square_size) // 2
    draw.rectangle([x, sq_y, x + square_size, sq_y + square_size], fill=ACCENT)

    draw.text((x + square_size + gap, y), text, font=f, fill=INK)
    return img


# ---------------------------------------------------------------------------
# Square monogram icon
# ---------------------------------------------------------------------------

def make_icon(size: int = 512, inverse: bool = False, transparent: bool = False) -> Image.Image:
    """Square icon. Standard variant: 'uba' lowercase ink on off-white with orange dot accent.
    Inverse: white on orange."""
    if inverse:
        bg = ACCENT
        text_color = SURFACE
        dot_color = SURFACE
    elif transparent:
        bg = (0, 0, 0, 0)
        text_color = INK
        dot_color = ACCENT
    else:
        bg = SURFACE
        text_color = INK
        dot_color = ACCENT

    mode = "RGBA" if transparent else "RGB"
    img = Image.new(mode, (size, size), bg)
    draw = ImageDraw.Draw(img)

    text = "hd"
    # Pick a font size that fills ~60% of width
    fs = int(size * 0.55)
    f = font("bold", fs)
    while draw.textlength(text, font=f) > size * 0.62:
        fs -= 4
        f = font("bold", fs)

    bbox = draw.textbbox((0, 0), text, font=f)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (size - text_w) // 2 - bbox[0]
    y = (size - text_h) // 2 - bbox[1] - int(size * 0.02)  # nudge up to leave room for dot

    draw.text((x, y), text, font=f, fill=text_color)

    # Accent dot: small square below the wordmark, centered horizontally
    dot_size = max(8, int(size * 0.10))
    dot_x = (size - dot_size) // 2
    dot_y = y + text_h + bbox[1] + int(size * 0.05)
    draw.rectangle([dot_x, dot_y, dot_x + dot_size, dot_y + dot_size], fill=dot_color)

    return img


# ---------------------------------------------------------------------------
# OG default image (1200x630)
# ---------------------------------------------------------------------------

def make_og(width: int = 1200, height: int = 630) -> Image.Image:
    img = Image.new("RGB", (width, height), SURFACE)
    draw = ImageDraw.Draw(img)

    margin = 80
    bar_w = 12
    content_w = width - margin * 2 - bar_w

    # Eyebrow
    eyebrow = "HOLLOWAY DAVIES"
    f_eyebrow = font("medium", 28)
    draw.rectangle([margin, 95, margin + 36, 95 + 36], fill=ACCENT)
    draw.text((margin + 60, 90), eyebrow, font=f_eyebrow, fill=INK)

    # Headline. Auto-fit: shrink until the longest line fits the content width.
    headline_lines = ["ICAEW qualified accountants", "for UK businesses", "of every shape."]
    size = 78
    while size > 32:
        f_headline = font("semibold", size)
        longest = max(draw.textlength(ln, font=f_headline) for ln in headline_lines)
        if longest <= content_w:
            break
        size -= 2
    f_headline = font("semibold", size)
    y = 215
    for ln in headline_lines:
        draw.text((margin, y), ln, font=f_headline, fill=INK)
        y += int(size * 1.18)

    # Footer URL
    f_url = font("medium", 26)
    url_text = "hollowaydavies.co.uk"
    draw.text((margin, height - 75), url_text, font=f_url, fill=INK)

    # Right-edge orange bar
    draw.rectangle([width - bar_w, 0, width, height], fill=ACCENT)

    return img


# ---------------------------------------------------------------------------
# SVG sources (vector, browser-renderable)
# ---------------------------------------------------------------------------

WORDMARK_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1240 280" width="1240" height="280">
  <rect width="1240" height="280" fill="#fafaf7"/>
  <rect x="160" y="118" width="50" height="50" fill="#f97316"/>
  <text x="240" y="180" font-family="Geist, 'Geist Sans', system-ui, sans-serif" font-weight="600" font-size="96" fill="#0a0a0a" letter-spacing="-1.5">UK Business Accountants</text>
</svg>
"""

ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <rect width="512" height="512" fill="#fafaf7"/>
  <text x="256" y="305" font-family="Geist, 'Geist Sans', system-ui, sans-serif" font-weight="700" font-size="280" fill="#0a0a0a" text-anchor="middle" letter-spacing="-8">hd</text>
  <rect x="232" y="360" width="48" height="48" fill="#f97316"/>
</svg>
"""

ICON_INVERSE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <rect width="512" height="512" fill="#f97316"/>
  <text x="256" y="305" font-family="Geist, 'Geist Sans', system-ui, sans-serif" font-weight="700" font-size="280" fill="#fafaf7" text-anchor="middle" letter-spacing="-8">hd</text>
  <rect x="232" y="360" width="48" height="48" fill="#fafaf7"/>
</svg>
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect width="64" height="64" fill="#f97316"/>
  <text x="32" y="42" font-family="Geist, 'Geist Sans', system-ui, sans-serif" font-weight="700" font-size="36" fill="#fafaf7" text-anchor="middle" letter-spacing="-1">hd</text>
</svg>
"""


def main():
    BRAND_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating SVGs...")
    (BRAND_DIR / "wordmark.svg").write_text(WORDMARK_SVG, encoding="utf-8")
    (BRAND_DIR / "icon.svg").write_text(ICON_SVG, encoding="utf-8")
    (BRAND_DIR / "icon-alt.svg").write_text(ICON_INVERSE_SVG, encoding="utf-8")
    (PUBLIC / "icon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    print(f"  wrote {BRAND_DIR / 'wordmark.svg'}")
    print(f"  wrote {BRAND_DIR / 'icon.svg'}")
    print(f"  wrote {BRAND_DIR / 'icon-alt.svg'}")
    print(f"  wrote {PUBLIC / 'icon.svg'}")

    print("\nGenerating PNG wordmarks...")
    primary = make_wordmark(1240, 280)
    primary.save(BRAND_DIR / "primary-logo.png", "PNG", optimize=True)
    print(f"  wrote {BRAND_DIR / 'primary-logo.png'}  ({primary.size})")

    small = make_wordmark(620, 140)
    small.save(BRAND_DIR / "logo.png", "PNG", optimize=True)
    print(f"  wrote {BRAND_DIR / 'logo.png'}  ({small.size})")

    print("\nGenerating PNG icons...")
    icon = make_icon(512, inverse=False)
    icon.save(BRAND_DIR / "icon.png", "PNG", optimize=True)
    print(f"  wrote {BRAND_DIR / 'icon.png'}  ({icon.size})")

    icon_alt = make_icon(512, inverse=True)
    icon_alt.save(BRAND_DIR / "icon-alt.png", "PNG", optimize=True)
    print(f"  wrote {BRAND_DIR / 'icon-alt.png'}  ({icon_alt.size})")

    print("\nGenerating favicons + apple-touch-icon + PWA icons...")
    # Favicon ICO (multi-size, uses the inverse icon for higher contrast at small sizes)
    fav_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
    fav_imgs = []
    for sz in fav_sizes:
        i = make_icon(sz[0], inverse=True)
        fav_imgs.append(i)
    fav_imgs[0].save(PUBLIC / "favicon.ico", format="ICO", sizes=fav_sizes,
                     append_images=fav_imgs[1:])
    print(f"  wrote {PUBLIC / 'favicon.ico'}  (16/32/48/64)")

    apple = make_icon(180, inverse=True)
    apple.save(PUBLIC / "apple-touch-icon.png", "PNG", optimize=True)
    print(f"  wrote {PUBLIC / 'apple-touch-icon.png'}  ({apple.size})")

    pwa192 = make_icon(192, inverse=True)
    pwa192.save(PUBLIC / "icon-192.png", "PNG", optimize=True)
    pwa512 = make_icon(512, inverse=True)
    pwa512.save(PUBLIC / "icon-512.png", "PNG", optimize=True)
    print(f"  wrote {PUBLIC / 'icon-192.png'}  /  {PUBLIC / 'icon-512.png'}")

    print("\nGenerating OG default image...")
    og = make_og(1200, 630)
    og.save(PUBLIC / "og-default.png", "PNG", optimize=True)
    print(f"  wrote {PUBLIC / 'og-default.png'}  ({og.size})")

    print("\nDone.")


if __name__ == "__main__":
    main()
