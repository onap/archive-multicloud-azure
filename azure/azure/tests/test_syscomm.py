# Copyright (c) 2018 Amdocs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import unittest

from azure.pub.utils import syscomm


class SyscommTest(unittest.TestCase):

    def test_keystone_version(self):
        url = "http://a.com/test"
        version = "v3"
        expected = "http://a.com/test/v3"
        self.assertEquals(expected, syscomm.keystoneVersion(url, version))

    def test_verify_keystone(self):
        param = \
            {
                "auth": {
                    "tenantName": "12345",
                    "passwordCredentials": {
                        "username": "admin",
                        "password": "admin"
                    }
                }
            }
        self.assertEquals(True, syscomm.verifyKeystoneV2(param))
