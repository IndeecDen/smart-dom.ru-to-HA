"""Key names come from the operator only — there is nothing to configure.

The option existed while the integration looked for key *codes* in the
notification text. A live account showed the message names the key instead
("... открыта ключом Денис"), so the codes were never in the text to match and
the setting could only duplicate a name the phone app already shows.

These tests pin that decision, so the option does not quietly come back and
become a second place where a name is edited.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPONENT = ROOT / "custom_components/my_dom_ru"
sys.path.insert(0, str(ROOT / "custom_components"))

from my_dom_ru.config_flow import MyDomRuOptionsFlowHandler  # noqa: E402
from my_dom_ru.const import CONF_GO2RTC_USERNAME  # noqa: E402
from my_dom_ru.user_agent import UserAgent  # noqa: E402

CATALOGUES = ("strings.json", "translations/ru.json", "translations/en.json")


class TestNoLabelOption:
    def test_const_is_gone(self) -> None:
        from my_dom_ru import const  # noqa: PLC0415

        assert not hasattr(const, "CONF_KEY_NAMES")

    def test_parsing_helpers_are_gone(self) -> None:
        from my_dom_ru import access_keys  # noqa: PLC0415

        assert not hasattr(access_keys, "parse_key_names")
        assert not hasattr(access_keys, "apply_overrides")

    @pytest.mark.parametrize("filename", CATALOGUES)
    def test_no_translated_field(self, filename: str) -> None:
        data = json.loads(
            (COMPONENT / filename).read_text(encoding="utf-8")
        )
        fields = data["options"]["step"]["init"]["data"]
        assert "key_names" not in fields

    def test_options_form_has_no_field(self) -> None:
        # The form is built inline inside async_step_init, and calling it needs
        # a fully wired OptionsFlow, which is not worth the fixture. Reading the
        # method source is the cheap guard that the setting does not come back;
        # the "does not break anything" half is covered by the resolution test
        # below and by the rest of the suite.
        import inspect  # noqa: PLC0415

        source = inspect.getsource(MyDomRuOptionsFlowHandler.async_step_init)
        assert "KEY_NAMES" not in source
        assert "key_names" not in source
        # A blank form would mean the removal ate something else by mistake.
        assert CONF_GO2RTC_USERNAME in source
        assert source.count("vol.Optional") >= 4


class TestNamesStillResolveWithoutTheOption:
    """Removing the setting must not stop resolution."""

    def test_operator_names_are_enough(self) -> None:
        from my_dom_ru.access_keys import build_key_index, resolve_key_identity

        index = build_key_index(
            [{"id": 1, "accessKey": {"accessKeyCode": "5034 0C4B", "name": "Денис"}}]
        )
        assert resolve_key_identity("открыта ключом Денис.", index) == "Денис"


class TestUserAgentUnaffected:
    def test_still_builds(self) -> None:
        # The option removal touched config_flow imports; confirm the user
        # agent the push body depends on is intact.
        agent = UserAgent()
        assert agent.app_version["code"] == "91000020"
        assert agent.phone_manufacturer
