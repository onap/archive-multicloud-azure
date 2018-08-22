import mock
import unittest

from azure.pub.utils import syscomm

class SyscommTest(unittest.TestCase):


    def test_keystone_version(self):
        url = "http://a.com/test"
        version = "v3"
        expected = "http://a.com/test/v3"
        self.assertEquals(expected, syscomm.keystoneVersion(url,version))

    def test_verify_keystone(self):
        param = \
            {
                "auth": {
                    "tenantName": "12345",
                    "passwordCredentials" : {
                        "username" : "admin",
                        "password" : "password"
                    }
                }
            }
        self.assertEquals(True, syscomm.verifyKeystoneV2(param))
