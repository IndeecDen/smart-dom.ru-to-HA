"""Human labels for operator access keys.

The backend never reports *which* key opened a door in any structured field.
`EventRaw` carries `eventTypeName`, `timestamp`, a `source` that identifies
the *lock*, and a server rendered `message`. Verified on a real account, a
door opening arrives as `POST /rest/v1/events/search` never returning
`accessKeyActivated` at all, and instead as a plain `infoNotification` event
whose text reads, for example::

    30 Лет Октября 6 (п. 3) открыта ключом Денис.

So the identity lives in the text, and the operator's own key names come from
`list_access_keys` — there is nothing to configure. Codes are indexed too,
because a key with no useful name is still recognised by its code, and the
app prints codes with a space in the middle ("5034 0C4B").

Matching is containment at word boundaries rather than a fixed template: the
operator may reword the sentence, and a key named "Дом" must not match
"Домофон".

The raw message never leaves the integration. Only the resolved name is put on
an entity attribute, so the key code stays out of the recorder and
diagnostics — consistent with `HistoryEvent` deliberately not carrying the
message either.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

#: Separators the operator inserts inside printed codes. Non-word runs collapse
#: to a wildcard when matching, so "5034 0C4B" matches "50340C4B".
_NON_WORD = re.compile(r"\W+", re.UNICODE)

#: Separators stripped when folding a code to a comparable key. Unicode aware,
#: so a Cyrillic name survives; an ASCII-only class would delete it.
_FOR_FOLD = re.compile(r"[^0-9a-zA-ZЀ-ӿ]+")

#: Separators the operator may insert inside a printed key code, replaced in
#: debug previews so a code cannot reach a log.
_SECRET_RUN = re.compile(r"[0-9A-Za-z]{4,}")

#: Below this length a label matches almost any sentence. Codes are longer in
#: practice; names shorter than this are not distinctive enough to trust.
_MIN_LABEL_LENGTH = 3


def normalize_code(value: Any) -> str:
    """Reduce a value to comparable lowercase letters and digits.

    Unicode aware, so Cyrillic names are preserved rather than deleted.
    """
    if not isinstance(value, str):
        return ""
    return _FOR_FOLD.sub("", value.lower())


def _label_pattern(label: str) -> re.Pattern[str] | None:
    """Compile a label into a word-boundary matcher.

    Runs of non-word characters inside the label become ``\\W*``, so a code
    printed as "5034 0C4B" matches any spacing. Word boundaries keep a short
    name from matching a longer word: "Дом" must not match "Домофон".

    Args:
        label: The raw code or name.

    Returns:
        The compiled pattern, or None when the label has no word characters.
    """
    parts = [part for part in _NON_WORD.split(label) if part]
    if not parts:
        return None
    return re.compile(
        r"\b" + r"\W*".join(re.escape(part) for part in parts) + r"\b",
        re.UNICODE | re.IGNORECASE,
    )


def parse_key_names(raw: Any) -> dict[str, str]:
    """Parse the options text into a label mapping.

    Accepted line forms, one per line::

        5034 0C4B = Денис
        454E6FB3: Арсений
        21E4C23F Ключ №1

    Blank lines and `#` comments are ignored. The first assignment of a code
    wins, so a duplicated line cannot silently shadow an earlier label.

    This is an override for keys the operator names badly or not at all; the
    names from `list_access_keys` are used when it is empty.

    Args:
        raw: The options string as typed by the user.

    Returns:
        Mapping of raw code → label, with empty labels dropped.
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
        label = label.strip()
        if code and label:
            mapping.setdefault(code, label)
    return mapping


def _split_assignment(text: str) -> tuple[str, str, str]:
    """Split one mapping line into code, separator and label.

    `=` and `:` are explicit separators. A bare space separator is only
    accepted when the first token holds word characters, so a code that is
    itself space separated ("5034 0C4B = Денис" uses `=`, but a code printed
    "12 45 67 Жена" without one) is not cut in half.
    """
    for separator in ("=", ":"):
        if separator in text:
            code, _, label = text.partition(separator)
            # Only the outer whitespace goes: a code may legitimately contain
            # a space, as the app prints it ("5034 0C4B = Денис").
            return code.strip(), separator, label
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and any(part.isalnum() for part in _NON_WORD.split(parts[0])):
        return parts[0], " ", parts[1]
    return text, "", ""


