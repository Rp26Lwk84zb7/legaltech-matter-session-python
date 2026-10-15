from unittest.mock import Mock

from legaltech_service import LegalTechService, MatterIntake, SignupRequest, signup_or_reject
from infrai_client import InfraiError


def test_rejected_captcha_stays_a_client_error() -> None:
    client = Mock()
    client.post.side_effect = InfraiError("CAPTCHA_SCORE_TOO_LOW", {}, 422)
    status, body = signup_or_reject(LegalTechService(client), SignupRequest("a@b.test", "secret", "A", "token", "widget-1"))
    assert status == 422
    assert body == {"error": "CAPTCHA_SCORE_TOO_LOW"}
    client.post.assert_called_once_with(
        "/v1/captcha/verify", {"widget_record_id": "widget-1", "token": "token", "action": "signup"}
    )


def test_matter_handoff_keeps_deadline_follow_up() -> None:
    client = Mock()
    client.post.return_value = {"ok": True, "data": {"session_id": "s-1"}}
    result = LegalTechService(client).prepare_matter(
        MatterIntake("client@example.test", "Lease review", "2026-10-01", "signed-lease.pdf"), "user-7"
    )
    assert result["follow_up"] == "Email client@example.test before 2026-10-01"
    assert result["session_id"] == "s-1"
