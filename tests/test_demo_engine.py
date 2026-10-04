from __future__ import annotations

from hashlib import sha256

from pageready.agent import Action, AgentPolicy, QualityGateAgent
from pageready.demo import generate_demo_documents
from pageready.schemas import OverrideRequest, PageStatus, TraceEvent


def test_demo_documents_are_deterministic() -> None:
    first = generate_demo_documents()
    second = generate_demo_documents()
    assert [document.filename for document in first] == [document.filename for document in second]
    assert [sha256(document.image.tobytes()).hexdigest() for document in first] == [sha256(document.image.tobytes()).hexdigest() for document in second]


def test_demo_documents_follow_the_intended_policy_outcomes() -> None:
    agent = QualityGateAgent(policy=AgentPolicy(minimum_blur=45.0))
    outcomes = {document.filename: agent.process(document.image, document_id=document.filename)[1]["selected_action"] for document in generate_demo_documents()}
    assert outcomes == {
        "permit-register-clean.png": Action.APPROVE,
        "council-minutes-skewed.png": Action.APPROVE,
        "property-card-blurred.png": Action.REQUEST_RESCAN,
        "zoning-notice-low-contrast.png": Action.HUMAN_REVIEW,
    }


def test_trace_events_match_the_contract() -> None:
    trace = QualityGateAgent(policy=AgentPolicy(minimum_blur=45.0)).process(generate_demo_documents()[1].image)[1]
    events = [TraceEvent.model_validate(event) for event in trace["events"]]
    assert [event.event_type for event in events] == [
        "input_received",
        "runtime_provenance",
        "image_analyzed",
        "action_selected",
        "tool_invoked",
        "correction_verified",
        "outcome_resolved",
    ]
    assert events[1].detail["opencv_version"]
    assert all(event.actor == "system" for event in events)


def test_page_statuses_and_override_note_are_validated() -> None:
    assert len(PageStatus) == 7
    assert OverrideRequest(note="  Clerk confirmed source readability. ").note == "Clerk confirmed source readability."
    try:
        OverrideRequest(note="   ")
    except ValueError:
        pass
    else:
        raise AssertionError("Whitespace-only override note must be rejected.")
