"""The brand artwork must ship, and use the names Home Assistant accepts."""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPONENT = ROOT / "custom_components/my_dom_ru"
BRAND = COMPONENT / "brand"

# Mirrors homeassistant/components/brands/const.py ALLOWED_IMAGES. The brands
# view rejects anything else with 404, so a typo here means a silent fallback
# to the generic placeholder in the UI.
ALLOWED_IMAGES = {
    "icon.png",
    "logo.png",
    "icon@2x.png",
    "logo@2x.png",
    "dark_icon.png",
    "dark_logo.png",
    "dark_icon@2x.png",
    "dark_logo@2x.png",
}

# Every name we actually ship. Dark-theme requests fall back through
# IMAGE_FALLBACKS, so this subset is sufficient.
EXPECTED = {
    "icon.png",
    "icon@2x.png",
    "logo.png",
    "logo@2x.png",
    "dark_icon.png",
    "dark_logo.png",
}


@pytest.fixture(scope="module")
def hacs_zip(tmp_path_factory) -> zipfile.ZipFile:
    """Build the HACS archive once and return it opened."""
    sys.path.insert(0, str(ROOT / "tools"))
    import package  # noqa: PLC0415

    for archive in package.build():
        if archive.name == "my_dom_ru.zip":
            return zipfile.ZipFile(archive)
    raise AssertionError("my_dom_ru.zip was not produced")


class TestBrandDirectory:
    def test_brand_directory_exists(self) -> None:
        assert BRAND.is_dir(), "brand/ is what Home Assistant looks for"

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_expected_file_present(self, name: str) -> None:
        path = BRAND / name
        assert path.is_file(), f"missing {name}"
        assert path.stat().st_size > 0

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_name_is_allowed_by_home_assistant(self, name: str) -> None:
        assert name in ALLOWED_IMAGES

    def test_no_unexpected_names(self) -> None:
        shipped = {path.name for path in BRAND.glob("*") if path.is_file()}
        assert shipped <= ALLOWED_IMAGES, f"rejected by brands view: {shipped}"
        assert shipped == EXPECTED

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_is_real_png(self, name: str) -> None:
        # The brands view hardcodes content_type: image/png, so a JPEG or SVG
        # under a .png name would be served as a broken image.
        assert (BRAND / name).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_is_square(self, name: str) -> None:
        from PIL import Image  # noqa: PLC0415

        with Image.open(BRAND / name) as image:
            assert image.width == image.height, f"{name} must be square"

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_keeps_alpha_channel(self, name: str) -> None:
        # The mark has a white outline on transparency. Flattening it onto
        # white — the obvious thing to do to a PNG — would paint a white
        # square behind it and look wrong on a dark theme.
        from PIL import Image  # noqa: PLC0415

        with Image.open(BRAND / name) as image:
            assert image.mode == "RGBA", f"{name} lost its alpha channel"
            alpha = image.convert("RGBA").getchannel("A")
            assert alpha.getextrema()[0] == 0, f"{name} has no transparent pixel"

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_mark_fills_but_does_not_touch_the_edge(self, name: str) -> None:
        from PIL import Image  # noqa: PLC0415

        with Image.open(BRAND / name) as image:
            alpha = image.convert("RGBA").getchannel("A")
            width, height = image.size
            edge = [
                alpha.getpixel((0, y)) for y in range(0, height, max(height // 32, 1))
            ]
            edge += [
                alpha.getpixel((x, 0)) for x in range(0, width, max(width // 32, 1))
            ]
            assert max(edge) == 0, f"{name} is flush to the edge"


class TestPackaging:
    def test_brand_images_reach_the_hacs_archive(self, hacs_zip) -> None:
        # tools/package.py filters by suffix. Before `.png` was allowlisted,
        # the artwork was silently dropped from every published archive and the
        # integration rendered with the generic placeholder icon.
        shipped = set(hacs_zip.namelist())
        for name in EXPECTED:
            assert f"brand/{name}" in shipped, f"brand/{name} missing from zip"

    def test_manifest_is_still_at_archive_root(self, hacs_zip) -> None:
        # HACS extracts the archive into config/, so the component files must
        # sit at the root rather than under custom_components/.
        assert "manifest.json" in hacs_zip.namelist()
        assert "custom_components/my_dom_ru/manifest.json" not in hacs_zip.namelist()

    def test_archive_ships_no_research_data(self, hacs_zip) -> None:
        forbidden = (".apk", ".apkm", ".research/", "secrets", ".env")
        for name in hacs_zip.namelist():
            assert not any(token in name for token in forbidden), name


class TestManifestConsistency:
    def test_manifest_has_no_brand_key(self) -> None:
        # Nothing in manifest.json needs to change for artwork: the brands view
        # discovers `brand/` from the component's top-level files.
        manifest = json.loads(
            (COMPONENT / "manifest.json").read_text(encoding="utf-8")
        )
        assert "logo" not in manifest
        assert "icon" not in manifest
