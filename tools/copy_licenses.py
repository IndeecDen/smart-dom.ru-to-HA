"""Copy license texts for frontend code included in the prebuilt bundle."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
packages = ("lit", "lit-html", "lit-element", "@lit/reactive-element", "lucide-static")
parts = []
for package in packages:
    package_dir = ROOT / "frontend/node_modules" / package
    candidates = (package_dir / "LICENSE", package_dir / "LICENSE.txt")
    license_file = next((candidate for candidate in candidates if candidate.is_file()), None)
    if license_file is None:
        raise FileNotFoundError(f"Missing license: {package}")
    parts.append(f"===== {package} =====\n" + license_file.read_text(encoding="utf-8"))
text = "\n\n".join(parts)
for destination in (ROOT / "THIRD_PARTY_LICENSES.txt", ROOT / "custom_components/my_dom_ru/THIRD_PARTY_LICENSES.txt"):
    destination.write_text(text, encoding="utf-8")
print("Copied frontend license notices")
