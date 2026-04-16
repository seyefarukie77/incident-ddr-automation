"""
PIR Automation Service (Mock) — FastAPI + Pydantic, single-file.

Workplace scenario:
- Incidents follow Detect → Diagnose → Recover (DDR)
- Post Incident Review (PIR/PMR) needs "readiness" checks and a generated PIR pack

Realistic simplifications / limitations (intentional for assessment):
- Uses static in-memory data only (no DB, no persistence)
- ISO datetime parsing is best-effort and assumes naive/UTC-ish strings (no timezone normalization)
- Validation rules are simplified and severity-based only (no service-specific nuance)
- PIR pack generation is deterministic but does not auto-fix data issues (e.g., timeline ordering)
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Set

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field, field_validator


# ----------------------------
# Enums / constants
# ----------------------------

class Severity(str, Enum):
    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"


class Phase(str, Enum):
    DETECT = "DETECT"
    DIAGNOSE = "DIAGNOSE"
    RECOVER = "RECOVER"
    PIR = "PIR"


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


ALLOWED_DETECTED_BY: Set[str] = {"monitoring", "customer", "report"}
ALLOWED_ACTION_STATUS: Set[str] = {"OPEN", "IN_PROGRESS", "DONE"}


# ----------------------------
# Pydantic domain models
# ----------------------------

class Detection(BaseModel):
    detectedBy: Optional[str] = Field(None, description="monitoring/customer/report")
    detectionSignals: List[str] = Field(default_factory=list)
    timeToDetectMinutes: int = 0


class Hypothesis(BaseModel):
    hypothesis: str
    confidence: float
    evidenceRefs: List[str] = Field(default_factory=list)

    @field_validator("confidence")
    @classmethod
    def confidence_must_be_0_to_1(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("confidence must be between 0 and 1")
        return v


class Diagnosis(BaseModel):
    suspectedComponents: List[str] = Field(default_factory=list)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    timeToDiagnoseMinutes: int = 0

    @field_validator("timeToDiagnoseMinutes")
    @classmethod
    def ttd_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("timeToDiagnoseMinutes must be >= 0")
        return v


class Recovery(BaseModel):
    mitigations: List[str] = Field(default_factory=list)
    fixForward: Optional[str] = None
    rollbackPerformed: bool = False
    timeToRecoverMinutes: int = 0

    @field_validator("timeToRecoverMinutes")
    @classmethod
    def ttr_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("timeToRecoverMinutes must be >= 0")
        return v


class TimelineEvent(BaseModel):
    timestamp: str
    eventType: str
    description: str
    owner: str


class ActionItem(BaseModel):
    actionId: str
    description: str
    owner: Optional[str] = None
    dueDate: Optional[str] = None  # ISO string expected
    status: str


class IncidentRecord(BaseModel):
    incidentId: str
    title: str
    serviceName: str
    severity: Severity
    startTime: str
    endTime: Optional[str] = None

    detection: Detection
    diagnosis: Diagnosis
    recovery: Recovery

    customerImpact: str
    businessImpact: str

    timelineEvents: List[TimelineEvent] = Field(default_factory=list)
    actionItems: List[ActionItem] = Field(default_factory=list)
    knownGaps: List[str] = Field(default_factory=list)


class CheckResult(BaseModel):
    phase: Phase
    checkName: str
    status: CheckStatus
    message: str


class DDRAssessmentResult(BaseModel):
    incidentId: str
    overallStatus: CheckStatus
    checks: List[CheckResult]
    failedChecksSummary: List[str]
    suggestedImprovements: List[str]


class RootCauseSection(BaseModel):
    summary: str
    hypotheses: List[Dict[str, Any]]
    confirmedRootCause: Optional[str] = None
    contributingFactors: List[str] = Field(default_factory=list)


class PIRPack(BaseModel):
    incidentId: str
    severity: Severity
    executiveSummary: str
    timeline: List[TimelineEvent]
    rootCauseSection: RootCauseSection
    actions: List[ActionItem]
    metrics: Dict[str, Any]
    gaps: List[str]
    suggestedImprovements: List[str]
    readinessStatus: CheckStatus


class PIRPackRequest(BaseModel):
    includeGaps: bool = True
    format: Literal["json"] = "json"


class RulesResponse(BaseModel):
    severity: str
    rules: Dict[str, Any]


# ----------------------------
# Mock dataset (5 incidents)
# - 2+ have data quality issues
# - 1 is a "good" example
# ----------------------------

MOCK_INCIDENTS: Dict[str, IncidentRecord] = {
    # Good SEV1 example (mostly passes)
    "INC13089493": IncidentRecord(
        incidentId="INC13089493",
        title="Desktop logon failures due to token validation regression",
        serviceName="DigiMod Desktop Logon",
        severity=Severity.SEV1,
        startTime="2026-04-08T01:16:00",
        endTime="2026-04-08T04:58:00",
        detection=Detection(
            detectedBy="monitoring",
            detectionSignals=["Synthetic journey failure", "Elevated 401 rate on edge gateway"],
            timeToDetectMinutes=7,
        ),
        diagnosis=Diagnosis(
            suspectedComponents=["ID Token Validator", "Edge Policy"],
            hypotheses=[
                Hypothesis(
                    hypothesis="Token CNF claim missing due to upstream change",
                    confidence=0.8,
                    evidenceRefs=["SNOW:CHG1234567", "LOG:edge-401-spike"],
                )
            ],
            timeToDiagnoseMinutes=120,
        ),
        recovery=Recovery(
            mitigations=["Revert journey routing to monolith (no-regrets)", "Rollback edge policy to previous version"],
            fixForward="Add automated contract test for CNF claim and block deploy on failure",
            rollbackPerformed=True,
            timeToRecoverMinutes=222,
        ),
        customerImpact="Customers could not complete desktop logon for multiple brands during impact window.",
        businessImpact="Increased contact centre load and reduced digital conversion during peak morning period.",
        timelineEvents=[
            TimelineEvent(timestamp="2026-04-08T01:16:00", eventType="DETECT", description="Synthetic failure detected", owner="SRE"),
            TimelineEvent(timestamp="2026-04-08T01:23:00", eventType="DETECT", description="Incident created and flagged", owner="Ops"),
            TimelineEvent(timestamp="2026-04-08T02:30:00", eventType="DIAGNOSE", description="Incident bridge opened", owner="IM"),
            TimelineEvent(timestamp="2026-04-08T03:30:00", eventType="DIAGNOSE", description="401 Invalid fingerprint cookie identified", owner="Engineer"),
            TimelineEvent(timestamp="2026-04-08T04:30:00", eventType="RECOVER", description="Revert routing to monolith for all brands", owner="IM"),
            TimelineEvent(timestamp="2026-04-08T04:58:00", eventType="RECOVER", description="Service stable; monitoring green", owner="SRE"),
        ],
        actionItems=[
            ActionItem(actionId="AI-001", description="Implement CNF contract test in CI pipeline", owner="K. Seth", dueDate="2026-04-22T17:00:00", status="OPEN"),
            ActionItem(actionId="AI-002", description="Expand synthetic coverage for desktop logon journey", owner="J. Goddard", dueDate="2026-04-29T17:00:00", status="IN_PROGRESS"),
        ],
        knownGaps=["Monitoring gap between change completion and detection", "Limited offshore log access during diagnosis"],
    ),

    # SEV2 with missing endTime (PIR readiness should FAIL)
    "INC13090001": IncidentRecord(
        incidentId="INC13090001",
        title="Intermittent payments API timeouts",
        serviceName="Payments API",
        severity=Severity.SEV2,
        startTime="2026-03-12T10:36:00",
        endTime=None,  # data quality issue
        detection=Detection(
            detectedBy="report",
            detectionSignals=["Support ticket volume spike"],
            timeToDetectMinutes=25,
        ),
        diagnosis=Diagnosis(
            suspectedComponents=["Gateway Timeout Handler"],
            hypotheses=[
                Hypothesis(
                    hypothesis="Downstream dependency saturation causing thread pool exhaustion",
                    confidence=0.6,
                    evidenceRefs=["APM:latency-heatmap"],
                )
            ],
            timeToDiagnoseMinutes=90,
        ),
        recovery=Recovery(
            mitigations=["Increased timeout threshold temporarily"],
            fixForward="Introduce circuit breaker and retry budget",
            rollbackPerformed=False,
            timeToRecoverMinutes=60,
        ),
        customerImpact="Some customers experienced delayed payment confirmations.",
        businessImpact="Increased operational monitoring and elevated failure rates during the window.",
        timelineEvents=[
            TimelineEvent(timestamp="2026-03-12T10:36:00", eventType="DETECT", description="Ops noticed alerts in dashboard", owner="Ops"),
            TimelineEvent(timestamp="2026-03-12T11:05:00", eventType="DIAGNOSE", description="Timeout pattern linked to dependency", owner="Engineer"),
        ],
        actionItems=[
            ActionItem(actionId="AI-101", description="Add circuit breaker for dependency X", owner="A. Arora", dueDate="2026-03-26T17:00:00", status="OPEN"),
        ],
        knownGaps=[],
    ),

    # SEV1 with out-of-order timeline and invalid action status (validation should FAIL)
    "INC13091010": IncidentRecord(
        incidentId="INC13091010",
        title="Authentication failures after policy update",
        serviceName="ID & Auth Platform",
        severity=Severity.SEV1,
        startTime="2026-04-01T23:39:00",
        endTime="2026-04-02T01:10:00",
        detection=Detection(
            detectedBy="monitoring",
            detectionSignals=["Error rate spike"],
            timeToDetectMinutes=15,
        ),
        diagnosis=Diagnosis(
            suspectedComponents=[],  # SEV1 requires non-empty -> issue
            hypotheses=[
                Hypothesis(
                    hypothesis="Edge policy misconfiguration blocking valid tokens",
                    confidence=0.7,
                    evidenceRefs=["CHG:edge-policy-789"],
                )
            ],
            timeToDiagnoseMinutes=30,
        ),
        recovery=Recovery(
            mitigations=["Applied hotfix policy update"],
            fixForward="Add automated pre-prod token validation checks",
            rollbackPerformed=False,
            timeToRecoverMinutes=40,
        ),
        customerImpact="Customers experienced login failures for a subset of journeys.",
        businessImpact="Drop in successful authentication rate; increased complaints.",
        timelineEvents=[
            # Out of order on purpose:
            TimelineEvent(timestamp="2026-04-02T00:30:00", eventType="DIAGNOSE", description="Root cause suspected", owner="Engineer"),
            TimelineEvent(timestamp="2026-04-01T23:45:00", eventType="DETECT", description="Alert triggered", owner="SRE"),
            TimelineEvent(timestamp="2026-04-02T01:10:00", eventType="RECOVER", description="Policy updated and stable", owner="IM"),
        ],
        actionItems=[
            ActionItem(actionId="AI-201", description="Create regression test suite for edge policies", owner="D. Loney", dueDate="2026-04-15T17:00:00", status="PENDING"),  # invalid status
        ],
        knownGaps=["Timeline recorded out of order in notes", "Action status taxonomy mismatch"],
    ),

    # SEV2 with empty customerImpact (should FAIL for SEV2)
    "INC13092020": IncidentRecord(
        incidentId="INC13092020",
        title="Conversational banking provider outage",
        serviceName="Conversational Banking",
        severity=Severity.SEV2,
        startTime="2026-03-24T10:36:00",
        endTime="2026-03-24T11:30:00",
        detection=Detection(
            detectedBy="customer",
            detectionSignals=[],  # SEV2 should require at least 1 -> issue
            timeToDetectMinutes=0,
        ),
        diagnosis=Diagnosis(
            suspectedComponents=["3rd Party Provider"],
            hypotheses=[],  # SEV2 requires at least 1 -> issue
            timeToDiagnoseMinutes=20,
        ),
        recovery=Recovery(
            mitigations=[],  # SEV2 requires at least 1 -> issue
            fixForward=None,  # SEV2 requires present -> issue
            rollbackPerformed=False,
            timeToRecoverMinutes=54,
        ),
        customerImpact="",  # issue
        businessImpact="Service unavailable; colleague response capability reduced.",
        timelineEvents=[],
        actionItems=[],
        knownGaps=["Missing PIR details from vendor", "No structured timeline captured"],
    ),

    # SEV3 lighter requirements; still validates formats/enums
    "INC13093030": IncidentRecord(
        incidentId="INC13093030",
        title="Minor UI glitch in account overview",
        serviceName="Account Overview",
        severity=Severity.SEV3,
        startTime="2026-04-10T09:00:00",
        endTime="2026-04-10T10:00:00",
        detection=Detection(
            detectedBy="report",
            detectionSignals=[],
            timeToDetectMinutes=30,
        ),
        diagnosis=Diagnosis(
            suspectedComponents=["Frontend Bundle"],
            hypotheses=[],
            timeToDiagnoseMinutes=15,
        ),
        recovery=Recovery(
            mitigations=["Feature flag disabled for affected cohort"],
            fixForward=None,
            rollbackPerformed=False,
            timeToRecoverMinutes=25,
        ),
        customerImpact="Small cohort saw misaligned text on one screen.",
        businessImpact="Negligible; tracked as defect and triaged.",
        timelineEvents=[
            TimelineEvent(timestamp="2026-04-10T09:00:00", eventType="DETECT", description="Issue reported by colleague", owner="Support"),
            TimelineEvent(timestamp="2026-04-10T09:30:00", eventType="DIAGNOSE", description="Identified CSS regression", owner="Engineer"),
            TimelineEvent(timestamp="2026-04-10T10:00:00", eventType="RECOVER", description="Feature flag disabled", owner="Engineer"),
        ],
        actionItems=[
            ActionItem(actionId="AI-301", description="Fix CSS regression in next sprint", owner="F. Hendriks", dueDate="2026-04-24T17:00:00", status="OPEN"),
        ],
        knownGaps=[],
    ),
}


# ----------------------------
# Severity rules (exposed via /v1/rules/{severity})
# ----------------------------

SEVERITY_RULES: Dict[str, Dict[str, Any]] = {
    "SEV1": {
        "detect": {
            "detectionSignalsRequired": True,
            "hypothesesRequired": True,
            "mitigationsRequired": True,
            "fixForwardRequired": True,
            "suspectedComponentsRequired": True,
            "customerImpactRequired": True,
            "actionItemsRequired": True,
        },
        "notes": "Strictest: expects strong DDR completeness and PIR readiness fields.",
    },
    "SEV2": {
        "detect": {
            "detectionSignalsRequired": True,
            "hypothesesRequired": True,
            "mitigationsRequired": True,
            "fixForwardRequired": True,
            "suspectedComponentsRequired": False,
            "customerImpactRequired": True,
            "actionItemsRequired": False,
        },
        "notes": "Medium strictness: key DDR fields expected; action items encouraged but not mandatory.",
    },
    "SEV3": {
        "detect": {
            "detectionSignalsRequired": False,
            "hypothesesRequired": False,
            "mitigationsRequired": False,
            "fixForwardRequired": False,
            "suspectedComponentsRequired": False,
            "customerImpactRequired": False,
            "actionItemsRequired": False,
        },
        "notes": "Light: validates formats/enums; allows fewer required fields.",
    },
}


# ----------------------------
# Utilities (deterministic, unit-test friendly)
# ----------------------------

def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    Best-effort ISO8601 parsing.
    Supports 'Z' suffix by converting to +00:00.
    """
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        return None
    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(v)
    except ValueError:
        return None


