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

import sys
import traceback
import logging
import urllib2
import uuid
import httplib2
import json

from multicloud_azure.pub.config.config import AAI_SCHEMA_VERSION
from multicloud_azure.pub.config.config import AAI_SERVICE_URL
from multicloud_azure.pub.config.config import AAI_USERNAME
from multicloud_azure.pub.config.config import AAI_PASSWORD
from multicloud_azure.pub.config.config import MSB_SERVICE_IP, MSB_SERVICE_PORT

from multicloud_azure.pub.exceptions import VimDriverAzureException

rest_no_auth, rest_oneway_auth, rest_bothway_auth = 0, 1, 2
HTTP_200_OK, HTTP_201_CREATED = '200', '201'
HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED = '204', '202'
status_ok_list = [HTTP_200_OK, HTTP_201_CREATED,
                  HTTP_204_NO_CONTENT, HTTP_202_ACCEPTED]
HTTP_404_NOTFOUND, HTTP_403_FORBIDDEN = '404', '403'
HTTP_401_UNAUTHORIZED, HTTP_400_BADREQUEST = '401', '400'

logger = logging.getLogger(__name__)


def call_req(base_url, user, passwd, auth_type, resource, method, content='',
             headers=None):
    callid = str(uuid.uuid1())
#    logger.debug("[%s]call_req('%s','%s','%s',%s,'%s','%s','%s')" % (
#        callid, base_url, user, passwd, auth_type, resource, method, content))
    ret = None
    resp_status = ''
    resp = ""
    full_url = ""

    try:
        full_url = combine_url(base_url, resource)
        if headers is None:
            headers = {}
            headers['content-type'] = 'application/json'

        if user:
            headers['Authorization'] = 'Basic ' + \
                ('%s:%s' % (user, passwd)).encode("base64")
        ca_certs = None
        for retry_times in range(3):
            http = httplib2.Http(
                ca_certs=ca_certs,
                disable_ssl_certificate_validation=(
                    auth_type == rest_no_auth))
            http.follow_all_redirects = True
            try:
                logger.debug("request=%s" % full_url)
                resp, resp_content = http.request(
                    full_url, method=method.upper(), body=content,
                    headers=headers)
                resp_status = resp['status']
                resp_body = resp_content.decode('UTF-8')

                if resp_status in status_ok_list:
                    ret = [0, resp_body, resp_status, resp]
                else:
                    ret = [1, resp_body, resp_status, resp]
                break
            except Exception as ex:
                if 'httplib.ResponseNotReady' in str(sys.exc_info()):
                    logger.error(traceback.format_exc())
                    ret = [1, "Unable to connect to %s" % full_url,
                           resp_status, resp]
                    continue
                raise ex
    except urllib2.URLError as err:
        ret = [2, str(err), resp_status, resp]
    except Exception as ex:
        logger.error(traceback.format_exc())
        logger.error("[%s]ret=%s" % (callid, str(sys.exc_info())))
        res_info = str(sys.exc_info())
        if 'httplib.ResponseNotReady' in res_info:
            res_info = ("The URL[%s] request failed or is not responding." %
                        full_url)
        ret = [3, res_info, resp_status, resp]
#    logger.debug("[%s]ret=%s" % (callid, str(ret)))
    return ret


def req_by_msb(resource, method, content=''):
    base_url = "http://%s:%s/" % (MSB_SERVICE_IP, MSB_SERVICE_PORT)
    return call_req(base_url, "", "", rest_no_auth, resource, method, content)


def combine_url(base_url, resource):
    full_url = None
    if base_url.endswith('/') and resource.startswith('/'):
        full_url = base_url[:-1] + resource
    elif base_url.endswith('/') and not resource.startswith('/'):
        full_url = base_url + resource
    elif not base_url.endswith('/') and resource.startswith('/'):
        full_url = base_url + resource
    else:
        full_url = base_url + '/' + resource
    return full_url


