"""Kill-switch behavior tests."""

from mas.protocols.kill_switch import get_kill_switch_reason, should_trigger_kill_switch


def test_kill_switch_triggers_on_overheat() -> None:
    class DummyModel:
        def __init__(self):
            self.system_shutdown = False
            self.unsafe_temp_threshold = 80.0
            self.max_failed_agents_before_shutdown = 2
            self.failed_agents = []
            self.zone_temperatures = {0: 81.0, 1: 50.0}

    model = DummyModel()
    assert should_trigger_kill_switch(model) is True
    assert get_kill_switch_reason(model) == "overheat"


def test_kill_switch_reason_includes_failure_limit() -> None:
    class DummyModel:
        def __init__(self):
            self.system_shutdown = False
            self.unsafe_temp_threshold = 80.0
            self.max_failed_agents_before_shutdown = 1
            self.zone_temperatures = {0: 81.0, 1: 81.0}
            # One failed agent triggers combined rule when overheated.
            self.failed_agents = [object()]

    model = DummyModel()
    assert should_trigger_kill_switch(model) is True
    assert get_kill_switch_reason(model) == "overheat_and_failure_limit"