def is_non_trivial_text(text: str, min_len: int = 10) -> bool:
    return isinstance(text, str) and len(text.strip()) >= min_len


def get_incident_or_404(incident_id: str) -> IncidentRecord:
    incident = MOCK_INCIDENTS.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    return incident


def add_check(
    checks: List[CheckResult],
    phase: Phase,
    check_name: str,
    passed: bool,
    pass_msg: str,
    fail_msg: str,
) -> None:
    checks.append(
        CheckResult(
            phase=phase,
            checkName=check_name,
            status=CheckStatus.PASS if passed else CheckStatus.FAIL,
            message=pass_msg if passed else fail_msg,
        )
    )


def evaluate_detect(incident: IncidentRecord, rules: Dict[str, Any]) -> List[CheckResult]:
    checks: List[CheckResult] = []
    det = incident.detection

    add_check(
        checks,
        Phase.DETECT,
        "Detected By Enum",
        passed=(det.detectedBy in ALLOWED_DETECTED_BY),
        pass_msg="detectedBy is valid",
        fail_msg=f"detectedBy must be one of {sorted(ALLOWED_DETECTED_BY)}",
    )

    signals_required = bool(rules["detect"]["detectionSignalsRequired"])
    add_check(
        checks,
        Phase.DETECT,
        "Detection Signals Present",
        passed=(not signals_required) or (len(det.detectionSignals) >= 1),
        pass_msg="detectionSignals present (or not required for this severity)",
        fail_msg="detectionSignals must include at least 1 item for SEV1/SEV2",
    )

    add_check(
        checks,
        Phase.DETECT,
        "Time To Detect Range",
        passed=(0 <= det.timeToDetectMinutes <= 1440),
        pass_msg="timeToDetectMinutes within range",
        fail_msg="timeToDetectMinutes must be between 0 and 1440",
    )

    return checks


