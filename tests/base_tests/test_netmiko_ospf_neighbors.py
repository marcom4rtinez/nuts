import pytest
from nornir.core.task import AggregatedResult, MultiResult, Result

from nuts.base_tests.netmiko_ospf_neighbors import CONTEXT
from tests.helpers.selftest_helpers import create_multi_result, create_result, SelfTestData

NEIGHBOR_ID_1 = "172.16.255.1"
NEIGHBOR_ID_2 = "172.16.255.2"
NEIGHBOR_ID_3 = "172.16.255.3"
NEIGHBOR_ID_4 = "172.16.255.4"
NEIGHBOR_ID_11 = "172.16.255.11"

ADDRESS_1 = "172.16.12.1"
ADDRESS_1_2 = "172.16.211.11"
ADDRESS_2 = "172.16.12.2"
ADDRESS_3_1 = "172.16.13.3"
ADDRESS_3_2 = "172.16.23.3"
ADDRESS_4 = "172.16.14.4"

STATE_FULLDR = "FULL/DR"
STATE_FULLBDR = "FULL/BDR"

DEAD_TIME = "00:00:42"
PRIORITY = "1"


raw_nornir_result_r1 = [
    {
        "neighbor_id": NEIGHBOR_ID_3,
        "priority": PRIORITY,
        "state": STATE_FULLBDR,
        "dead_time": DEAD_TIME,
        "address": ADDRESS_3_1,
        "interface": "GigabitEthernet4",
    },
    {
        "neighbor_id": NEIGHBOR_ID_2,
        "priority": PRIORITY,
        "state": STATE_FULLBDR,
        "dead_time": DEAD_TIME,
        "address": ADDRESS_2,
        "interface": "GigabitEthernet3",
    },
    {
        "neighbor_id": NEIGHBOR_ID_4,
        "priority": PRIORITY,
        "state": STATE_FULLBDR,
        "dead_time": DEAD_TIME,
        "address": ADDRESS_4,
        "interface": "GigabitEthernet2",
    },
]


raw_nornir_result_r2 = [
    {
        "neighbor_id": NEIGHBOR_ID_3,
        "priority": PRIORITY,
        "state": STATE_FULLBDR,
        "dead_time": DEAD_TIME,
        "address": ADDRESS_3_2,
        "interface": "GigabitEthernet4",
    },
    {
        "neighbor_id": NEIGHBOR_ID_11,
        "priority": PRIORITY,
        "state": STATE_FULLBDR,
        "dead_time": DEAD_TIME,
        "address": ADDRESS_1_2,
        "interface": "GigabitEthernet3",
    },
    {
        "neighbor_id": NEIGHBOR_ID_1,
        "priority": PRIORITY,
        "state": STATE_FULLDR,
        "dead_time": DEAD_TIME,
        "address": ADDRESS_1,
        "interface": "GigabitEthernet2",
    },
]


ospf_r1_1 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R1",
        "local_port": "GigabitEthernet4",
        "neighbor_id": NEIGHBOR_ID_3,
        "state": STATE_FULLBDR,
        "neighbor_address": ADDRESS_3_1,
    },
)

ospf_r1_2 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R1",
        "local_port": "GigabitEthernet3",
        "neighbor_id": NEIGHBOR_ID_2,
        "state": STATE_FULLBDR,
        "neighbor_address": ADDRESS_2,
    },
)

ospf_r1_3 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r1,
    test_data={
        "host": "R1",
        "local_port": "GigabitEthernet2",
        "neighbor_id": NEIGHBOR_ID_4,
        "state": STATE_FULLBDR,
        "neighbor_address": ADDRESS_4,
    },
)

ospf_r2_1 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r2,
    test_data={
        "host": "R2",
        "local_port": "GigabitEthernet4",
        "neighbor_id": NEIGHBOR_ID_3,
        "state": STATE_FULLBDR,
        "neighbor_address": ADDRESS_3_2,
    },
)

ospf_r2_2 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r2,
    test_data={
        "host": "R2",
        "local_port": "GigabitEthernet3",
        "neighbor_id": NEIGHBOR_ID_11,
        "state": STATE_FULLBDR,
        "neighbor_address": ADDRESS_1_2,
    },
)


ospf_r2_3 = SelfTestData(
    nornir_raw_result=raw_nornir_result_r2,
    test_data={
        "host": "R2",
        "local_port": "GigabitEthernet2",
        "neighbor_id": NEIGHBOR_ID_1,
        "state": STATE_FULLDR,
        "neighbor_address": ADDRESS_1,
    },
)


@pytest.fixture
def general_result(timeouted_multiresult):
    task_name = "netmiko_send_command"
    result = AggregatedResult(task_name)
    result["R1"] = create_multi_result([create_result(raw_nornir_result_r1, task_name)], task_name)
    result["R2"] = create_multi_result([create_result(raw_nornir_result_r2, task_name)], task_name)
    result["R3"] = timeouted_multiresult
    return result


@pytest.fixture(
    params=[
        pytest.param(ospf_r1_1.test_data, id="ospf_r1_1"),
        pytest.param(ospf_r1_2.test_data, id="ospf_r1_2"),
        pytest.param(ospf_r1_3.test_data, id="ospf_r1_3"),
        pytest.param(ospf_r2_1.test_data, id="ospf_r2_1"),
        pytest.param(ospf_r2_2.test_data, id="ospf_r2_2"),
        pytest.param(ospf_r2_3.test_data, id="ospf_r2_3"),
    ]
)
def testdata(request):
    return request.param


pytestmark = [pytest.mark.nuts_test_ctx(CONTEXT())]


def test_contains_hosts_at_toplevel(transformed_result):
    assert transformed_result.keys() == {"R1", "R2", "R3"}


@pytest.mark.parametrize(
    "host, neighbors",
    [
        ("R1", {NEIGHBOR_ID_3, NEIGHBOR_ID_2, NEIGHBOR_ID_4}),
        ("R2", {NEIGHBOR_ID_3, NEIGHBOR_ID_11, NEIGHBOR_ID_1}),
    ],
)
def test_contains_neighbors_at_second_level(transformed_result, host, neighbors):
    assert transformed_result[host].result.keys() == neighbors


def test_contains_information_about_neighbor(transformed_result, testdata):
    print(testdata)
    neighbor_details = transformed_result[testdata["host"]].result[testdata["neighbor_id"]]
    expected = {
        "neighbor_id": testdata["neighbor_id"],
        "priority": PRIORITY,
        "state": testdata["state"],
        "dead_time": DEAD_TIME,
        "address": testdata["neighbor_address"],
        "interface": testdata["local_port"],
    }
    assert neighbor_details == expected


def test_marks_as_failed_if_task_failed(transformed_result):
    assert transformed_result["R3"].failed
    assert transformed_result["R3"].exception is not None
