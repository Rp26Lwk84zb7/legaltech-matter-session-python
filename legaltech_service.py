from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from infrai_client import InfraiClient, InfraiError, captcha_verify


@dataclass(frozen=True)
class SignupRequest:
    email: str
    password: str
    name: str
    captcha_token: str
    captcha_widget_record_id: str


@dataclass(frozen=True)
class MatterIntake:
    client_email: str
    matter_title: str
    deadline: str
    document_name: str


class LegalTechService:
    def __init__(self, client: InfraiClient):
        self.client = client

    def signup(self, request: SignupRequest) -> dict[str, Any]:
        captcha_verify(self.client, request.captcha_widget_record_id, request.captcha_token)
        user = self.client.post(
            "/v1/auth/user/create",
            {"email": request.email, "password": request.password, "name": request.name,
             "metadata": {"domain": "matter-intake"}, "vendor": "infrai", "mode": "X",
             "idempotency_key": f"signup:{request.email}"},
        )
        return {"user": user["data"]}

    def login(self, user_id: str) -> dict[str, Any]:
        session = self.client.post("/v1/auth/session/create", {"user_id": user_id, "method": "password"})
        return {"session": session["data"]}

    def prepare_matter(self, matter: MatterIntake, user_id: str) -> dict[str, str]:
        """Cross the authenticated session with intake and delivery follow-up."""
        session = self.login(user_id)["session"]
        return {
            "matter": matter.matter_title,
            "document": matter.document_name,
            "deadline": matter.deadline,
            "follow_up": f"Email {matter.client_email} before {matter.deadline}",
            "session_id": str(session.get("session_id", "")),
        }


def signup_or_reject(service: LegalTechService, request: SignupRequest) -> tuple[int, dict[str, Any]]:
    try:
        return 201, service.signup(request)
    except InfraiError as exc:
        return exc.status if 400 <= exc.status < 500 else 502, {"error": exc.code}