def evaluate_diagnose(incident: IncidentRecord, rules: Dict[str, Any]) -> List[CheckResult]:
    checks: List[CheckResult] = []
    diag = incident.diagnosis

    hypotheses_required = bool(rules["detect"]["hypothesesRequired"])
    add_check(
        checks,
        Phase.DIAGNOSE,
        "Hypotheses Present",
        passed=(not hypotheses_required) or (len(diag.hypotheses) >= 1),
        pass_msg="hypotheses present (or not required for this severity)",
        fail_msg="At least 1 hypothesis is required for SEV1/SEV2",
    )

    # Confidence bounds are validated by Pydantic, but also check deterministically here:
    bad_conf = [h for h in diag.hypotheses if not (0 <= h.confidence <= 1)]
    add_check(
        checks,
        Phase.DIAGNOSE,
        "Hypothesis Confidence Bounds",
        passed=(len(bad_conf) == 0),
        pass_msg="All hypothesis confidence values are between 0 and 1",
        fail_msg="One or more hypotheses have confidence outside 0..1",
    )

    suspected_required = bool(rules["detect"]["suspectedComponentsRequired"])
    add_check(
        checks,
        Phase.DIAGNOSE,
        "Suspected Components Present",
        passed=(not suspected_required) or (len(diag.suspectedComponents) >= 1),
        pass_msg="suspectedComponents present (or not required for this severity)",
        fail_msg="suspectedComponents must not be empty for SEV1",
    )

    add_check(
        checks,
        Phase.DIAGNOSE,
        "Time To Diagnose Non-Negative",
        passed=(diag.timeToDiagnoseMinutes >= 0),
        pass_msg="timeToDiagnoseMinutes is non-negative",
        fail_msg="timeToDiagnoseMinutes must be >= 0",
    )

    return checks


