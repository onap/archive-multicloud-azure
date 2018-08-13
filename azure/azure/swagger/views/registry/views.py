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


import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from azure.pub.exceptions import VimDriverAzureException
from azure.pub.msapi import extsys
from azure.pub.utils.restcall import AAIClient


logger = logging.getLogger(__name__)


class Registry(APIView):
    # def _get_tenants(self, auth_info):
    #     tenant_instance = OperateTenant.OperateTenant()
    #     try:
    #         projects = tenant_instance.get_projects(auth_info)
    #     except Exception as e:
    #         logger.exception("get tenants error %(e)s", {"e": e})
    #         raise e
    #
    #     rsp = {"tenants": []}
    #     for project in projects:
    #         rsp['tenants'].append(project.to_dict())
    #     return rsp
    #
    # def _get_images(self, auth_info):
    #     image_instance = OperateImage.OperateImage(auth_info)
    #     try:
    #         images = image_instance.get_vim_images()
    #     except Exception as e:
    #         logger.exception("get images error %(e)s", {"e": e})
    #         raise e
    #
    #     rsp = {"images": []}
    #     for image in images:
    #         rsp['images'].append(image.to_dict())
    #     return rsp
    #
    # def _get_flavors(self, auth_info):
    #     flavors_op = OperateFlavors.OperateFlavors()
    #     try:
    #         flavors = flavors_op.list_flavors(
    #             auth_info, auth_info['tenant'])
    #     except Exception as e:
    #         logger.exception("get flavors error %(e)s", {"e": e})
    #         raise e
    #
    #     rsp = {"flavors": []}
    #     for flavor in flavors:
    #         flavor_info = flavor[0].to_dict()
    #         flavor_info['extra_specs'] = flavor[1].extra_specs
    #         rsp['flavors'].append(flavor_info)
    #     return rsp
    #
    # def _get_networks(self, auth_info):
    #     net_op = OperateNetwork.OperateNetwork()
    #     try:
    #         resp = net_op.list_networks(
    #             auth_info['vimId'], auth_info['tenant'])
    #     except Exception as e:
    #         logger.exception("get networks error %(e)s", {"e": e})
    #         raise e
    #
    #     rsp = {'networks': resp['networks']}
    #     return rsp
    #
    # def _get_hypervisors(self, auth_info):
    #     hypervisor_op = OperateHypervisor.OperateHypervisor()
    #     try:
    #         hypervisors = hypervisor_op.list_hypervisors(auth_info)
    #     except Exception as e:
    #         logger.exception("get hypervisors error %(e)s", {"e": e})
    #         raise e
    #
    #     rsp = {"hypervisors": []}
    #     for hypervisor in hypervisors:
    #         rsp['hypervisors'].append(hypervisor.to_dict())
    #     return rsp

    def _find_tenant_id(self, name, tenants):
        for tenant in tenants['tenants']:
            if tenant['name'] == name:
                return tenant['id']

    def post(self, request, vimid):
        try:
            vim_info = extsys.get_vim_by_id(vimid)
        except VimDriverAzureException as e:
            return Response(data={'error': str(e)}, status=e.status_code)
        data = {}
        data['vimId'] = vim_info['vimId']
        data['username'] = vim_info['userName']
        data['userName'] = vim_info['userName']
        data['password'] = vim_info['password']
        data['url'] = vim_info['url']
        data['project_name'] = vim_info['tenant']

        rsp = {}
        # get tenants
        try:
            logger.debug('Getting tenants')
            tenants = self._get_tenants(data)
            rsp.update(tenants)
            data['tenant'] = self._find_tenant_id(
                data['project_name'], tenants)
            data['project_id'] = data['tenant']
            # set default tenant
            # get images
            logger.debug('Getting images')
            images = self._get_images(data)
            rsp.update(images)
            # get flavors
            logger.debug('Getting flavors')
            flavors = self._get_flavors(data)
            rsp.update(flavors)
            # get networks
            logger.debug('Getting networks')
            networks = self._get_networks(data)
            rsp.update(networks)
            # get hypervisors
            logger.debug('Getting hypervisors')
            hypervisors = self._get_hypervisors(data)
            rsp.update(hypervisors)
            # update A&AI
            logger.debug('Put data into A&AI')
            cloud_owner, cloud_region = extsys.split_vim_to_owner_region(
                vimid)
            aai_adapter = AAIClient(cloud_owner, cloud_region)
            aai_adapter.update_vim(rsp)
        except Exception as e:
            if hasattr(e, "http_status"):
                return Response(data={'error': str(e)}, status=e.http_status)
            else:
                return Response(data={'error': str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data="", status=status.HTTP_200_OK)


class UnRegistry(APIView):

    def delete(self, request, vimid):
        try:
            cloud_owner, cloud_region = extsys.split_vim_to_owner_region(
                    vimid)
            aai_adapter = AAIClient(cloud_owner, cloud_region)
            aai_adapter.delete_vim()
        except Exception as e:
            return Response(data=e.message,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data="", status=status.HTTP_204_NO_CONTENT)
