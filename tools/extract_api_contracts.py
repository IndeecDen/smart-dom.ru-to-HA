"""Extract an endpoint inventory from a local jadx output, never copy app code.

Usage: python tools/extract_api_contracts.py PATH_TO_JADX_SOURCES
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

METHODS = {"b": "DELETE", "f": "GET", "g": "HEAD", "n": "PATCH", "o": "POST", "p": "PUT"}


def extract(root: Path) -> list[dict]:
    """Read Retrofit method annotations and their following declarations."""
    records = []
    for path in sorted(root.rglob("*.java")):
        source = path.read_text(encoding="utf-8")
        if "import pt0." not in source:
            continue
        lines = source.splitlines()
        for index, line in enumerate(lines):
            match = re.search(r'@(b|f|g|n|o|p)\("((?:/?rest/|/?auth/|/?api/)[^"]+)"\)', line)
            if match:
                method, endpoint = METHODS[match[1]], match[2]
            else:
                match = re.search(r'@h\(.*method = "(\w+)", path = "([^"]+)"', line)
                if not match:
                    continue
                method, endpoint = match[1], match[2]
            declaration = lines[index + 1] if index + 1 < len(lines) else ""
            record = {
                "method": method, "path": "/" + endpoint.lstrip("/"),
                "path_parameters": re.findall(r'@s\("([^"]+)"\)', declaration),
                "query_parameters": re.findall(r'@t\("([^"]+)"\)', declaration),
                "source": path.relative_to(root).as_posix(), "line": index + 1,
            }
            body_match = re.search(r'@pt0\.a ([\w.]+)', declaration)
            if body_match:
                body_type = body_match[1]
                record["body_type"] = body_type
                imports = re.findall(r'^import ([\w.]+);', source, re.MULTILINE)
                qualified = next((item for item in imports if item.endswith("." + body_type)), None)
                if qualified:
                    adapter = root / (qualified.replace(".", "/") + "JsonAdapter.java")
                    if adapter.exists():
                        fields = re.search(r'c\.b\(([^;]+)\)', adapter.read_text(encoding="utf-8"))
                        if fields:
                            record["body_fields"] = re.findall(r'"([^"\\]+)"', fields[1])
            records.append(record)
    return records


if __name__ == "__main__":
    output = Path(__file__).resolve().parents[1] / "docs/apk-api-9.10.0.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    records = extract(Path(sys.argv[1]))
    output.write_text(json.dumps({"application": "com.ertelecom.smarthome", "version": "9.10.0", "version_code": 91000020, "endpoints": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(records)} Retrofit declarations in {output}")