def evaluate_recover(incident: IncidentRecord, rules: Dict[str, Any]) -> List[CheckResult]:
    checks: List[CheckResult] = []
    rec = incident.recovery

    mitigations_required = bool(rules["detect"]["mitigationsRequired"])
    add_check(
        checks,
        Phase.RECOVER,
        "Mitigations Present",
        passed=(not mitigations_required) or (len(rec.mitigations) >= 1),
        pass_msg="mitigations present (or not required for this severity)",
        fail_msg="mitigations must include at least 1 item for SEV1/SEV2",
    )

    fix_required = bool(rules["detect"]["fixForwardRequired"])
    add_check(
        checks,
        Phase.RECOVER,
        "Fix Forward Present",
        passed=(not fix_required) or (isinstance(rec.fixForward, str) and rec.fixForward.strip() != ""),
        pass_msg="fixForward present (or not required for this severity)",
        fail_msg="fixForward must be present for SEV1/SEV2",
    )

    if rec.rollbackPerformed:
        mentions = " ".join(rec.mitigations).lower()
        rollback_ok = ("rollback" in mentions) or ("revert" in mentions)
        add_check(
            checks,
            Phase.RECOVER,
            "Rollback Mentioned In Mitigations",
            passed=rollback_ok,
            pass_msg="Rollback performed and mitigations mention rollback/revert",
            fail_msg="rollbackPerformed is true but mitigations do not mention rollback or revert",
        )
    else:
        add_check(
            checks,
            Phase.RECOVER,
            "Rollback Mentioned In Mitigations",
            passed=True,
            pass_msg="rollbackPerformed is false (check not applicable)",
            fail_msg="rollback check not applicable",
        )

    add_check(
        checks,
        Phase.RECOVER,
        "Time To Recover Non-Negative",
        passed=(rec.timeToRecoverMinutes >= 0),
        pass_msg="timeToRecoverMinutes is non-negative",
        fail_msg="timeToRecoverMinutes must be >= 0",
    )

    return checks


