Test Bundles
============

A test bundle contains one ore more tests that are logically related to each other. For example, a test bundle about BGP neighbors has a test that checks the correctness of the local ID, another test checks if a peer is up etc. These tests are defined by the individual fields for each entry in ``test_data``. If all fields are present, all tests are executed. If the field is missing, the test will be shown as "skipped" in the results. In the example on BGP neighbors below, ``R2`` only has a test that checks if its neighbor is down (``is_up: false``). 

This section contains all test bundles which have been implemented in NUTS, you can incorporate them in your own bundles. They can be executed with the command ``$ pytest <test bundle name>.yaml`` from your project root. 

Note that you need an inventory of network devices for the tests to work. Please see :doc:`First Steps with NUTS <../tutorial/firststeps>` for more information.

In some test bundles you can directly pass arguments to the nornir task, i.e. the network query that is executed in the background. For those test bundles we indicate the specific task which is used to query the devices, so that you can look up all available arguments. 


BGP Neighbors - Information
---------------------------

**Test Bundle:** Tests if pre-defined BGP neighbors exist on a host.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNapalmBgpNeighbors
      test_data:
        - host: <host name, required>
          local_id: <ID>
          local_as: <AS number>
          peer: <IP address, required>
          remote_as: <AS number>
          remote_id: <remote ID>
          is_enabled: <true|false>
          is_up: <true|false>

Required fields for specific tests in this bundle:

    * Test the local AS: ``host, peer, local_as`` 
    * Test the local ID: ``host, peer, local_id``
    * Test remote AS: ``host, peer, remote_as``
    * Test remote ID: ``host, peer, remote_id``
    * Test if the peer is enabled: ``host, peer, is_enabled``
    * Test if the peer is up: ``host, peer, is_up``

**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNapalmBgpNeighbors
      test_data:
        - host: R1
          local_id: 172.16.255.1
          local_as: 45001
          peer: 172.16.255.2
          remote_as: 45002
          remote_id: 0.0.0.0
          is_enabled: true
          is_up: false
        - host: R2
          peer: 172.16.255.2
          is_up: false      


BGP Neighbors - Count
---------------------

**Test Bundle:** Tests the amount of BGP neighbors a host should have.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNapalmBgpNeighborsCount
      test_data:
        - host: <host name, required>
          neighbor_count: <number of neighbors, required>


**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNapalmBgpNeighborsCount
      test_data:
        - host: R1
          neighbor_count: 2
        - host: R2
          neighbor_count: 1


CDP Neighbors
-------------

**Test Bundle:** Tests if pre-defined CDP neighbors exist on a host.

**Note**: `ntc-templates <https://github.com/networktocode/ntc-templates>`__ must be pre-installed.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNetmikoCdpNeighbors
      test_data:
        - host: <host name, required>
          local_port: <name of the local interface>
          remote_host: <host name, required>
          management_ip: <IP address>
          remote_port: <name of the remote interface>

Required fields for specific tests in this bundle:

    * Test remote_host host: ``host, remote_host`` 
    * Test local port: ``host, remote_host, local_port``
    * Test remote port: ``host, remote_host, remote_port``
    * Test management IP: ``host, remote_host, management_ip``

**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNetmikoCdpNeighbors
      test_data:
        - host: R1
          local_port: GigabitEthernet3
          remote_host: R2
          management_ip: 172.16.12.2
          remote_port: GigabitEthernet2


Interfaces
--------------

**Test Bundle:** Tests if an interface exists on a host and has the required attributes.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNapalmInterfaces
      test_data:
        - host: <host name, required>
          name: <name of the interface, required>
          is_enabled: <true|false>
          is_up: <true|false>
          mac_address: <MAC address>
          mtu: <int value>
          speed: <int value>

Required fields for specific tests in this bundle:

    * Test if interface is enabled: ``host, name, is_enabled``
    * Test if interface is up: ``host, name, is_up`` 
    * Test MAC address of interface: ``host, name, mac_address``
    * Test MTU: ``host, name, mtu``
    * Test speed: ``host, name, speed`` 

**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNapalmInterfaces
        test_data:
        - host: R1
          name: GigabitEthernet1
          is_enabled: true
          is_up: true
          mac_address: C0:FF:EE:BE:EF:00
          mtu: 1500
          speed: 1000

iperf - Bandwidth Test
----------------------

.. attention::

  Nornir parallelizes tasks, and this test bundle uses iperf3 to determine the bandwidth. This generates a conflict: A destination may be blocked for Host A because a parallel task for Host B is already connected to the same destination. In this case, task execution fails. The `pull request for iperf3 <https://github.com/esnet/iperf/pull/1074>`__ is still open which should allow parallel connections from one server to several clients. Until this is merged and released, please see the requirements below for solutions.

**Requirements**: 
 
  * Linux hosts required with ``iperf3`` installed.
  * Run nornir with one thread only:
  * Adjust your nornir configuration for this test bundle only: in ``nr-config.yaml`` set ``num_workers: 1``.

**Test Bundle:** Tests if a connection between two hosts achieves a certain minimum bandwidth.

**Test Bundle Structure:**

.. code:: yaml

  - test_class: TestNetmikoIperf
    test_data:
      - host: <host name, required>
        destination: <IP address>
        min_expected: <bits per second>

**Test Bundle Example:**

.. code:: yaml

  - test_class: TestNetmikoIperf
    test_data:
      - host: L1
        destination: 10.20.2.12
        min_expected: 10000000

