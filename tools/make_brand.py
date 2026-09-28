"""Normalise the integration's brand artwork.

Home Assistant serves integration artwork from
`custom_components/<domain>/brand/<image>` through
`/api/brands/integration/{domain}/{image}`, hardcoding
`content_type: image/png`, and accepts only the names in ALLOWED_IMAGES
(`homeassistant/components/brands/const.py`). The six files written here are
the light and HiDPI variants; dark-theme requests fall back through
IMAGE_FALLBACKS, so `dark_*` are produced for crispness rather than necessity.

The mark itself — the operator's house glyph and the Home Assistant blue
combined — is authored by hand and passed in as a PNG. This script only
normalises it, so the shipped pixels are the original artwork:

* crops to the visible content, so stray transparent margins from whatever
  tool exported it do not shrink the mark inside its own canvas;
* pads to a square on transparency, because HA renders these in square slots;
* resamples with Lanczos and keeps the alpha channel.

Transparency is preserved deliberately. The mark has a white outline, so
flattening it onto white — the obvious thing to do for a PNG — would paint a
white square behind it and look wrong on a dark theme.

Usage:
    python tools/make_brand.py <source.png> [--padding 0.04]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "custom_components/my_dom_ru/brand"

# Names Home Assistant accepts, with output sizes in pixels.
OUTPUTS: dict[str, int] = {
    "icon.png": 256,
    "icon@2x.png": 512,
    "logo.png": 512,
    "logo@2x.png": 1024,
    "dark_icon.png": 256,
    "dark_logo.png": 512,
}

# Breathing room around the mark, as a fraction of the final side. A mark
# flush to the edge looks cropped once the UI rounds the corners.
DEFAULT_PADDING = 0.04


def normalise(source: Path, padding: float = DEFAULT_PADDING) -> Image.Image:
    """Return the source as a square RGBA image on transparency."""
    if not source.is_file():
        raise FileNotFoundError(source)
    with Image.open(source) as image:
        image = image.convert("RGBA")
        # getbbox() on RGBA uses the alpha channel, so this drops fully
        # transparent margins. It returns None for a fully blank image.
        bounds = image.getbbox()
        if bounds is None:
            raise ValueError(f"{source} is fully transparent")
        image = image.crop(bounds)

        side = max(image.size)
        inset = int(side * padding)
        canvas_size = side + inset * 2
        canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        canvas.paste(
            image,
            ((canvas_size - image.width) // 2, (canvas_size - image.height) // 2),
        )
        return canvas


def build(source: Path, padding: float = DEFAULT_PADDING) -> list[Path]:
    """Write every allowed brand image derived from the source."""
    master = normalise(source, padding)

    BRAND.mkdir(parents=True, exist_ok=True)
    written = []
    for name, size in OUTPUTS.items():
        destination = BRAND / name
        master.resize((size, size), Image.LANCZOS).save(
            destination, "PNG", optimize=True
        )
        written.append(destination)
    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="the artwork PNG")
    parser.add_argument(
        "--padding",
        type=float,
        default=DEFAULT_PADDING,
        help="margin as a fraction of the side (default 0.04)",
    )
    args = parser.parse_args()
    for written in build(args.source, args.padding):
        print(f"{written.relative_to(ROOT)}: {written.stat().st_size} bytes")