def evaluate_pir_readiness(incident: IncidentRecord, rules: Dict[str, Any]) -> List[CheckResult]:
    checks: List[CheckResult] = []

    start_dt = parse_iso_datetime(incident.startTime)
    add_check(
        checks,
        Phase.PIR,
        "StartTime Valid ISO",
        passed=(start_dt is not None),
        pass_msg="startTime is valid ISO datetime",
        fail_msg="startTime must be valid ISO datetime",
    )

    end_dt = parse_iso_datetime(incident.endTime)
    add_check(
        checks,
        Phase.PIR,
        "EndTime Present & Valid ISO",
        passed=(end_dt is not None),
        pass_msg="endTime is present and valid ISO datetime",
        fail_msg="endTime must be present and valid ISO datetime (missing endTime fails readiness)",
    )

    if start_dt and end_dt:
        add_check(
            checks,
            Phase.PIR,
            "EndTime After StartTime",
            passed=(end_dt > start_dt),
            pass_msg="endTime occurs after startTime",
            fail_msg="endTime must be after startTime",
        )
    else:
        add_check(
            checks,
            Phase.PIR,
            "EndTime After StartTime",
            passed=False,
            pass_msg="endTime occurs after startTime",
            fail_msg="Cannot validate ordering without valid startTime and endTime",
        )

    customer_required = bool(rules["detect"]["customerImpactRequired"])
    add_check(
        checks,
        Phase.PIR,
        "Customer Impact Non-Trivial",
        passed=(not customer_required) or is_non_trivial_text(incident.customerImpact),
        pass_msg="customerImpact present (or not required for this severity)",
        fail_msg="customerImpact must be present and non-trivial for SEV1/SEV2",
    )

    timeline_present = len(incident.timelineEvents) > 0
    add_check(
        checks,
        Phase.PIR,
        "Timeline Events Present",
        passed=timeline_present,
        pass_msg="timelineEvents present",
        fail_msg="timelineEvents must be present",
    )

    parsed_ts: List[Optional[datetime]] = [parse_iso_datetime(ev.timestamp) for ev in incident.timelineEvents]
    all_ts_valid = timeline_present and all(t is not None for t in parsed_ts)
    add_check(
        checks,
        Phase.PIR,
        "Timeline Timestamps Valid ISO",
        passed=all_ts_valid,
        pass_msg="All timeline event timestamps are valid ISO datetimes",
        fail_msg="One or more timeline event timestamps are invalid ISO datetimes",
    )

    chronological = False
    if all_ts_valid:
        chronological = True
        for i in range(1, len(parsed_ts)):
            if parsed_ts[i] < parsed_ts[i - 1]:
                chronological = False
                break

    add_check(
        checks,
        Phase.PIR,
        "Timeline Chronological Order",
        passed=chronological,
        pass_msg="timelineEvents are in chronological order",
        fail_msg="timelineEvents are not in chronological order",
    )

    action_required = bool(rules["detect"]["actionItemsRequired"])
    add_check(
        checks,
        Phase.PIR,
        "Action Items Present",
        passed=(not action_required) or (len(incident.actionItems) >= 1),
        pass_msg="actionItems present (or not required for this severity)",
        fail_msg="actionItems must include at least 1 item for SEV1",
    )

    if incident.severity == Severity.SEV1 and len(incident.actionItems) >= 1:
        missing_owner_due = [
            a.actionId
            for a in incident.actionItems
            if not (a.owner and a.owner.strip() and a.dueDate and parse_iso_datetime(a.dueDate))
        ]
        add_check(
            checks,
            Phase.PIR,
            "Action Items Have Owner + DueDate",
            passed=(len(missing_owner_due) == 0),
            pass_msg="All action items include owner and valid dueDate",
            fail_msg=f"Action items missing owner or valid dueDate: {missing_owner_due}",
        )
    else:
        add_check(
            checks,
            Phase.PIR,
            "Action Items Have Owner + DueDate",
            passed=True,
            pass_msg="Owner/dueDate strictness not applied for this severity",
            fail_msg="Owner/dueDate strictness not applied",
        )

    bad_status = [a.actionId for a in incident.actionItems if a.status not in ALLOWED_ACTION_STATUS]
    add_check(
        checks,
        Phase.PIR,
        "Action Item Status Enum",
        passed=(len(bad_status) == 0),
        pass_msg="All actionItem statuses are valid",
        fail_msg=f"Invalid actionItem status for actionIds: {bad_status}. Allowed: {sorted(ALLOWED_ACTION_STATUS)}",
    )

    return checks


