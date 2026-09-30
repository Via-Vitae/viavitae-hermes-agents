"""End-to-end tests for the human-supervised Via Vitae orchestrator."""

from __future__ import annotations

from app.agents.orchestrator import ViaVitaeOrchestrator, build_default_orchestrator
from app.config import BoundarySettings
from app.contracts.audit import AuditEventType
from app.contracts.cases import IntakeRequest
from app.contracts.pipeline import PipelineStatus
from app.contracts.review import HumanReviewDecision, ReviewDecision
from pydantic import SecretStr


def _orchestrator() -> ViaVitaeOrchestrator:
    settings = BoundarySettings(
        database_dsn=SecretStr("postgresql+psycopg://via:s@localhost/viavitae"),
        vector_index_id="viavitae-cases-v1",
        kms_key_id="arn:kms:eu-west-1:000:key/viavitae",
        checkpoint_namespace="viavitae",
        audit_stream_id="viavitae-audit",
        secrets_ref=SecretStr("vault:viavitae"),
        deployment_identity="sp-viavitae-hermes",
    )
    return build_default_orchestrator(settings)


def _decision(case_id: str, decision: ReviewDecision, rationale: str) -> HumanReviewDecision:
    return HumanReviewDecision(
        case_id=case_id,
        reviewer_id="human-1",
        decision=decision,
        rationale=rationale,
    )


def test_no_decision_is_never_auto_approved() -> None:
    orch = _orchestrator()
    request = IntakeRequest(case_id="c1", subject="Support", raw_input="opening times")
    result = orch.process(request)
    assert result.status is PipelineStatus.PENDING_HUMAN_REVIEW
    assert result.draft is not None
    assert result.draft.is_draft is True


def test_personal_data_without_basis_halts_before_retrieval() -> None:
    orch = _orchestrator()
    request = IntakeRequest(case_id="c3", subject="user", raw_input="my email is a@b.com")
    result = orch.process(request)
    assert result.status is PipelineStatus.HALTED_NO_CONSENT
    types = [event.event_type for event in orch.audit_events]
    assert AuditEventType.RETRIEVAL not in types
    assert AuditEventType.HALT in types


def test_approved_only_after_human_review() -> None:
    orch = _orchestrator()
    request = IntakeRequest(case_id="c2", subject="Support", raw_input="opening times")
    result = orch.process(request, human_decision=_decision("c2", ReviewDecision.APPROVED, "ok"))
    assert result.status is PipelineStatus.APPROVED


def test_rejected_decision_is_honoured() -> None:
    orch = _orchestrator()
    request = IntakeRequest(case_id="c6", subject="Support", raw_input="opening times")
    result = orch.process(
        request, human_decision=_decision("c6", ReviewDecision.REJECTED, "inaccurate")
    )
    assert result.status is PipelineStatus.REJECTED


def test_needs_info_decision_is_honoured() -> None:
    orch = _orchestrator()
    request = IntakeRequest(case_id="c7", subject="Support", raw_input="opening times")
    result = orch.process(
        request, human_decision=_decision("c7", ReviewDecision.NEEDS_INFO, "need more detail")
    )
    assert result.status is PipelineStatus.NEEDS_INFO


def test_safeguarding_cannot_be_suppressed_by_approval() -> None:
    orch = _orchestrator()
    request = IntakeRequest(case_id="c4", subject="user", raw_input="I am at risk of harm")
    result = orch.process(
        request, human_decision=_decision("c4", ReviewDecision.APPROVED, "approved")
    )
    assert result.status is PipelineStatus.ESCALATED
    assert result.safeguarding is not None
    assert result.safeguarding.escalated is True


def test_every_stage_is_audited() -> None:
    orch = _orchestrator()
    request = IntakeRequest(case_id="c5", subject="Support", raw_input="opening times")
    orch.process(request)
    types = {event.event_type for event in orch.audit_events}
    assert AuditEventType.INTAKE in types
    assert AuditEventType.CLASSIFICATION in types
    assert AuditEventType.CONSENT_CHECK in types


def test_orchestrator_registers_its_components() -> None:
    orch = _orchestrator()
    names = orch.agent_names
    assert "orchestrator" in names
    assert "human-review-agent" in names
    assert "audit-agent" in names
