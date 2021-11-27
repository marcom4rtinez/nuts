"""Query CDP neighbors of a device."""
from typing import Callable, Dict, Any

import pytest
from nornir.core.filter import F
from nornir.core.task import MultiResult, Result
from nornir_netmiko import netmiko_send_command

from nuts.helpers.filters import filter_hosts
from nuts.helpers.result import AbstractHostResultExtractor
from nuts.context import NornirNutsContext


class NetmikoVlansExtractor(AbstractHostResultExtractor):
    def single_transform(self, single_result: MultiResult) -> Dict[int, Any]:
        result = {}
        for vlan in self._simple_extract(single_result):
            result[int(vlan["vlan_id"])] = {"name": vlan["name"], "interfaces": vlan["interfaces"]}
        return result


class NetmikoVlansContext(NornirNutsContext):
    def nuts_task(self) -> Callable[..., Result]:
        return netmiko_send_command

    def nuts_arguments(self) -> Dict[str, Any]:
        return {"command_string": "show vlan", "use_textfsm": True}

    def nornir_filter(self) -> F:
        return filter_hosts(self.nuts_parameters["test_data"])

    def nuts_extractor(self) -> NetmikoVlansExtractor:
        return NetmikoVlansExtractor(self)


CONTEXT = NetmikoVlansContext


class TestNetmikoVlans:
    @pytest.mark.nuts("vlan_tag")
    def test_vlan_tag(self, single_result, vlan_tag):
        assert vlan_tag in single_result.result

    @pytest.mark.nuts("vlan_name,vlan_tag")
    def test_vlan_name_to_tag(self, single_result, vlan_name, vlan_tag):
        assert single_result.result[vlan_tag]["name"] == vlan_name


class TestNetmikoOnlyDefinedVlansExist:
    @pytest.mark.nuts("vlan_tags")
    def test_no_rogue_vlans(self, single_result, vlan_tags):
        assert list(single_result.result.keys()) == sorted(vlan_tags)