def run_ddr_assessment(incident: IncidentRecord) -> DDRAssessmentResult:
    rules = SEVERITY_RULES[incident.severity.value]

    checks: List[CheckResult] = []
    checks.extend(evaluate_detect(incident, rules))
    checks.extend(evaluate_diagnose(incident, rules))
    checks.extend(evaluate_recover(incident, rules))
    checks.extend(evaluate_pir_readiness(incident, rules))

    failed = [c for c in checks if c.status == CheckStatus.FAIL]
    overall = CheckStatus.PASS if not failed else CheckStatus.FAIL

    failed_summaries = [c.message for c in failed]

    improvements: List[str] = []
    for c in failed:
        if c.checkName == "Timeline Chronological Order":
            improvements.append("Sort timelineEvents by timestamp before generating the PIR pack")
        elif c.checkName == "EndTime Present & Valid ISO":
            improvements.append("Populate endTime with a valid ISO datetime when the incident is resolved")
        elif c.checkName == "Customer Impact Non-Trivial":
            improvements.append("Add a clear customerImpact statement describing who was affected and how")
        elif c.checkName == "Action Item Status Enum":
            improvements.append("Standardise action item statuses to OPEN / IN_PROGRESS / DONE")
        elif c.checkName == "Action Items Have Owner + DueDate":
            improvements.append("Ensure every SEV1 action has an owner and a dueDate (valid ISO datetime)")
        elif c.checkName == "Suspected Components Present":
            improvements.append("Record suspectedComponents early to speed diagnosis and improve PIR quality")
        elif c.checkName == "Detection Signals Present":
            improvements.append("Capture at least one detection signal (alert, synthetic, ticket) for SEV1/SEV2")
        elif c.checkName == "Hypotheses Present":
            improvements.append("Document at least one hypothesis with confidence and evidence references for SEV1/SEV2")
        elif c.checkName == "Mitigations Present":
            improvements.append("Document at least one mitigation to support recoverability learning for SEV1/SEV2")
        elif c.checkName == "Fix Forward Present":
            improvements.append("Add a fixForward statement describing the durable prevention approach for SEV1/SEV2")
        else:
            improvements.append(f"Address failed check: {c.checkName}")

    # De-duplicate while preserving order
    seen: Set[str] = set()
    improvements_unique: List[str] = []
    for msg in improvements:
        if msg not in seen:
            seen.add(msg)
            improvements_unique.append(msg)

    return DDRAssessmentResult(
        incidentId=incident.incidentId,
        overallStatus=overall,
        checks=checks,
        failedChecksSummary=failed_summaries,
        suggestedImprovements=improvements_unique,
    )