def build_key_index(keys: Any) -> dict[str, str]:
    """Index the operator's access keys by every form they appear under.

    The verified shape of `list_access_keys` is a list of
    ``{id, placeId, accessKey: {accessKeyCode, name, …}}`` — the code is
    nested, the id is not.

    Both the code and the name are indexed, because the operator writes
    *either* into the notification. Both resolve to the same display name, so
    a key is recognised no matter which form the message used.

    Args:
        keys: The raw `list_access_keys` payload, or `None`.

    Returns:
        Mapping of raw code or name → display name.
    """
    index: dict[str, str] = {}
    if not isinstance(keys, list):
        return index
    for item in keys:
        if not isinstance(item, dict):
            continue
        nested = item.get("accessKey")
        nested = nested if isinstance(nested, dict) else item
        code = nested.get("accessKeyCode")
        code = code.strip() if isinstance(code, str) else ""
        raw_name = nested.get("name")
        name = raw_name.strip() if isinstance(raw_name, str) else ""
        # A key with no name is still identified by its code.
        display = name or (code.upper() if code else "")
        if not display:
            continue
        for token in (code, name):
            token = token.strip() if isinstance(token, str) else ""
            if token and _label_pattern(token):
                index.setdefault(token, display)
    return index


def describe_key_payload(keys: Any) -> str:
    """Describe the shape of a `list_access_keys` response, never its values.

    The nesting assumption — `accessKey.accessKeyCode` nested while `id` sits
    at the top level — came from the APK. If the operator ever returns a
    different shape, the index silently comes out empty and every key event
    goes anonymous. This makes that visible without putting a code or a name
    into a log.

    Args:
        keys: The raw response, whatever shape it turned out to be.

    Returns:
        A short structural description.
    """
    if not isinstance(keys, list):
        return f"not-a-list({type(keys).__name__})"
    if not keys:
        return "empty-list"
    first = keys[0]
    if not isinstance(first, dict):
        return f"item-not-dict({type(first).__name__})"
    nested = first.get("accessKey")
    inner = (
        sorted(nested)
        if isinstance(nested, dict)
        else f"not-dict({type(nested).__name__})"
    )
    return f"{len(keys)} items, top={sorted(first)}, accessKey={inner}"


def apply_overrides(
    index: Mapping[str, str],
    overrides: Mapping[str, str],
) -> dict[str, str]:
    """Return `index` with the user's labels applied to whole keys.

    A key is indexed under both its code and its name, and the message may
    contain either. Renaming therefore has to hit every form of the same key:
    overriding `5034 0C4B` also renames the `Денис` form, or the user would
    still get the operator's name for every notification that happens to
    spell it out.

    Args:
        index: Output of :func:`build_key_index`.
        overrides: Output of :func:`parse_key_names`.

    Returns:
        A new mapping; the inputs are not modified.
    """
    result = dict(index)
    for token, label in overrides.items():
        if not token or not label:
            continue
        # Whatever this token currently points at identifies the key; every
        # other form bound to the same value is renamed alongside it.
        affected = result.get(token)
        result[token] = label
        if affected and affected != label:
            for other, value in list(result.items()):
                if other != token and value == affected:
                    result[other] = label
    return result


def resolve_key_identity(
    message: Any,
    index: Mapping[str, str],
) -> str | None:
    """Return the name of a key whose code or name occurs in `message`.

    Longer labels are tried first, so a code that is a prefix of another
    cannot shadow the longer, more specific one.

    Args:
        message: The server rendered event text, or `None`.
        index: Output of :func:`build_key_index` or :func:`parse_key_names`.

    Returns:
        The key's display name, or `None` when nothing matches.
    """
    if not isinstance(message, str) or not message.strip() or not index:
        return None
    # Longest first: a specific code beats a short name.
    for label in sorted(index, key=len, reverse=True):
        if len(normalize_code(label)) < _MIN_LABEL_LENGTH:
            continue
        pattern = _label_pattern(label)
        if pattern is not None and pattern.search(message):
            return index[label]
    return None


def mask_secrets(text: Any) -> str:
    """Return `text` with every identifier-like run replaced by `***`.

    Used for diagnostics: it keeps the sentence readable — "открыта ключом
    Денис" — while making it safe to put in a log a user may paste into an
    issue. Cyrillic words are untouched, since the class is ASCII only.

    Args:
        text: The operator message, or `None`.

    Returns:
        The masked text, or an empty string for a falsy input.
    """
    if not isinstance(text, str) or not text:
        return ""
    return _SECRET_RUN.sub("***", text)
