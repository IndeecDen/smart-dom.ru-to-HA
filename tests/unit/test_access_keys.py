"""Unit tests for access-key label resolution."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "custom_components"))

from my_dom_ru.access_keys import (  # noqa: E402
    normalize_code,
    parse_key_names,
    resolve_key_name,
)


class TestNormalizeCode:
    def test_strips_separators_and_case(self) -> None:
        assert normalize_code("098-B987") == "098b987"
        assert normalize_code(" 098 b 987 ") == "098b987"
        assert normalize_code("098B987") == "098b987"

    def test_rejects_non_string(self) -> None:
        assert normalize_code(None) == ""
        assert normalize_code(123) == ""


class TestParseKeyNames:
    def test_parses_equals_and_colon(self) -> None:
        parsed = parse_key_names("098b987y = Сын\n098c112z: Жена")
        assert parsed == {"098b987y": "Сын", "098c112z": "Жена"}

    def test_ignores_comments_and_blank_lines(self) -> None:
        parsed = parse_key_names("# ключи\n\n098b987y = Сын\n   \n")
        assert parsed == {"098b987y": "Сын"}

    def test_ignores_lines_without_label(self) -> None:
        assert parse_key_names("098b987y") == {}
        assert parse_key_names("098b987y =   ") == {}

    def test_first_assignment_wins(self) -> None:
        parsed = parse_key_names("098b987y = Сын\n098b987y = Дубль")
        assert parsed == {"098b987y": "Сын"}

    def test_normalizes_code_on_parse(self) -> None:
        assert parse_key_names("098-B987 = Сын") == {"098b987": "Сын"}

    def test_non_string_is_empty(self) -> None:
        assert parse_key_names(None) == {}
        assert parse_key_names(42) == {}

    def test_bare_space_separator(self) -> None:
        assert parse_key_names("098b987y Сын") == {"098b987y": "Сын"}


class TestResolveKeyName:
    KEYS = parse_key_names("098b987y = Сын\n098c112z = Жена")

    def test_finds_code_anywhere_in_text(self) -> None:
        assert resolve_key_name("Адрес открыта ключом 098b987y", self.KEYS) == "Сын"
        assert resolve_key_name("098c112z открыл домофон", self.KEYS) == "Жена"

    def test_survives_reworded_template(self) -> None:
        # The operator may reword the sentence; containment still resolves it.
        for template in (
            "Дверь открыта ключом 098b987y",
            "Доступ предоставлен: 098b987y",
            "Код 098b987y применён",
        ):
            assert resolve_key_name(template, self.KEYS) == "Сын"

    def test_ignores_separators_in_text(self) -> None:
        assert resolve_key_name("открыто ключом 098-B987y", self.KEYS) == "Сын"

    def test_truncated_code_does_not_match(self) -> None:
        # A prefix of the real code must not resolve: matching it would
        # attribute an activation to the wrong person.
        assert resolve_key_name("открыто ключом 098-B987", self.KEYS) is None

    def test_ignores_case(self) -> None:
        assert resolve_key_name("открыто ключом 098B987Y", self.KEYS) == "Сын"

    def test_no_match_returns_none(self) -> None:
        assert resolve_key_name("Дверь открыта приложением", self.KEYS) is None

    def test_empty_inputs(self) -> None:
        assert resolve_key_name("", self.KEYS) is None
        assert resolve_key_name(None, self.KEYS) is None
        assert resolve_key_name("098b987y", {}) is None

    def test_longest_code_wins_over_prefix(self) -> None:
        keys = parse_key_names("098 = Короткий\n098b987y = Сын")
        # Both are >= _MIN_CODE_LENGTH only for the long one; assert ordering
        # explicitly with two long codes sharing a prefix instead.
        keys = parse_key_names("abcdef = Короткий\nabcdefghij = Сын")
        assert resolve_key_name("код abcdefghij", keys) == "Сын"

    def test_too_short_code_is_rejected(self) -> None:
        # A 3-character code would match almost any sentence.
        keys = parse_key_names("abc = Опасно")
        assert resolve_key_name("любой текст abc", keys) is None

    @pytest.mark.parametrize("raw", ["", "   ", "нет знака равенства тут"])
    def test_garbage_input_is_harmless(self, raw: str) -> None:
        assert isinstance(parse_key_names(raw), dict)