def generate_executive_summary(incident: IncidentRecord, assessment: DDRAssessmentResult) -> str:
    readiness_line = f"PIR readiness: {assessment.overallStatus}."
    impact = incident.customerImpact.strip() if incident.customerImpact.strip() else "[MISSING customerImpact]"
    return (
        f"{incident.severity.value} incident in {incident.serviceName}: {incident.title}. "
        f"Customer impact: {impact} {readiness_line}"
    )


def generate_root_cause_section(incident: IncidentRecord) -> RootCauseSection:
    hypotheses = [
        {"hypothesis": h.hypothesis, "confidence": h.confidence, "evidenceRefs": h.evidenceRefs}
        for h in incident.diagnosis.hypotheses
    ]
    summary = "Root cause not confirmed yet." if not hypotheses else "Root cause under investigation based on hypotheses."
    return RootCauseSection(
        summary=summary,
        hypotheses=hypotheses,
        confirmedRootCause=None,  # placeholder-friendly
        contributingFactors=[],
    )


def generate_pir_pack(incident: IncidentRecord, request: PIRPackRequest) -> PIRPack:
    assessment = run_ddr_assessment(incident)

    gaps = incident.knownGaps if request.includeGaps else []

    metrics = {
        "timeToDetectMinutes": incident.detection.timeToDetectMinutes,
        "timeToDiagnoseMinutes": incident.diagnosis.timeToDiagnoseMinutes,
        "timeToRecoverMinutes": incident.recovery.timeToRecoverMinutes,
        "rollbackPerformed": incident.recovery.rollbackPerformed,
    }

    return PIRPack(
        incidentId=incident.incidentId,
        severity=incident.severity,
        executiveSummary=generate_executive_summary(incident, assessment),
        timeline=incident.timelineEvents,  # intentionally not auto-sorted
        rootCauseSection=generate_root_cause_section(incident),
        actions=incident.actionItems,
        metrics=metrics,
        gaps=gaps,
        suggestedImprovements=assessment.suggestedImprovements,
        readinessStatus=assessment.overallStatus,
    )


