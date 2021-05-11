import pytest
from napalm.base.exceptions import ConnectionException
from nornir.core.task import AggregatedResult

from nuts.base_tests.napalm_ping import CONTEXT
from tests.helpers.selftest_helpers import tupelize
from tests.base_tests.conftest import TIMEOUT_MESSAGE
from tests.helpers.selftest_helpers import create_result, create_multi_result, SelfTestData

ping_r1_1 = SelfTestData(
    nornir_raw_result={
        "success": {
            "probes_sent": 5,
            "packet_loss": 1,
            "rtt_min": 1.0,
            "rtt_max": 2.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": "172.16.23.3", "rtt": 0.0},
                {"ip_address": "172.16.23.3", "rtt": 0.0},
                {"ip_address": "172.16.23.3", "rtt": 0.0},
                {"ip_address": "172.16.23.3", "rtt": 0.0},
                {"ip_address": "172.16.23.3", "rtt": 0.0},
            ],
        }
    },
    test_data={"expected": "SUCCESS", "host": "R1", "destination": "172.16.23.3", "max_drop": 1},
)

ping_r1_2 = SelfTestData(
    nornir_raw_result={
        "success": {
            "probes_sent": 5,
            "packet_loss": 1,
            "rtt_min": 1.0,
            "rtt_max": 1.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": "172.16.23.5", "rtt": 0.0},
                {"ip_address": "172.16.23.5", "rtt": 0.0},
                {"ip_address": "172.16.23.5", "rtt": 0.0},
                {"ip_address": "172.16.23.5", "rtt": 0.0},
                {"ip_address": "172.16.23.5", "rtt": 0.0},
            ],
        }
    },
    test_data={"expected": "SUCCESS", "host": "R1", "destination": "172.16.23.6", "max_drop": 1},
)

ping_r2 = SelfTestData(
    nornir_raw_result={
        "success": {
            "probes_sent": 5,
            "packet_loss": 5,
            "rtt_min": 1.0,
            "rtt_max": 1.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": "172.16.23.4", "rtt": 0.0},
                {"ip_address": "172.16.23.4", "rtt": 0.0},
                {"ip_address": "172.16.23.4", "rtt": 0.0},
                {"ip_address": "172.16.23.4", "rtt": 0.0},
                {"ip_address": "172.16.23.4", "rtt": 0.0},
            ],
        }
    },
    test_data={"expected": "FAIL", "host": "R2", "destination": "172.16.23.4", "max_drop": 1},
)

ping_r3 = SelfTestData(
    nornir_raw_result={
        "success": {
            "probes_sent": 5,
            "packet_loss": 3,
            "rtt_min": 1.0,
            "rtt_max": 2.0,
            "rtt_avg": 1.0,
            "rtt_stddev": 0.0,
            "results": [
                {"ip_address": "172.16.23.6", "rtt": 0.0},
                {"ip_address": "172.16.23.6", "rtt": 0.0},
                {"ip_address": "172.16.23.6", "rtt": 0.0},
                {"ip_address": "172.16.23.6", "rtt": 0.0},
                {"ip_address": "172.16.23.6", "rtt": 0.0},
            ],
        }
    },
    test_data={"expected": "FLAPPING", "host": "R3", "destination": "172.16.23.5", "max_drop": 1},
)


@pytest.fixture
def general_result():
    task_name = "napalm_ping"
    confirmation_result = create_result(result_content="All pings executed", task_name="napalm_ping_multihost")
    timeouted = create_result(
        TIMEOUT_MESSAGE,
        task_name=task_name,
        host="R3",
        destination="172.16.23.6",
        failed=True,
        exception=ConnectionException("Cannot connect to 10.20.0.123"),
    )
    general_result = AggregatedResult(task_name)
    general_result["R1"] = create_multi_result(
        results=[
            confirmation_result,
            ping_r1_1.create_nornir_result(task_name),
            ping_r1_2.create_nornir_result(task_name),
        ],
        task_name=task_name,
    )
    general_result["R2"] = create_multi_result(
        results=[confirmation_result, ping_r2.create_nornir_result(task_name)], task_name=task_name
    )
    general_result["R3"] = create_multi_result(
        results=[confirmation_result, ping_r3.create_nornir_result(task_name), timeouted], task_name=task_name
    )
    return general_result

@pytest.fixture
def all_testdata():
    return [ping_r1_1.test_data, ping_r1_2.test_data, ping_r2.test_data, ping_r3.test_data]

pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT(nuts_parameters={"test_data": [ping_r1_1.test_data, ping_r1_2.test_data, ping_r2.test_data, ping_r3.test_data]}))]


class TestTransformResult:
    def test_contains_host_at_toplevel(self, transformed_result, all_testdata):
        hosts = [e["host"] for e in all_testdata]
        assert all(h in transformed_result for h in hosts)

    def test_contains_pinged_destination(self, transformed_result, all_testdata):
        assert all(entry["destination"] in transformed_result[entry["host"]] for entry in all_testdata)

    def test_destination_maps_to_enum_success(self, transformed_result):
        expected_success = ping_r1_1.test_data
        assert transformed_result["R1"][expected_success["destination"]].result.name == expected_success["expected"]

    def test_destination_maps_to_enum_failure(self, transformed_result):
        expected_fail = ping_r2.test_data
        assert transformed_result["R2"][expected_fail["destination"]].result.name == expected_fail["expected"]

    def test_destination_maps_to_enum_flapping(self, transformed_result):
        expected_flapping = ping_r3.test_data
        assert transformed_result["R3"][expected_flapping["destination"]].result.name == expected_flapping["expected"]

    def test_one_host_several_destinations(self, transformed_result):
        expected1 = ping_r1_1.test_data
        expected2 = ping_r1_2.test_data
        assert transformed_result["R1"][expected1["destination"]].result.name == expected1["expected"]
        assert transformed_result["R1"][expected2["destination"]].result.name == expected2["expected"]

    def test_marks_as_failed_if_task_failed(self, transformed_result):
        assert transformed_result["R3"]["172.16.23.6"].failed
        assert transformed_result["R3"]["172.16.23.6"].exception is not None
