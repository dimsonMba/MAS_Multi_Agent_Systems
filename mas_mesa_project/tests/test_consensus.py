"""Consensus protocol smoke tests."""

from mas.protocols.consensus import vote_on_failure


def test_vote_on_failure_returns_boolean() -> None:
    result = vote_on_failure(voter_id=1, suspect_id=2, evidence={"heartbeat_missed": 3})
    assert isinstance(result, bool)
