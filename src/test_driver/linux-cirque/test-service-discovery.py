#!/usr/bin/env python3
"""
Copyright (c) 2021 Project CHIP Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
import os
import time
import sys

from helper.CHIPTestBase import CHIPVirtualHome

logger = logging.getLogger('CHIPInteractionModelTest')
logger.setLevel(logging.INFO)

sh = logging.StreamHandler()
sh.setFormatter(
    logging.Formatter(
        '%(asctime)s [%(name)s] %(levelname)s %(message)s'))
logger.addHandler(sh)

DEVICE_CONFIG = {
    'device0': {
        'type': 'MobileDevice',
        'base_image': 'chip_mobile_device',
        'capability': ['Interactive'],
        'rcp_mode': False,
    },
    'device1': {
        'type': 'CHIPEndDevice',
        'base_image': 'chip_server',
        'capability': ['Thread', 'Interactive'],
        'rcp_mode': True,
    },
    'device2': {
        'type': 'Border-Router',
        'base_image': 'border_router',
        'capability': ['Thread', 'Interactive'],
        'rcp_mode': True,
    }
}

CHIP_PORT = 11097

CIRQUE_URL = "http://localhost:5000"

TEST_EXTPANID = "fedcba9876543210"


class TestPythonController(CHIPVirtualHome):
    def __init__(self, device_config):
        super().__init__(CIRQUE_URL, device_config)
        self.logger = logger

    def setup(self):
        self.initialize_home()

    def test_routine(self):
        self.run_controller_test()

    def run_controller_test(self):
        ethernet_ip = [device['description']['ipv4_addr'] for device in self.non_ap_devices
                       if device['type'] == 'CHIPEndDevice'][0]
        br_id = [device['id'] for device in self.non_ap_devices
                  if device['type'] == 'Border-Router'][0]
        server_ids = [device['id'] for device in self.non_ap_devices
                      if device['type'] == 'CHIPEndDevice']
        req_id = [device['id'] for device in self.non_ap_devices
                   if device['type'] == 'MobileDevice'][0]

        self.reset_thread_devices(server_ids)
        self.assertTrue(self.wait_for_device_output(br_id, "Border router agent started.", 30))
        self.form_thread_network(device_id=br_id, expected_role='leader', timeout=15)

        command = "gdb -return-child-result -q -ex run -ex bt --args python3 /usr/bin/operational-discovery-srp-test.py -t 75 -a {}".format(
            ethernet_ip)
        ret = self.execute_device_cmd(req_id, command)
        self.assertEqual(ret['return_code'], '0',
                         "Test failed: non-zero return code")

        self.check_device_thread_state(server_ids[0],expected_role=['child', 'router'], timeout=2)


if __name__ == "__main__":
    sys.exit(TestPythonController(DEVICE_CONFIG).run_test())
