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
import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from multicloud_azure.pub.exceptions import VimDriverAzureException
from multicloud_azure.pub.msapi import extsys
from multicloud_azure.pub.utils.restcall import AAIClient
from multicloud_azure.pub.vim.vimapi.compute import OperateFlavors


logger = logging.getLogger(__name__)


class Registry(APIView):
    def _get_flavors(self, auth_info):
        flavors_op = OperateFlavors.OperateFlavors()
        try:
            flavors = flavors_op.list_flavors(auth_info)
        except Exception as e:
            logger.exception("get flavors error %(e)s", {"e": e})
            raise e

        rsp = {"flavors": flavors}
        return rsp

    def post(self, request, vimid):
        try:
            vim_info = extsys.get_vim_by_id(vimid)
        except VimDriverAzureException as e:
            return Response(data={'error': str(e)}, status=e.status_code)
        cloud_extra_info = json.loads(vim_info['cloud_extra_info'])
        data = {
            'subscription_id': cloud_extra_info['subscription_id'],
            'username': vim_info['username'],
            'password': vim_info['password'],
            'tenant_id': vim_info['default_tenant'],
            'region_id': vim_info['cloud-region-id']
        }
        rsp = {}
        try:
            logger.debug('Getting flavors')
            flavors = self._get_flavors(data)
            rsp.update(flavors)
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

class APIv1Registry(Registry):

    def post(self, request, cloud_owner, cloud_region_id):
        vimid = extsys.encode_vim_id(cloud_owner, cloud_region_id)
        return super(APIv1Registry, self).post(request, vimid)


class APIv1UnRegistry(UnRegistry):

    def delete(self, request, cloud_owner, cloud_region_id):
        vimid = extsys.encode_vim_id(cloud_owner, cloud_region_id)
        return super(APIv1UnRegistry, self).delete(request, vimid)
