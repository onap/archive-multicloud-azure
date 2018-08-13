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

import json
import mock
import unittest

from azure.pub.exceptions import VimDriverAzureException
from azure.pub.utils import restcall


class TestAAIClient(unittest.TestCase):

    def setUp(self):
        self.view = restcall.AAIClient("vmware", "4.0")

    @mock.patch.object(restcall, "call_req")
    def test_get_vim(self, mock_call):
        mock_call.return_value = [0, '{"cloudOwner": "vmware"}']
        ret = self.view.get_vim(get_all=True)
        expect_ret = {"cloudOwner": "vmware"}
        self.assertEqual(expect_ret, ret)

    @mock.patch.object(restcall.AAIClient, "get_vim")
    @mock.patch.object(restcall, "call_req")
    def test_update_identity_url(self, mock_call, mock_getvim):
        mock_getvim.return_value = {}
        self.view.update_identity_url()
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_add_tenants(self, mock_call):
        tenants = {"tenants": [{"name": "admin", "id": "admin-id"}]}
        self.view.add_tenants(tenants)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_add_flavors(self, mock_call):
        flavors = {
            "flavors": [{
                "name": "m1.small",
                "id": "1",
                "vcpus": 1,
                "ram": 512,
                "disk": 10,
                "ephemeral": 0,
                "swap": 0,
                "is_public": True,
                "links": [{"href": "http://fake-url"}],
                "is_disabled": False
            }]
        }
        self.view.add_flavors(flavors)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_add_flavors_with_hpa(self, mock_call):
        flavors = {
            "flavors": [{
                "name": "onap.small",
                "id": "1",
                "vcpus": 1,
                "ram": 512,
                "disk": 10,
                "ephemeral": 0,
                "swap": 0,
                "is_public": True,
                "links": [{"href": "http://fake-url"}],
                "is_disabled": False,
                "extra_specs": {},
            }]
        }
        self.view._get_ovsdpdk_capabilities = mock.MagicMock()
        self.view._get_ovsdpdk_capabilities.return_value = {}
        self.view.add_flavors(flavors)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_add_images(self, mock_call):
        images = {
            "images": [{
                "name": "ubuntu-16.04",
                "id": "image-id"
            }]
        }
        self.view.add_images(images)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_add_networks(self, mock_call):
        networks = {
            "networks": [{
                "name": "net-1",
                "id": "net-id",
                "segmentationId": 144
            }]
        }
        self.view.add_networks(networks)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_add_pservers(self, mock_call):
        pservers = {
            "hypervisors": [{
                "name": "compute-1",
                "vcpus": 100,
                "local_disk_size": 1000,
                "memory_size": 10240,
                "host_ip": "10.0.0.7",
                "id": "compute-1-id"
            }]
        }
        self.view.add_pservers(pservers)
        self.assertEqual(mock_call.call_count, 2)

    @mock.patch.object(restcall, "call_req")
    def test_del_tenants(self, mock_call):
        mock_call.return_value = [0]
        rsp = {
            "tenants": {
                "tenant": [{
                    "tenant-id": "tenant-id",
                    "resource-version": "version-1"
                }]
            }
        }
        self.view._del_tenants(rsp)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_del_flavors(self, mock_call):
        mock_call.return_value = [0]
        rsp = {
            "flavors": {
                "flavor": [{
                    "flavor-id": "fake-id",
                    "resource-version": "fake-version"
                }]
            }
        }
        self.view._del_flavors(rsp)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_del_images(self, mock_call):
        mock_call.return_value = [0]
        rsp = {
            "images": {
                "image": [{
                    "image-id": "fake-id",
                    "resource-version": "fake-version"
                }]
            }
        }
        self.view._del_images(rsp)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_del_networks(self, mock_call):
        mock_call.return_value = [0]
        rsp = {
            "oam-networks": {
                "oam-network": [{
                    "network-uuid": "fake-id",
                    "resource-version": "fake-version"
                }]
            }
        }
        self.view._del_networks(rsp)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_del_azs(self, mock_call):
        mock_call.return_value = [0]
        rsp = {
            "availability-zones": {
                "availability-zone": [{
                    "availability-zone-name": "fake-name",
                    "resource-version": "fake-version"
                }]
            }
        }
        self.view._del_azs(rsp)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_del_hpa(self, mock_call):
        mock_call.return_value = [0]
        rsp = {
            "flavor-id": "id1",
            "hpa-capabilities": {
                "hpa-capability": [{
                    "resource-version": "v1",
                    "hpa-capability-id": "id2"
                }]
            }
        }
        self.view._del_hpa(rsp)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_del_vim(self, mock_call):
        resp = {
            "resource-version": "1"
        }
        self.view.get_vim = mock.MagicMock()
        self.view.get_vim.return_value = resp
        mock_call.return_value = [0, "", "", ""]
        self.view.delete_vim()
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_del_vim_fail(self, mock_call):
        resp = {
            "resource-version": "1"
        }
        self.view.get_vim = mock.MagicMock()
        self.view.get_vim.return_value = resp
        mock_call.return_value = [1, "", "", ""]
        self.assertRaises(VimDriverAzureException, self.view.delete_vim)

    @mock.patch.object(restcall, "call_req")
    def test_update_vim(self, mock_call):
        resp = {
            "resource-version": "1"
        }
        self.view.get_vim = mock.MagicMock()
        self.view.get_vim.return_value = resp
        content = {
            "tenants": [],
            "images": [],
            "flavors": [],
            "networks": [],
            "hypervisors": []
        }
        self.view.update_vim(content)
        mock_call.assert_called_once()

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa(self, mock_call):
        self.view._get_hpa_basic_capabilities = mock.MagicMock()
        self.view._get_hpa_basic_capabilities.return_value = {"hpa": "basic"}
        self.view._get_cpupinning_capabilities = mock.MagicMock()
        self.view._get_cpupinning_capabilities.return_value = {"hpa": "basic"}
        self.view._get_cputopology_capabilities = mock.MagicMock()
        self.view._get_cputopology_capabilities.return_value = {"hpa": "basic"}
        self.view._get_hugepages_capabilities = mock.MagicMock()
        self.view._get_hugepages_capabilities.return_value = {"hpa": "basic"}
        self.view._get_numa_capabilities = mock.MagicMock()
        self.view._get_numa_capabilities.return_value = {"hpa": "basic"}
        self.view._get_storage_capabilities = mock.MagicMock()
        self.view._get_storage_capabilities.return_value = {"hpa": "basic"}
        self.view._get_instruction_set_capabilities = mock.MagicMock()
        self.view._get_instruction_set_capabilities.return_value = {
            "hpa": "basic"}
        self.view._get_pci_passthrough_capabilities = mock.MagicMock()
        self.view._get_pci_passthrough_capabilities.return_value = {
            "hpa": "basic"}
        self.view._get_ovsdpdk_capabilities = mock.MagicMock()
        self.view._get_ovsdpdk_capabilities.return_value = {"hpa": "basic"}
        ret = self.view._get_hpa_capabilities({"extra_specs": {}})
        self.assertEqual([{"hpa": "basic"}]*9, ret)

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_basic(self, mock_call):
        flavor = {
            "vcpus": 1,
            "ram": 1024
        }
        ret = self.view._get_hpa_basic_capabilities(flavor)
        self.assertEqual(len(ret["hpa-feature-attributes"]), 2)

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_cpupin(self, mock_call):
        extra = {
            "hw:cpu_policy": "cpu_policy",
            "hw:cpu_thread_policy": "thread_policy"
        }
        ret = self.view._get_cpupinning_capabilities(extra)
        self.assertEqual(len(ret["hpa-feature-attributes"]), 2)

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_cputopo(self, mock_call):
        extra = {
            "hw:cpu_sockets": 2,
            "hw:cpu_cores": 2,
            "hw:cpu_threads": 4
        }
        ret = self.view._get_cputopology_capabilities(extra)
        self.assertEqual(len(ret["hpa-feature-attributes"]), 3)

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_hugepage_large(self, mock_call):
        extra = {
            "hw:mem_page_size": "large"
        }
        ret = self.view._get_hugepages_capabilities(extra)
        self.assertIn(
            "2", ret["hpa-feature-attributes"][0]["hpa-attribute-value"])

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_hugepage_small(self, mock_call):
        extra = {
            "hw:mem_page_size": "small"
        }
        ret = self.view._get_hugepages_capabilities(extra)
        self.assertIn(
            "4", ret["hpa-feature-attributes"][0]["hpa-attribute-value"])

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_hugepage_int(self, mock_call):
        extra = {
            "hw:mem_page_size": 8,
        }
        ret = self.view._get_hugepages_capabilities(extra)
        self.assertIn(
            "8", ret["hpa-feature-attributes"][0]["hpa-attribute-value"])

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_hugepage_any(self, mock_call):
        extra = {
            "hw:mem_page_size": "any",
        }
        ret = self.view._get_hugepages_capabilities(extra)
        self.assertEqual(0, len(ret["hpa-feature-attributes"]))

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_numa(self, mock_call):
        extra = {
            "hw:numa_nodes": 1,
            "hw:numa_cpus.0": 1,
            "hw:numa_mem.0": 1024,
        }
        ret = self.view._get_numa_capabilities(extra)
        self.assertEqual(3, len(ret["hpa-feature-attributes"]))

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_storage(self, mock_call):
        extra = {
            "disk": 10,
        }
        ret = self.view._get_storage_capabilities(extra)
        self.assertEqual(3, len(ret["hpa-feature-attributes"]))

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_instru(self, mock_call):
        extra = {
            "hw:capabilities:cpu_info:features": "avx",
        }
        ret = self.view._get_instruction_set_capabilities(extra)
        self.assertEqual(1, len(ret["hpa-feature-attributes"]))

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_pci(self, mock_call):
        extra = {
            "pci_passthrough:alias": "gpu-nvidia-x86-0011-0022:1",
        }
        ret = self.view._get_pci_passthrough_capabilities(extra)
        self.assertEqual(3, len(ret["hpa-feature-attributes"]))

    @mock.patch.object(restcall, "call_req")
    def test_get_hpa_dpdk(self, mock_call):
        self.view.get_vim = mock.MagicMock()
        self.view.get_vim.return_value = {
            "cloud-extra-info": json.dumps({'ovsDpdk': {
                'libname': 'generic', 'libversion': '17.04'}})
        }
        ret = self.view._get_ovsdpdk_capabilities()
        self.assertEqual(1, len(ret["hpa-feature-attributes"]))
