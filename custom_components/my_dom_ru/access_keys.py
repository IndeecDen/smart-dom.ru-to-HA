"""Human labels for operator access keys.

The backend does not report *which* key opened a door. `EventRaw` carries only
`eventTypeName` (the string `accessKeyActivated`), `timestamp`, and a server
rendered `message`. The app itself never parses that text either — it only
picks an icon from the event type.

So the key identity has to be resolved from the message locally. Rather than
parsing positionally ("address opened by key X"), we test whether a configured
key code occurs anywhere in the text. That survives rewording: "Дверь открыта
ключом X", "Доступ предоставлен: X" and "Код X" all match the same code, and a
sentence the operator rephrases does not silently stop resolving.

The raw message is consumed here and never propagated. The rest of the
integration only ever sees the resolved `key_name`, which keeps the localized
text (and the key code inside it) out of entity attributes, the recorder and
diagnostics — consistent with `HistoryEvent` deliberately not carrying it.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

#: Separators the operator may insert inside a printed key code. Codes are
#: alphanumeric, so dropping every non-alphanumeric character on both sides
#: makes "098-B987" in the message match the configured "098B987".
#:
#: Both cases must be accepted before folding to lowercase — a `[0-9a-z]`
#: class would *delete* `B` rather than lower it, so "098B987Y" and
#: "098b987y" would normalize to different strings and never match.
_NON_ALNUM = re.compile(r"[^0-9a-zA-Z]+")

#: Below this length a "code" matches almost any text, so it is rejected
#: outright. Real access key codes are comfortably longer.
_MIN_CODE_LENGTH = 4


def normalize_code(value: Any) -> str:
    """Reduce a key code to comparable lowercase alphanumerics."""
    if not isinstance(value, str):
        return ""
    return _NON_ALNUM.sub("", value).lower()


def parse_key_names(raw: Any) -> dict[str, str]:
    """Parse the options text into a normalized code → label mapping.

    Accepted line forms, one per line::

        098b987y = Сын
        098c112z: Жена
        12 45 67 Жена

    Blank lines and `#` comments are ignored. The first assignment of a code
    wins, so a duplicated line cannot silently shadow an earlier label.

    Args:
        raw: The options string as typed by the user.

    Returns:
        Mapping of normalized code → label, with empty labels dropped.
    """
    if not isinstance(raw, str):
        return {}
    mapping: dict[str, str] = {}
    for line in raw.splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        code, separator, label = _split_assignment(text)
        if not separator:
            continue
        normalized = normalize_code(code)
        label = label.strip()
        if not normalized or not label:
            continue
        mapping.setdefault(normalized, label)
    return mapping


def _split_assignment(text: str) -> tuple[str, str, str]:
    """Split one mapping line into code, separator and label.

    `=` and `:` are explicit separators. A bare space separator is only
    accepted when the first token survives normalization, so a label written
    without a separator ("098b987y Сын") still works while a code that is
    itself space separated ("12 45 67") is not cut in half.
    """
    for separator in ("=", ":"):
        if separator in text:
            code, _, label = text.partition(separator)
            return code, separator, label
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and normalize_code(parts[0]):
        return parts[0], " ", parts[1]
    return text, "", ""


def resolve_key_name(message: Any, key_names: Mapping[str, str]) -> str | None:
    """Return the label of a configured key mentioned in `message`.

    Codes are matched longest-first so that a code which is a prefix of
    another cannot shadow the longer, more specific one.

    Args:
        message: The server rendered event text, or `None`.
        key_names: Output of :func:`parse_key_names`.

    Returns:
        The configured label, or `None` when no key matches.
    """
    haystack = normalize_code(message)
    if not haystack:
        return None
    for code in sorted(key_names, key=len, reverse=True):
        if len(code) < _MIN_CODE_LENGTH:
            continue
        if code in haystack:
            return key_names[code]
    return None


# Runs of four or more ASCII alphanumerics. A key code is exactly this shape;
# so are phone numbers and identifiers, which must not reach a log either.
_SECRET_RUN = re.compile(r"[0-9A-Za-z]{4,}")


def mask_secrets(text: Any) -> str:
    """Return `text` with every identifier-like run replaced by `***`.

    Used for diagnostics: it keeps the sentence readable — "адрес открыта
    ключом ***" — while making it safe to put in a log that a user may paste
    into an issue. Cyrillic words are untouched, since the class is ASCII only.

    Args:
        text: The operator message, or `None`.

    Returns:
        The masked text, or an empty string for a falsy input.
    """
    if not isinstance(text, str) or not text:
        return ""
    return _SECRET_RUN.sub("***", text)
