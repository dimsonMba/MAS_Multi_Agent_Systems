"""Kill-switch behavior test."""

from mas.protocols.kill_switch import evaluate_kill_switch


def test_kill_switch_stops_running_model() -> None:
    class DummyEnvironment:
        hazard_flag = True

    class DummyModel:
        environment = DummyEnvironment()
        running = True

    model = DummyModel()
    evaluate_kill_switch(model)
    assert model.running is False
