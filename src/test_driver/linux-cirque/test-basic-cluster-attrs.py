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

logger = logging.getLogger('CHIPBasicClusterAttributesTest')
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
        'rcp_mode': True,
    },
    'device1': {
        'type': 'CHIPEndDevice',
        'base_image': 'chip_server',
        'capability': ['Thread', 'Interactive'],
        'rcp_mode': True,
    }
}

CHIP_PORT = 11097

CIRQUE_URL = "http://localhost:5000"

TEST_EXTPANID = "fedcba9876543210"


class TestBasicCluster(CHIPVirtualHome):
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
        server_ids = [device['id'] for device in self.non_ap_devices
                      if device['type'] == 'CHIPEndDevice']
        req_id = [device['id'] for device in self.non_ap_devices
                   if device['type'] == 'MobileDevice'][0]

        self.reset_thread_devices(server_ids)

        command = "gdb -return-child-result -q -ex run -ex bt --args python3 /usr/bin/basic-cluster-attributes-test.py -t 75 -a {}".format(
            ethernet_ip)
        ret = self.execute_device_cmd(req_id, command)
        self.assertEqual(ret['return_code'], '0',
                         "Test failed: non-zero return code")

        for device_id in server_ids:
            self.check_device_thread_state(device_id, expected_role=['leader'], timeout=2)

        # Verification of Basic Cluster response
        fmt = "CHIP:ZCL:   ClusterId: {cluster}\n" \
              "CHIP:ZCL:   attributeId: {attr}\n" \
              "CHIP:ZCL:   status: EMBER_ZCL_STATUS_SUCCESS (0x00)\n" \
              "CHIP:ZCL:   attributeType: {attr_type}\n" \
              "CHIP:ZCL:   value: {value}"

        # VendorName
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x0001',
                                   attr_type='0x42',
                                   value='TEST_VENDOR') in ret['output'])
        # VendorID
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x0002',
                                   attr_type='0x21',
                                   value='0x235a') in ret['output'])
        # ProductName
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x0003',
                                   attr_type='0x42',
                                   value='TEST_PRODUCT') in ret['output'])
        # ProductID
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x0004',
                                   attr_type='0x21',
                                   value='0xfeff') in ret['output'])
        # UserLabel
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x0005',
                                   attr_type='0x42',
                                   value='') in ret['output'])
        # Location
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x0006',
                                   attr_type='0x42',
                                   value='') in ret['output'])
        # HardwareVersion
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x0007',
                                   attr_type='0x21',
                                   value='0x0001') in ret['output'])
        # HardwareVersionString
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x0008',
                                   attr_type='0x42',
                                   value='TEST_VERSION') in ret['output'])
        # SoftwareVersion
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x0009',
                                   attr_type='0x23',
                                   value='0x00000001') in ret['output'])
        # SoftwareVersionString
        self.assertTrue(fmt.format(cluster='0x0028',
                                   attr='0x000a',
                                   attr_type='0x42',
                                   value='prerelease') in ret['output'])


if __name__ == "__main__":
    sys.exit(TestBasicCluster(DEVICE_CONFIG).run_test())
