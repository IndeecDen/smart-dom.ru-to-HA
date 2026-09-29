"""The push/device registration body must identify this operator's app.

Regression: `appId` was hardcoded to 2, which in 9.10.0 is the *Новотелеком*
build (`NTK(2, "com.novotelecom.domophone")`). This integration is the
ЭР-Телеком build, `ERTH(4, "erth")`. Registration still returned 200, so the
mismatch was invisible: the operator accepted the device but addressed no
pushes to it.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "custom_components"))

from my_dom_ru.api import MyDomRuAPI  # noqa: E402
from my_dom_ru.const import APP_ID, FCM_BUNDLE_ID  # noqa: E402
from my_dom_ru.user_agent import UserAgent  # noqa: E402

# Values from the 9.10.0 enum `hg.f`, which the app uses to build the body.
APK_APP_IDS = {
    "ЭР-Телеком (наш оператор)": 4,
    "Новотелеком": 2,
    "мониторинг ЭР-Телеком": 6,
    "часы ЭР-Телеком": 8,
}


def make_api() -> MyDomRuAPI:
    user_agent = UserAgent()
    user_agent.from_json(
        {
            "phone_manufacturer": "Google",
            "phone_model": "Pixel 9",
            "android_ver": "16",
            "uuid": "11111111-2222-3333-4444-555555555555",
            "app_version": {"name": "9.10.0", "code": "91000020"},
            "account_id": "1",
            "operator_id": "18",
            "place_id": "55",
        }
    )
    api = MyDomRuAPI(MagicMock(), user_agent, operator="18")
    # _push_body only reads the user agent off the HTTP wrapper.
    api.http = MagicMock()
    api.http.user_agent = user_agent
    return api


class TestAppIdentity:
    def test_app_id_is_the_ertelecom_build(self) -> None:
        assert APP_ID == APK_APP_IDS["ЭР-Телеком (наш оператор)"]

    def test_app_id_is_not_the_inherited_novotelecom_value(self) -> None:
        # The specific wrong value that was there, so the intent is explicit.
        assert APP_ID != APK_APP_IDS["Новотелеком"]

    def test_push_body_carries_app_id(self) -> None:
        api = make_api()
        body = api._push_body("token-abc")
        assert body["appId"] == APP_ID

    def test_bundle_and_app_id_agree(self) -> None:
        # A body claiming one operator while carrying the other's FCM project
        # is the exact combination that produced no pushes.
        assert FCM_BUNDLE_ID == "com.ertelecom.smarthome"
        assert APP_ID == 4

    @pytest.mark.parametrize("label, expected", list(APK_APP_IDS.items()))
    def test_enumeration_reference(self, label: str, expected: int) -> None:
        # Documents the source values so a future APK refresh can be checked
        # against them rather than re-guessed.
        assert expected in (2, 4, 6, 8), label


class TestPushBodyShape:
    def test_subscriber_registration_has_device_type(self) -> None:
        assert make_api()._push_body("t")["deviceType"] == "MOBILE_APPLICATION"

    def test_device_installations_omits_device_type(self) -> None:
        # HAR 9.9.0: deviceType is present for subscriberNotifications and
        # absent for public device-installations.
        body = make_api()._push_body("t", include_device_type=False)
        assert "deviceType" not in body

    def test_mac_address_is_not_sent(self) -> None:
        # The app sends macAddress only when deviceType is TERMINAL; for a
        # phone registration the constructor passes null. Omitting it matches
        # the app, and the field is 12th in the APK model.
        assert "macAddress" not in make_api()._push_body("t")

    def test_unregister_body_has_no_token(self) -> None:
        assert "pushToken" not in make_api()._push_body()
