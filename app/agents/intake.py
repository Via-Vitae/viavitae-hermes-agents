"""Intake Agent — normalize inbound requests into typed cases (no I/O)."""

from __future__ import annotations

from uuid import uuid4

from app.contracts.cases import Case, IntakeRequest


class IntakeAgent:
    """Turns an :class:`IntakeRequest` into an immutable :class:`Case`."""

    name: str = "intake-agent"

    def intake(self, request: IntakeRequest) -> Case:
        return Case(
            case_id=request.case_id or uuid4().hex,
            subject=request.subject,
            raw_input=request.raw_input,
            channel=request.channel,
            lawful_basis=request.lawful_basis,
        )
