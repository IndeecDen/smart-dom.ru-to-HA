"""Build the 1280×640 social preview card for the GitHub repository.

GitHub's REST API cannot set a repository avatar or a social preview: PATCH
/repos/{owner}/{repo} silently ignores an `avatar` field (200 OK, unchanged
`updated_at`) and POST /social_preview returns 404. Both are web-UI only, so
this writes a ready-to-upload PNG and prints where it went.

Usage:
    python tools/make_social_preview.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BRAND_LOGO = ROOT / "custom_components/my_dom_ru/brand/logo.png"
OUT = ROOT / "dist/social-preview.png"

WIDTH, HEIGHT = 1280, 640
HA_BLUE = (17, 180, 252)
INK = (26, 26, 26)
MUTED = (90, 90, 90)

TITLE = "Умный Дом.ру"
SUBTITLE = "для Home Assistant"
FOOTER = "Домофон · камеры · архив · звонок с двухсторонним звуком"

FONT_DIR = Path("C:/Windows/Fonts")


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def build() -> Path:
    """Render the card and return the path it was written to."""
    if not BRAND_LOGO.is_file():
        raise FileNotFoundError(BRAND_LOGO)

    card = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(card)

    # A slim rule along the top, in the mark's blue, ties the card to it.
    draw.rectangle([0, 0, WIDTH, 12], fill=HA_BLUE)

    logo_size = 300
    with Image.open(BRAND_LOGO) as logo:
        # Keep RGBA and paste with a mask: converting to RGB would turn the
        # mark's transparent background black instead of letting the card
        # show through.
        logo = logo.convert("RGBA").resize((logo_size, logo_size), Image.LANCZOS)
    card.paste(logo, (90, (HEIGHT - logo_size) // 2), logo)

    left = 90 + logo_size + 70
    draw.text(
        (left, 190), TITLE, font=_font("arialbd.ttf", 76), fill=INK
    )
    draw.text(
        (left, 285), SUBTITLE, font=_font("arial.ttf", 44), fill=MUTED
    )
    draw.text(
        (left, 372), FOOTER, font=_font("arial.ttf", 25), fill=MUTED
    )

    OUT.parent.mkdir(exist_ok=True)
    card.save(OUT, "PNG", optimize=True)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"{path.relative_to(ROOT)}: {path.stat().st_size} bytes")
    print(
        "Upload manually: repo -> About -> Edit -> "
        "Social preview -> Upload an image"
    )
    print("  (dist/ is gitignored, so this file stays out of the repo)")
