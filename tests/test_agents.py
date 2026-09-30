"""Contract + behaviour tests for the individual Via Vitae agents."""

from __future__ import annotations

import pytest
from pydantic import SecretStr, ValidationError

from viavitae_hermes.agents.audit import AuditAgent
from viavitae_hermes.agents.classification import DataClassificationAgent
from viavitae_hermes.agents.consent import ConsentAgent
from viavitae_hermes.agents.draft_response import DraftResponseAgent
from viavitae_hermes.agents.human_review import HumanReviewAgent, HumanReviewRequiredError
from viavitae_hermes.agents.intake import IntakeAgent
from viavitae_hermes.agents.retrieval import InformationRetrievalAgent, NullRetrievalSource
from viavitae_hermes.agents.safeguarding import SafeguardingEscalationAgent
from viavitae_hermes.agents.summary import CaseSummaryAgent
from viavitae_hermes.audit.stream import AuditStream
from viavitae_hermes.config import BoundarySettings
from viavitae_hermes.contracts.artifacts import CaseSummary, RetrievalResult
from viavitae_hermes.contracts.audit import AuditEventType
from viavitae_hermes.contracts.cases import Case, IntakeRequest, SensitivityLevel
from viavitae_hermes.contracts.consent import LawfulBasis
from viavitae_hermes.contracts.review import HumanReviewDecision, ReviewDecision
from viavitae_hermes.security.boundary import BoundaryGuard


def _settings() -> BoundarySettings:
    return BoundarySettings(
        database_dsn=SecretStr("postgresql+psycopg://via:s@localhost/viavitae"),
        vector_index_id="viavitae-cases-v1",
        kms_key_id="arn:kms:eu-west-1:000:key/viavitae",
        checkpoint_namespace="viavitae",
        audit_stream_id="viavitae-audit",
        secrets_ref=SecretStr("vault:viavitae"),
        deployment_identity="sp-viavitae-hermes",
    )


def _guard() -> BoundaryGuard:
    return BoundaryGuard(_settings())


# --- Intake -----------------------------------------------------------------
def test_intake_normalizes_request_into_a_case() -> None:
    request = IntakeRequest(subject="Support", raw_input="Please help", channel="email")
    case = IntakeAgent().intake(request)
    assert isinstance(case, Case)
    assert case.subject == "Support"
    assert case.raw_input == "Please help"
    assert case.case_id
    assert case.sensitivity is None  # not classified at intake


def test_intake_preserves_supplied_case_id() -> None:
    request = IntakeRequest(case_id="case-42", subject="S", raw_input="x")
    assert IntakeAgent().intake(request).case_id == "case-42"


# --- Classification ---------------------------------------------------------
def test_classification_flags_personal_data() -> None:
    case = Case(subject="user", raw_input="my email is a@b.com")
    assert DataClassificationAgent().classify(case).sensitivity is SensitivityLevel.PERSONAL


def test_classification_flags_special_category() -> None:
    case = Case(subject="user", raw_input="my medical diagnosis")
    result = DataClassificationAgent().classify(case)
    assert result.sensitivity is SensitivityLevel.SPECIAL_CATEGORY


def test_classification_defaults_to_internal_never_public() -> None:
    case = Case(subject="ops", raw_input="quarterly figures")
    assert DataClassificationAgent().classify(case).sensitivity is SensitivityLevel.INTERNAL


# --- Consent ----------------------------------------------------------------
def test_consent_fails_closed_for_personal_without_basis() -> None:
    case = Case(
        subject="u",
        raw_input="email a@b.com",
        sensitivity=SensitivityLevel.PERSONAL,
        lawful_basis=LawfulBasis.NONE,
    )
    assert ConsentAgent().evaluate(case).verified is False


def test_consent_verified_for_personal_with_basis() -> None:
    case = Case(
        subject="u",
        raw_input="email a@b.com",
        sensitivity=SensitivityLevel.PERSONAL,
        lawful_basis=LawfulBasis.CONSENT,
    )
    assert ConsentAgent().evaluate(case).verified is True


def test_consent_verified_for_non_personal() -> None:
    case = Case(subject="ops", raw_input="figures", sensitivity=SensitivityLevel.INTERNAL)
    assert ConsentAgent().evaluate(case).verified is True


