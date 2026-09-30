"""Via Vitae Orchestrator — human-supervised coordination of assistive agents.

The orchestrator holds no data-store or network access; it only sequences agents
and enforces the control gates:

* personal data is never processed without a verified lawful basis (halt first);
* safeguarding escalations cannot be suppressed by an approval;
* nothing is ever auto-approved or sent — an explicit human decision is required.
"""

from __future__ import annotations

from app.agents.audit import AuditAgent
from app.agents.base import Agent, AgentRegistry
from app.agents.classification import DataClassificationAgent
from app.agents.consent import ConsentAgent
from app.agents.draft_response import DraftResponseAgent
from app.agents.human_review import HumanReviewAgent
from app.agents.intake import IntakeAgent
from app.agents.retrieval import (
    InformationRetrievalAgent,
    NullRetrievalSource,
    RetrievalSource,
)
from app.agents.safeguarding import SafeguardingEscalationAgent
from app.agents.summary import CaseSummaryAgent
from app.audit.stream import AuditStream
from app.config import BoundarySettings
from app.contracts.artifacts import SafeguardingAssessment
from app.contracts.audit import AuditEvent, AuditEventType
from app.contracts.cases import Case, IntakeRequest
from app.contracts.pipeline import PipelineResult, PipelineStatus
from app.contracts.review import HumanReviewDecision, ReviewDecision, ReviewOutcome
from app.security.boundary import BoundaryGuard


class ViaVitaeOrchestrator:
    """Sequences assistive agents behind mandatory human supervision."""

    name: str = "orchestrator"

    def __init__(
        self,
        *,
        intake: IntakeAgent,
        classification: DataClassificationAgent,
        consent: ConsentAgent,
        retrieval: InformationRetrievalAgent,
        summary: CaseSummaryAgent,
        draft: DraftResponseAgent,
        safeguarding: SafeguardingEscalationAgent,
        human_review: HumanReviewAgent,
        audit: AuditAgent,
        guard: BoundaryGuard,
    ) -> None:
        self._intake = intake
        self._classification = classification
        self._consent = consent
        self._retrieval = retrieval
        self._summary = summary
        self._draft = draft
        self._safeguarding = safeguarding
        self._human_review = human_review
        self._audit = audit
        self._guard = guard

        components: tuple[Agent, ...] = (
            self,
            intake,
            classification,
            consent,
            retrieval,
            summary,
            draft,
            safeguarding,
            human_review,
            audit,
        )
        self._registry = AgentRegistry()
        for component in components:
            self._registry.register(component)

    @property
    def agent_names(self) -> list[str]:
        return self._registry.names()

    @property
    def audit_events(self) -> tuple[AuditEvent, ...]:
        return self._audit.stream.events()

    def process(
        self, request: IntakeRequest, *, human_decision: HumanReviewDecision | None = None
    ) -> PipelineResult:
        self._guard.verify_isolation()

        case = self._intake.intake(request)
        self._record(AuditEventType.INTAKE, case, self._intake.name, "request normalized")

        case = self._classification.classify(case)
        self._record(
            AuditEventType.CLASSIFICATION,
            case,
            self._classification.name,
            f"sensitivity={case.sensitivity}",
        )

        consent_state = self._consent.evaluate(case)
        self._record(
            AuditEventType.CONSENT_CHECK,
            case,
            self._consent.name,
            f"verified={consent_state.verified} reason={consent_state.reason}",
        )

        if not consent_state.verified:
            self._record(
                AuditEventType.HALT,
                case,
                self.name,
                "halted: no verified lawful basis for personal data",
            )
            return PipelineResult(
                case_id=case.case_id,
                status=PipelineStatus.HALTED_NO_CONSENT,
                consent=consent_state,
            )

        retrieval = self._retrieval.retrieve(case)
        self._record(
            AuditEventType.RETRIEVAL,
            case,
            self._retrieval.name,
            f"documents={len(retrieval.documents)}",
        )

        summary = self._summary.summarize(case, retrieval)
        self._record(AuditEventType.SUMMARY, case, self._summary.name, f"chars={len(summary.text)}")

        safeguard = self._safeguarding.assess(case, summary)
        self._record(
            AuditEventType.SAFEGUARDING,
            case,
            self._safeguarding.name,
            f"escalated={safeguard.escalated}",
        )

        draft = self._draft.draft(case, summary)
        self._record(AuditEventType.DRAFT, case, self._draft.name, "draft produced; not sent")

        if human_decision is None:
            status = (
                PipelineStatus.ESCALATED
                if safeguard.escalated
                else PipelineStatus.PENDING_HUMAN_REVIEW
            )
            self._record(
                AuditEventType.HUMAN_REVIEW, case, self.name, f"awaiting review (status={status})"
            )
            return PipelineResult(
                case_id=case.case_id,
                status=status,
                consent=consent_state,
                summary=summary,
                draft=draft,
                safeguarding=safeguard,
            )

        outcome = self._human_review.review(case, human_decision)
        self._record(
            AuditEventType.HUMAN_REVIEW,
            case,
            self._human_review.name,
            f"decision={outcome.decision} reviewer={outcome.reviewer_id}",
        )
        return PipelineResult(
            case_id=case.case_id,
            status=self._resolve_status(safeguard, outcome),
            consent=consent_state,
            summary=summary,
            draft=draft,
            safeguarding=safeguard,
            review=outcome,
        )

    def _resolve_status(
        self, safeguard: SafeguardingAssessment, outcome: ReviewOutcome
    ) -> PipelineStatus:
        # A safeguarding escalation can never be suppressed by a human approval.
        if safeguard.escalated:
            return PipelineStatus.ESCALATED
        if outcome.approved:
            return PipelineStatus.APPROVED
        if outcome.decision is ReviewDecision.REJECTED:
            return PipelineStatus.REJECTED
        return PipelineStatus.NEEDS_INFO

    def _record(self, event_type: AuditEventType, case: Case, actor: str, detail: str) -> None:
        self._audit.record(event_type=event_type, case_id=case.case_id, actor=actor, detail=detail)


def build_default_orchestrator(
    settings: BoundarySettings,
    *,
    retrieval_source: RetrievalSource | None = None,
    audit_stream: AuditStream | None = None,
) -> ViaVitaeOrchestrator:
    """Assemble an orchestrator wired to isolated, read-only defaults."""
    guard = BoundaryGuard(settings)
    guard.verify_isolation()
    source: RetrievalSource = (
        NullRetrievalSource() if retrieval_source is None else retrieval_source
    )
    stream: AuditStream = AuditStream() if audit_stream is None else audit_stream
    return ViaVitaeOrchestrator(
        intake=IntakeAgent(),
        classification=DataClassificationAgent(),
        consent=ConsentAgent(),
        retrieval=InformationRetrievalAgent(source, guard),
        summary=CaseSummaryAgent(),
        draft=DraftResponseAgent(),
        safeguarding=SafeguardingEscalationAgent(),
        human_review=HumanReviewAgent(),
        audit=AuditAgent(stream),
        guard=guard,
    )