def get_res_from_aai(resource, content=''):
    headers = {
        'X-FromAppId': 'MultiCloud',
        'X-TransactionId': '9001',
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    base_url = "%s/%s" % (AAI_SERVICE_URL, AAI_SCHEMA_VERSION)
    return call_req(base_url, AAI_USERNAME, AAI_PASSWORD, rest_no_auth,
                    resource, "GET", content, headers)


class AAIClient(object):
    def __init__(self, cloud_owner, cloud_region):
        self.base_url = "%s/%s" % (AAI_SERVICE_URL, AAI_SCHEMA_VERSION)
        self.username = AAI_USERNAME
        self.password = AAI_PASSWORD
        self.default_headers = {
            'X-FromAppId': 'multicloud-azure',
            'X-TransactionId': '9004',
            'content-type': 'application/json',
            'accept': 'application/json'
        }
        self.cloud_owner = cloud_owner
        self.cloud_region = cloud_region
        self._vim_info = None

    def get_vim(self, get_all=False):
        resource = ("/cloud-infrastructure/cloud-regions/cloud-region"
                    "/%s/%s" % (self.cloud_owner, self.cloud_region))
        if get_all:
            resource = "%s?depth=all" % resource
        resp = call_req(self.base_url, self.username, self.password,
                        rest_no_auth, resource, "GET",
                        headers=self.default_headers)
        if resp[0] != 0:
            raise VimDriverAzureException(
                status_code=404,
                content="Failed to query VIM with id (%s_%s) from extsys." % (
                    self.cloud_owner, self.cloud_region))
        return json.loads(resp[1])

    def delete_vim(self):
        resp = self.get_vim(get_all=True)
        logger.debug('Delete cloud region')
        resource = ("/cloud-infrastructure/cloud-regions/cloud-region"
                    "/%s/%s?resource-version=%s" %
                    (self.cloud_owner, self.cloud_region,
                     resp['resource-version']))
        resp = call_req(self.base_url, self.username, self.password,
                        rest_no_auth, resource, "DELETE",
                        headers=self.default_headers)
        if resp[0] != 0:
            raise VimDriverAzureException(
                status_code=400,
                content="Failed to delete cloud %s_%s: %s." % (
                    self.cloud_owner, self.cloud_region, resp[1]))

    def update_vim(self, content):
        self.add_flavors(content)

    def update_identity_url(self):
        vim = self.get_vim()
        vim['identity-url'] = ("http://%s/api/multicloud/v0/%s_%s/identity/"
                               "v3" % (MSB_SERVICE_IP, self.cloud_owner,
                                       self.cloud_region))
        resource = ("/cloud-infrastructure/cloud-regions/cloud-region"
                    "/%s/%s" % (self.cloud_owner, self.cloud_region))
        logger.debug("Updating identity url %s" % vim)
        call_req(self.base_url, self.username, self.password,
                 rest_no_auth, resource, "PUT",
                 content=json.dumps(vim),
                 headers=self.default_headers)

    def add_flavors(self, content):
        for flavor in content['flavors']:
            resource = ("/cloud-infrastructure/cloud-regions/cloud-region/"
                        "%s/%s/flavors/flavor/%s" % (
                            self.cloud_owner, self.cloud_region,
                            flavor['name']))
            body = {
                'flavor-name': flavor['name'],
                'flavor-vcpus': flavor['vcpus'],
                'flavor-ram': flavor['ram'],
                'flavor-disk': flavor['disk'],
                'flavor-selflink': ""
            }
            # Handle extra specs
            if flavor['name'].startswith("onap."):
                hpa_capabilities = self._get_hpa_capabilities(
                    flavor)
                body['hpa-capabilities'] = {
                    'hpa-capability': hpa_capabilities}

            logger.debug("Adding flavors to cloud region")
            call_req(self.base_url, self.username, self.password,
                     rest_no_auth, resource, "PUT",
                     content=json.dumps(body),
                     headers=self.default_headers)

    def _get_hpa_capabilities(self, flavor):
        hpa_caps = []

        # Basic capabilties
        caps_dict = self._get_hpa_basic_capabilities(flavor)
        if len(caps_dict) > 0:
            logger.debug("basic_capabilities_info: %s" % caps_dict)
            hpa_caps.append(caps_dict)

        # cpupining capabilities
        caps_dict = self._get_cpupinning_capabilities(flavor['extra_specs'])
        if len(caps_dict) > 0:
            logger.debug("cpupining_capabilities_info: %s" % caps_dict)
            hpa_caps.append(caps_dict)

        # cputopology capabilities
        caps_dict = self._get_cputopology_capabilities(flavor['extra_specs'])
        if len(caps_dict) > 0:
            logger.debug("cputopology_capabilities_info: %s" % caps_dict)
            hpa_caps.append(caps_dict)

        # hugepages capabilities
        caps_dict = self._get_hugepages_capabilities(flavor['extra_specs'])
        if len(caps_dict) > 0:
            logger.debug("hugepages_capabilities_info: %s" % caps_dict)
            hpa_caps.append(caps_dict)

        # numa capabilities
        caps_dict = self._get_numa_capabilities(flavor['extra_specs'])
        if len(caps_dict) > 0:
            logger.debug("numa_capabilities_info: %s" % caps_dict)
            hpa_caps.append(caps_dict)

        # storage capabilities
        caps_dict = self._get_storage_capabilities(flavor)
        if len(caps_dict) > 0:
            logger.debug("storage_capabilities_info: %s" % caps_dict)
            hpa_caps.append(caps_dict)

        # CPU instruction set extension capabilities
        caps_dict = self._get_instruction_set_capabilities(
            flavor['extra_specs'])
        if len(caps_dict) > 0:
            logger.debug("instruction_set_capabilities_info: %s" % caps_dict)
            hpa_caps.append(caps_dict)

        # PCI passthrough capabilities
        caps_dict = self._get_pci_passthrough_capabilities(
            flavor['extra_specs'])
        if len(caps_dict) > 0:
            logger.debug("pci_passthrough_capabilities_info: %s" % caps_dict)
            hpa_caps.append(caps_dict)

        # ovsdpdk capabilities
        caps_dict = self._get_ovsdpdk_capabilities()
        if len(caps_dict) > 0:
            logger.debug("ovsdpdk_capabilities_info: %s" % caps_dict)
            hpa_caps.append(caps_dict)

        return hpa_caps

    def _get_hpa_basic_capabilities(self, flavor):
        basic_capability = {}
        feature_uuid = uuid.uuid4()

        basic_capability['hpa-capability-id'] = str(feature_uuid)
        basic_capability['hpa-feature'] = 'basicCapabilities'
        basic_capability['architecture'] = 'generic'
        basic_capability['hpa-version'] = 'v1'

        basic_capability['hpa-feature-attributes'] = []
        basic_capability['hpa-feature-attributes'].append({
            'hpa-attribute-key': 'numVirtualCpu',
            'hpa-attribute-value': json.dumps(
                {'value': str(flavor['vcpus'])})})
        basic_capability['hpa-feature-attributes'].append({
            'hpa-attribute-key': 'virtualMemSize',
            'hpa-attribute-value': json.dumps({'value': str(
                flavor['ram']), 'unit': 'GB'})})

        return basic_capability

    def _get_cpupinning_capabilities(self, extra_specs):
        cpupining_capability = {}
        feature_uuid = uuid.uuid4()

        if (extra_specs.get('hw:cpu_policy') or
                extra_specs.get('hw:cpu_thread_policy')):
            cpupining_capability['hpa-capability-id'] = str(feature_uuid)
            cpupining_capability['hpa-feature'] = 'cpuPinning'
            cpupining_capability['architecture'] = 'generic'
            cpupining_capability['hpa-version'] = 'v1'

            cpupining_capability['hpa-feature-attributes'] = []
            if extra_specs.get('hw:cpu_thread_policy'):
                cpupining_capability['hpa-feature-attributes'].append({
                    'hpa-attribute-key': 'logicalCpuThreadPinningPolicy',
                    'hpa-attribute-value': json.dumps({'value': str(
                        extra_specs['hw:cpu_thread_policy'])})})
            if extra_specs.get('hw:cpu_policy'):
                cpupining_capability['hpa-feature-attributes'].append({
                    'hpa-attribute-key': 'logicalCpuPinningPolicy',
                    'hpa-attribute-value': json.dumps({'value': str(
                        extra_specs['hw:cpu_policy'])})})

        return cpupining_capability

    def _get_cputopology_capabilities(self, extra_specs):
        cputopology_capability = {}
        feature_uuid = uuid.uuid4()

        if (extra_specs.get('hw:cpu_sockets') or
                extra_specs.get('hw:cpu_cores') or
                extra_specs.get('hw:cpu_threads')):
            cputopology_capability['hpa-capability-id'] = str(feature_uuid)
            cputopology_capability['hpa-feature'] = 'cpuTopology'
            cputopology_capability['architecture'] = 'generic'
            cputopology_capability['hpa-version'] = 'v1'

            cputopology_capability['hpa-feature-attributes'] = []
            if extra_specs.get('hw:cpu_sockets'):
                cputopology_capability['hpa-feature-attributes'].append({
                    'hpa-attribute-key': 'numCpuSockets',
                    'hpa-attribute-value': json.dumps({'value': str(
                        extra_specs['hw:cpu_sockets'])})})
            if extra_specs.get('hw:cpu_cores'):
                cputopology_capability['hpa-feature-attributes'].append({
                    'hpa-attribute-key': 'numCpuCores',
                    'hpa-attribute-value': json.dumps({'value': str(
                        extra_specs['hw:cpu_cores'])})})
            if extra_specs.get('hw:cpu_threads'):
                cputopology_capability['hpa-feature-attributes'].append({
                    'hpa-attribute-key': 'numCpuThreads',
                    'hpa-attribute-value': json.dumps({'value': str(
                        extra_specs['hw:cpu_threads'])})})

        return cputopology_capability

    def _get_hugepages_capabilities(self, extra_specs):
        hugepages_capability = {}
        feature_uuid = uuid.uuid4()

        if extra_specs.get('hw:mem_page_size'):
            hugepages_capability['hpa-capability-id'] = str(feature_uuid)
            hugepages_capability['hpa-feature'] = 'hugePages'
            hugepages_capability['architecture'] = 'generic'
            hugepages_capability['hpa-version'] = 'v1'

            hugepages_capability['hpa-feature-attributes'] = []
            if extra_specs['hw:mem_page_size'] == 'large':
                hugepages_capability['hpa-feature-attributes'].append({
                    'hpa-attribute-key': 'memoryPageSize',
                    'hpa-attribute-value': json.dumps(
                        {'value': '2', 'unit': 'MB'})})
            elif extra_specs['hw:mem_page_size'] == 'small':
                hugepages_capability['hpa-feature-attributes'].append({
                    'hpa-attribute-key': 'memoryPageSize',
                    'hpa-attribute-value': json.dumps(
                        {'value': '4', 'unit': 'KB'})})
            elif extra_specs['hw:mem_page_size'] == 'any':
                logger.info("Currently HPA feature memoryPageSize "
                            "did not support 'any' page!!")
            else:
                hugepages_capability['hpa-feature-attributes'].append({
                    'hpa-attribute-key': 'memoryPageSize',
                    'hpa-attribute-value': json.dumps({'value': str(
                        extra_specs['hw:mem_page_size']), 'unit': 'KB'})
                    })

        return hugepages_capability

    def _get_numa_capabilities(self, extra_specs):
        numa_capability = {}
        feature_uuid = uuid.uuid4()

        if extra_specs.get('hw:numa_nodes'):
            numa_capability['hpa-capability-id'] = str(feature_uuid)
            numa_capability['hpa-feature'] = 'numa'
            numa_capability['architecture'] = 'generic'
            numa_capability['hpa-version'] = 'v1'

            numa_capability['hpa-feature-attributes'] = []
            numa_capability['hpa-feature-attributes'].append({
                'hpa-attribute-key': 'numaNodes',
                'hpa-attribute-value': json.dumps({'value': str(
                    extra_specs['hw:numa_nodes'])})
                })

            for num in range(0, int(extra_specs['hw:numa_nodes'])):
                numa_cpu_node = "hw:numa_cpus.%s" % num
                numa_mem_node = "hw:numa_mem.%s" % num
                numacpu_key = "numaCpu-%s" % num
                numamem_key = "numaMem-%s" % num

                if (extra_specs.get(numa_cpu_node) and
                        extra_specs.get(numa_mem_node)):
                    numa_capability['hpa-feature-attributes'].append({
                        'hpa-attribute-key': numacpu_key,
                        'hpa-attribute-value': json.dumps({'value': str(
                            extra_specs[numa_cpu_node])})
                        })
                    numa_capability['hpa-feature-attributes'].append({
                        'hpa-attribute-key': numamem_key,
                        'hpa-attribute-value': json.dumps({'value': str(
                            extra_specs[numa_mem_node]), 'unit': 'MB'})
                        })

        return numa_capability

    def _get_storage_capabilities(self, flavor):
        storage_capability = {}
        feature_uuid = uuid.uuid4()

        storage_capability['hpa-capability-id'] = str(feature_uuid)
        storage_capability['hpa-feature'] = 'localStorage'
        storage_capability['architecture'] = 'generic'
        storage_capability['hpa-version'] = 'v1'

        storage_capability['hpa-feature-attributes'] = []
        storage_capability['hpa-feature-attributes'].append({
            'hpa-attribute-key': 'diskSize',
            'hpa-attribute-value': json.dumps({'value': str(
                flavor['disk']), 'unit': 'MB'})
            })
        storage_capability['hpa-feature-attributes'].append({
            'hpa-attribute-key': 'swapMemSize',
            'hpa-attribute-value': json.dumps({'value': str(
                flavor.get('swap', 0)), 'unit': 'MB'})
            })
        storage_capability['hpa-feature-attributes'].append({
            'hpa-attribute-key': 'ephemeralDiskSize',
            'hpa-attribute-value': json.dumps({'value': str(
                flavor.get('OS-FLV-EXT-DATA:ephemeral', 0)), 'unit': 'GB'})
            })
        return storage_capability

    def _get_instruction_set_capabilities(self, extra_specs):
        instruction_capability = {}
        feature_uuid = uuid.uuid4()

        if extra_specs.get('hw:capabilities:cpu_info:features'):
            instruction_capability['hpa-capability-id'] = str(feature_uuid)
            instruction_capability['hpa-feature'] = 'instructionSetExtensions'
            instruction_capability['architecture'] = 'Intel64'
            instruction_capability['hpa-version'] = 'v1'

            instruction_capability['hpa-feature-attributes'] = []
            instruction_capability['hpa-feature-attributes'].append({
                'hpa-attribute-key': 'instructionSetExtensions',
                'hpa-attribute-value': json.dumps(
                    {'value': extra_specs[
                        'hw:capabilities:cpu_info:features']})
                })
        return instruction_capability

    def _get_pci_passthrough_capabilities(self, extra_specs):
        instruction_capability = {}
        feature_uuid = uuid.uuid4()

        if extra_specs.get('pci_passthrough:alias'):
            value1 = extra_specs['pci_passthrough:alias'].split(':')
            value2 = value1[0].split('-')

            instruction_capability['hpa-capability-id'] = str(feature_uuid)
            instruction_capability['hpa-feature'] = 'pciePassthrough'
            instruction_capability['architecture'] = str(value2[2])
            instruction_capability['hpa-version'] = 'v1'

            instruction_capability['hpa-feature-attributes'] = []
            instruction_capability['hpa-feature-attributes'].append({
                'hpa-attribute-key': 'pciCount',
                'hpa-attribute-value': json.dumps({'value': value1[1]})
                })
            instruction_capability['hpa-feature-attributes'].append({
                'hpa-attribute-key': 'pciVendorId',
                'hpa-attribute-value': json.dumps({'value': value2[3]})
                })
            instruction_capability['hpa-feature-attributes'].append({
                'hpa-attribute-key': 'pciDeviceId',
                'hpa-attribute-value': json.dumps({'value': value2[4]})
                })

        return instruction_capability

    def _get_ovsdpdk_capabilities(self):
        ovsdpdk_capability = {}
        feature_uuid = uuid.uuid4()

        if not self._vim_info:
            self._vim_info = self.get_vim(get_all=True)
        cloud_extra_info_str = self._vim_info.get('cloud-extra-info')
        if not isinstance(cloud_extra_info_str, dict):
            try:
                cloud_extra_info_str = json.loads(cloud_extra_info_str)
            except Exception as ex:
                logger.error("Can not convert cloud extra info %s %s" % (
                             str(ex), cloud_extra_info_str))
                return {}
        if cloud_extra_info_str:
            cloud_dpdk_info = cloud_extra_info_str.get("ovsDpdk")
            if cloud_dpdk_info:
                ovsdpdk_capability['hpa-capability-id'] = str(feature_uuid)
                ovsdpdk_capability['hpa-feature'] = 'ovsDpdk'
                ovsdpdk_capability['architecture'] = 'Intel64'
                ovsdpdk_capability['hpa-version'] = 'v1'

                ovsdpdk_capability['hpa-feature-attributes'] = []
                ovsdpdk_capability['hpa-feature-attributes'].append({
                    'hpa-attribute-key': str(cloud_dpdk_info.get("libname")),
                    'hpa-attribute-value': json.dumps(
                        {'value': cloud_dpdk_info.get("libversion")})
                    })
        return ovsdpdk_capability