def test_consent_fails_closed_for_unclassified() -> None:
    case = Case(subject="u", raw_input="x")  # sensitivity is None
    assert ConsentAgent().evaluate(case).verified is False


# --- Retrieval --------------------------------------------------------------
def test_retrieval_is_read_only_and_empty_by_default() -> None:
    case = Case(subject="u", raw_input="x", sensitivity=SensitivityLevel.INTERNAL)
    agent = InformationRetrievalAgent(NullRetrievalSource(), _guard())
    result = agent.retrieve(case)
    assert result.documents == ()
    assert result.case_id == case.case_id


# --- Summary ----------------------------------------------------------------
def test_summary_is_bounded_and_source_attributed() -> None:
    case = Case(subject="u", raw_input="x", sensitivity=SensitivityLevel.INTERNAL)
    retrieval = RetrievalResult(case_id=case.case_id, documents=())
    summary = CaseSummaryAgent().summarize(case, retrieval)
    assert summary.case_id == case.case_id
    assert isinstance(summary.source_ids, tuple)


# --- Draft response ---------------------------------------------------------
def test_draft_is_marked_not_sent_and_has_no_egress_capability() -> None:
    case = Case(subject="u", raw_input="x", sensitivity=SensitivityLevel.INTERNAL)
    summary = CaseSummary(case_id=case.case_id, text="s", source_ids=())
    agent = DraftResponseAgent()
    draft = agent.draft(case, summary)
    assert draft.is_draft is True
    assert "DRAFT" in draft.body
    for forbidden in ("send", "dispatch", "post", "email", "deliver", "transmit"):
        assert not hasattr(agent, forbidden)
        assert not hasattr(draft, forbidden)


# --- Safeguarding -----------------------------------------------------------
def test_safeguarding_escalates_on_trigger() -> None:
    case = Case(subject="u", raw_input="I feel at risk of harm")
    summary = CaseSummary(case_id=case.case_id, text="", source_ids=())
    assessment = SafeguardingEscalationAgent().assess(case, summary)
    assert assessment.escalated is True
    assert assessment.alert is not None


def test_safeguarding_quiet_without_trigger() -> None:
    case = Case(subject="u", raw_input="routine question about opening times")
    summary = CaseSummary(case_id=case.case_id, text="", source_ids=())
    assert SafeguardingEscalationAgent().assess(case, summary).escalated is False


# --- Human review -----------------------------------------------------------
def test_human_review_required_when_no_decision() -> None:
    case = Case(subject="u", raw_input="x")
    with pytest.raises(HumanReviewRequiredError):
        HumanReviewAgent().review(case, None)


def test_human_review_rejects_mismatched_case() -> None:
    case = Case(subject="u", raw_input="x")
    decision = HumanReviewDecision(
        case_id="other",
        reviewer_id="r1",
        decision=ReviewDecision.APPROVED,
        rationale="ok",
    )
    with pytest.raises(HumanReviewRequiredError):
        HumanReviewAgent().review(case, decision)


def test_human_review_records_explicit_decision() -> None:
    case = Case(subject="u", raw_input="x")
    decision = HumanReviewDecision(
        case_id=case.case_id,
        reviewer_id="r1",
        decision=ReviewDecision.APPROVED,
        rationale="looks good",
    )
    outcome = HumanReviewAgent().review(case, decision)
    assert outcome.approved is True
    assert outcome.reviewer_id == "r1"


def test_human_review_decision_requires_rationale() -> None:
    with pytest.raises(ValidationError):
        HumanReviewDecision(
            case_id="c",
            reviewer_id="r1",
            decision=ReviewDecision.APPROVED,
            rationale="   ",
        )


def test_human_review_decision_requires_reviewer_id() -> None:
    with pytest.raises(ValidationError):
        HumanReviewDecision(
            case_id="c",
            reviewer_id="   ",
            decision=ReviewDecision.APPROVED,
            rationale="ok",
        )


# --- Audit ------------------------------------------------------------------
def test_audit_agent_appends_to_stream() -> None:
    stream = AuditStream()
    agent = AuditAgent(stream)
    agent.record(event_type=AuditEventType.INTAKE, case_id="c1", actor="x", detail="d")
    assert len(stream) == 1
