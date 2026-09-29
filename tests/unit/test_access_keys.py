"""Unit tests for access-key identity resolution.

The verified facts these encode, from a real account:

* a door opening arrives as `infoNotification`, not `accessKeyActivated`;
* its text reads e.g. "30 Лет Октября 6 (п. 3) открыта ключом Денис.";
* `list_access_keys` nests the code under `accessKey` while `id` is at top
  level, and the app prints codes with a space ("5034 0C4B");
* so the name is already in the message and needs no configuration.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "custom_components"))

from my_dom_ru.access_keys import (  # noqa: E402
    build_key_index,
    mask_secrets,
    normalize_code,
    resolve_key_identity,
)

# Exactly the shape shown in the app for this account.
KEYS = [
    {"id": 1, "placeId": 20443849,
     "accessKey": {"accessKeyCode": "21E4 C23F", "name": "Ключ №1"}},
    {"id": 2, "placeId": 20443849,
     "accessKey": {"accessKeyCode": "454E 6FB3", "name": "Арсений"}},
    {"id": 3, "placeId": 20443849,
     "accessKey": {"accessKeyCode": "5034 0C4B", "name": "Денис"}},
]

MESSAGE = "30 Лет Октября 6  (п. 3) открыта ключом Денис."


class TestNormalizeCode:
    def test_is_unicode_aware(self) -> None:
        # The previous ASCII-only class deleted Cyrillic names entirely,
        # which would have made name matching impossible.
        assert normalize_code("Денис") == "денис"
        assert normalize_code("Арсений") == "арсений"

    def test_folds_case_and_spaces(self) -> None:
        assert normalize_code("5034 0C4B") == "50340c4b"
        assert normalize_code("50340C4B") == "50340c4b"
        assert normalize_code(" 21E4-C23F ") == "21e4c23f"

    def test_rejects_non_string(self) -> None:
        assert normalize_code(None) == ""
        assert normalize_code(123) == ""


class TestBuildKeyIndex:
    def test_indexes_both_code_and_name(self) -> None:
        index = build_key_index(KEYS)
        assert index["Денис"] == "Денис"
        assert index["5034 0C4B"] == "Денис"
        assert index["Арсений"] == "Арсений"
        assert index["454E 6FB3"] == "Арсений"

    def test_every_key_lands_under_its_own_name(self) -> None:
        index = build_key_index(KEYS)
        assert index["21E4 C23F"] == "Ключ №1"
        assert index["Ключ №1"] == "Ключ №1"

    def test_unnamed_key_falls_back_to_code(self) -> None:
        index = build_key_index(
            [{"id": 9, "accessKey": {"accessKeyCode": "ABCD1234", "name": ""}}]
        )
        assert index["ABCD1234"] == "ABCD1234"

    def test_tolerates_flat_shape(self) -> None:
        # Some payloads put the fields at the top level instead.
        index = build_key_index([{"accessKeyCode": "ABCD1234", "name": "Гость"}])
        assert index["Гость"] == "Гость"

    def test_garbage_input_is_harmless(self) -> None:
        for bad in (None, "nope", 42, [None, 3, "x"], [{"accessKey": None}]):
            assert build_key_index(bad) == {}


class TestResolveKeyIdentity:
    INDEX = build_key_index(KEYS)

    def test_resolves_the_verified_message(self) -> None:
        assert resolve_key_identity(MESSAGE, self.INDEX) == "Денис"

    def test_resolves_by_code_with_its_spacing(self) -> None:
        assert resolve_key_identity("открыта ключом 5034 0C4B", self.INDEX) == "Денис"

    def test_resolves_by_code_without_spacing(self) -> None:
        assert resolve_key_identity("открыта ключом 50340C4B", self.INDEX) == "Денис"

    def test_distinguishes_keys(self) -> None:
        assert resolve_key_identity("ключом Арсений", self.INDEX) == "Арсений"
        assert resolve_key_identity("ключом Ключ №1", self.INDEX) == "Ключ №1"

    @pytest.mark.parametrize(
        "text",
        [
            "Дверь открыта ключом Денис",
            "Доступ предоставлен: Денис",
            "Кто-то открыл домофон, Денис",
            "ДЕНИС открыл",
        ],
    )
    def test_survives_rewording(self, text: str) -> None:
        # Containment, not a fixed template: the operator may reword.
        assert resolve_key_identity(text, self.INDEX) == "Денис"

    def test_short_name_does_not_match_a_longer_word(self) -> None:
        # The bug a plain substring search would have: "Дом" must not be found
        # inside "Домофон".
        index = build_key_index([{"accessKey": {"accessKeyCode": "ZZZZ1111", "name": "Дом"}}])
        assert resolve_key_identity("Домофон открыт", index) is None
        assert resolve_key_identity("открыто ключом Дом", index) == "Дом"

    def test_no_match_returns_none(self) -> None:
        assert resolve_key_identity("Дверь открыта приложением", self.INDEX) is None

    def test_empty_inputs(self) -> None:
        assert resolve_key_identity("", self.INDEX) is None
        assert resolve_key_identity(None, self.INDEX) is None
        assert resolve_key_identity(MESSAGE, {}) is None

    def test_very_short_label_is_ignored(self) -> None:
        # "Я" would match almost any sentence.
        assert resolve_key_identity("открыто ключом Я", {"Я": "Я"}) is None


class TestMaskSecrets:
    """Diagnostic previews stay readable but must not leak a key code."""

    def test_code_is_masked_but_sentence_survives(self) -> None:
        masked = mask_secrets("открыта ключом 50340C4B")
        assert masked == "открыта ключом ***"
        assert "открыта ключом" in masked

    def test_cyrillic_words_are_untouched(self) -> None:
        text = "Доступ предоставлен жильцу"
        assert mask_secrets(text) == text

    def test_contiguous_long_digits_are_masked(self) -> None:
        assert mask_secrets("ид 9161234567") == "ид ***"

    def test_spaced_groups_are_not_masked(self) -> None:
        # Documented limitation rather than papered over: the class is a
        # contiguous run, so digits split by spaces survive. Widening it to
        # spaced groups would mangle ordinary prose.
        assert mask_secrets("звоните +7 916 123 45 67") == "звоните +7 916 123 45 67"

    def test_non_string_is_empty(self) -> None:
        assert mask_secrets(None) == ""
        assert mask_secrets(123) == ""