LLDP Neighbors
--------------

**Test Bundle:** Tests if pre-defined LLDP neighbors exist on a host.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNapalmLldpNeighbors
      test_data:
        - host: <host name, required>
          local_port: <name of the local interface, required>
          remote_host: <host name>
          remote_port: <name of the remote interface>

Required fields for specific tests in this bundle:

    * Test remote host: ``host, local_port, remote_host``
    * Test remote port: ``host, local_port, remote_port`` 

**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNapalmLldpNeighbors
      test_data:
        - host: R1
          local_port: GigabitEthernet3
          remote_host: R2
          remote_port: GigabitEthernet2


Network Instances
-----------------

**Test Bundle:**  Tests if pre-defined network instances (VRFs) exist.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNapalmNetworkInstances
      test_data:
        - host: <host name, required>
          network_instance: <VRF name, required>
          interfaces:
            - <interface name>
          route_distinguisher: "<number>:<number>"

Required fields for specific tests in this bundle:

    * Test interfaces that belong to a VRF: ``host, network_instance, interfaces``
    * Test route-distinguisher: ``host, network_instance, route_distinguisher``  


**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNapalmNetworkInstances
      test_data:
        - host: R1
          network_instance: test1
          interfaces:
            - GigabitEthernet2
            - GigabitEthernet3
            - Loopback0
          route_distinguisher: "1:1"

OSPF Neighbors - Information
----------------------------

**Test Bundle:** Tests if pre-defined OSPF neighbors exist on a host.

**Note**: `ntc-templates <https://github.com/networktocode/ntc-templates>`__ must be pre-installed.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNetmikoOspfNeighbors
      test_data:
        - host: <host name, required>
          local_port: <name of the local interface>
          neighbor_id: <ID>
          state: <FULL/BDR|FULL/DR>
          neighbor_address: <IP address>

Required fields for specific tests in this bundle:

    * Test local port: ``host, local_port, neighbor_id``
    * Test neighbor ID: ``host, neighbor_id``
    * Test state: ``host, neighbor_id, state``
    * Test neighbor address: ``host, neighbor_id, neighbor_address``


**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNetmikoOspfNeighbors
      test_data:
        - host: R1
          local_port: GigabitEthernet2
          neighbor_id: 172.16.255.4
          state: FULL/BDR
          neighbor_address: 172.16.14.4


OSPF Neighbors - Count
----------------------------

**Test Bundle:** Tests the amount of OSPF neighbors a host should have.

**Note**: `ntc-templates <https://github.com/networktocode/ntc-templates>`__ must be pre-installed.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNetmikoOspfNeighborsCount
      test_data:
        - host: <host name, required>
          neighbor_count: <number of neighbors, required>

**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNetmikoOspfNeighbors
      test_data:
        - host: R1
          neighbor_count: 3


Ping Hosts
----------

**Test Bundle:** Tests if a host can ping another.

**Note**: Linux host required with Ping installed.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNapalmPing
      test_execution: 
        ttl: <number, optional>
        timeout: <number, optional>
        size: <number, optional>
        count: <number, optional>
        vrf: <string, optional>
      test_data:
        - host: <host name, required>
          destination: <IP Address>
          expected: <SUCCESS|FAIL|FLAPPING>
          max_drop: <number>

There is only one test in this bundle, i.e. ping another host. All fields are therefore required: ``host, destination, expected, max_drop``. 

``max_drop``:  Defines how many ping attemps are allowed to fail to still be counted as ``SUCCESS``. ``FAIL`` means every packet was lost. ``FLAPPING`` is everything else in-between.

``test_execution``: These fields directly control how the ping is executed. Their values are passed on to nornir, which executes the actual network requests in the background. `Nornir uses napalm's ping <https://github.com/nornir-automation/nornir_napalm/blob/master/nornir_napalm/plugins/tasks/napalm_ping.py>`__, which supports the following fields:

    * ``ttl``: Max number of hops, optional.
    * ``timeout``: Max seconds to wait after sending final packet, optional.
    * ``size``: Size of request in bytes.
    * ``count``: Number of ping request to send.
    * ``vrf``: Name of VRF.


**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNapalmPing
      test_execution:
        count: 5
        ttl: 10
      test_data:
        - host: R1
          destination: 172.16.23.3
          expected: SUCCESS
          max_drop: 1


Users - Information
-------------------


**Test Bundle:** Tests pre-defined users of a device.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNapalmUsers
      test_data:
        - host: <host name, required>
          username: <name>
          password: <password>
          level: <1...15>          

Required fields for specific tests in this bundle:

    * Test username: ``host, username``
    * Test password: ``host, username, password`` 
    * Test privilege level: ``host, username, level`` 

**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNapalmUsers
      test_data:
        - host: R1
          username: arya
          password: stark
          level: 15

Users - No Rogue Users
----------------------

**Test Bundle:** Tests if only pre-defined users exist on a device, i.e. that there are no rogue users.

**Test Bundle Structure:**

.. code:: yaml

    - test_class: TestNapalmOnlyDefinedUsersExist
      test_data:
        - host: <host name, required>
          usernames: <list of usernames, required>
            - <username>

**Test Bundle Example:**

.. code:: yaml

    - test_class: TestNapalmOnlyDefinedUsersExist
      test_data:
        - host: R1
          usernames:
            - cisco
            - arya
