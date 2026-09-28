"""Build distributable archives from an explicit allowlist, excluding local data."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components/my_dom_ru"

# `.png` is required by `brand/`: Home Assistant serves integration artwork
# from `custom_components/<domain>/brand/` via /api/brands/integration, and
# hardcodes `content_type: image/png` (homeassistant/components/brands). With
# the suffix filter below omitting `.png`, the artwork was silently dropped
# from every archive and the UI fell back to the generic placeholder.
ALLOWED_SUFFIXES = frozenset(
    {".py", ".json", ".yaml", ".js", ".txt", ".png"}
)


def build() -> list[Path]:
    version = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))["version"]
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    files = sorted(
        path
        for path in COMPONENT.rglob("*")
        if path.is_file() and path.suffix in ALLOWED_SUFFIXES
    )
    result = []
    for filename, manual in [("my_dom_ru.zip", False), (f"my_dom_ru-{version}-manual.zip", True)]:
        dest = output / filename
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                relative = path.relative_to(ROOT if manual else COMPONENT)
                archive.write(path, relative.as_posix())
            root_files = ("LICENSE", "NOTICE.md", "THIRD_PARTY_LICENSES.txt") if manual else ("LICENSE", "NOTICE.md")
            for name in root_files:
                archive.write(ROOT / name, name)
            if manual:
                for name in ("README.md", "CHANGELOG.md", "docs/FEATURES.md", "docs/INSTALL.md", "docs/TESTING.md"):
                    archive.write(ROOT / name, name)
        result.append(dest)
    (output / "SHA256SUMS.txt").write_text("".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in result), encoding="utf-8")
    return result


if __name__ == "__main__":
    for archive in build():
        print(f"{archive.name}: {archive.stat().st_size} bytes")