# ----------------------------
# FastAPI app + endpoints (thin)
# ----------------------------

app = FastAPI(
    title="PIR Automation API (Mock)",
    version="1.0.0",
    description="Backend API for DDR completeness validation and PIR pack generation (static mock dataset).",
)


@app.get("/v1/incidents/{incidentId}", response_model=IncidentRecord)
def get_incident(
    incidentId: str = Path(..., description="Incident identifier e.g., INC13089493", min_length=3, max_length=32)
) -> IncidentRecord:
    return get_incident_or_404(incidentId)


@app.get("/v1/incidents/{incidentId}/ddr-assess", response_model=DDRAssessmentResult)
def ddr_assess(
    incidentId: str = Path(..., description="Incident identifier e.g., INC13089493", min_length=3, max_length=32)
) -> DDRAssessmentResult:
    incident = get_incident_or_404(incidentId)
    return run_ddr_assessment(incident)


@app.post("/v1/incidents/{incidentId}/pir-pack", response_model=PIRPack)
def pir_pack(
    request: PIRPackRequest,
    incidentId: str = Path(..., description="Incident identifier e.g., INC13089493", min_length=3, max_length=32),
) -> PIRPack:
    incident = get_incident_or_404(incidentId)
    return generate_pir_pack(incident, request)


@app.get("/v1/rules/{severity}", response_model=RulesResponse)
def get_rules(severity: str) -> RulesResponse:
    # Requirement: return 404 for invalid severities (not 422),
    # so accept string and validate manually.
    sev = severity.strip().upper()
    rules = SEVERITY_RULES.get(sev)
    if rules is None:
        raise HTTPException(status_code=404, detail=f"Invalid severity '{severity}'. Use SEV1/SEV2/SEV3.")
    return RulesResponse(severity=sev, rules=rules)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}