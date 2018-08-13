#    Copyright (c) 2018 Amdocs
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import json
from keystoneauth1.identity import v2 as keystone_v2
from keystoneauth1.identity import v3 as keystone_v3
from keystoneauth1 import session
import pecan
from pecan import rest
import re

from azure.api_v2.api_definition import utils
from azure.pub import exceptions
from azure.pub.msapi import extsys


OBJ_IN_ARRAY = "(\w+)\[(\d+)\]\.(\w+)"


def _get_vim_auth_session(vim_id, tenant_id):
    """ Get the auth session to the given backend VIM """

    try:
        vim = extsys.get_vim_by_id(vim_id)
    except exceptions.VimDriverAzureException as e:
        return pecan.abort(500, str(e))

    params = {
        "auth_url": vim["url"],
        "username": vim["userName"],
        "password": vim["password"],
    }
    params["tenant_id"] = tenant_id

    if '/v2' in params["auth_url"]:
        auth = keystone_v2.Password(**params)
    else:
        params["user_domain_name"] = vim["domain"]
        params["project_domain_name"] = vim["domain"]

        if 'tenant_id' in params:
            params["project_id"] = params.pop("tenant_id")
        if 'tenant_name' in params:
            params["project_name"] = params.pop("tenant_name")
        if '/v3' not in params["auth_url"]:
            params["auth_url"] = params["auth_url"] + "/v3",
        auth = keystone_v3.Password(**params)

    return session.Session(auth=auth)


def _convert_default_value(default):
    return {"None":None, "true": True, "false": False}[default]


def _property_exists(resource, attr, required=False):
    if attr not in resource:
        if required:
            raise Exception("Required field %s is missed in VIM "
                            "resource %s", (attr, resource))
        else:
            return False

    return True


def _convert_vim_res_to_mc_res(vim_resource, res_properties):
    mc_resource = {}
    for key in res_properties:
        vim_res, attr = res_properties[key]["source"].split('.', 1)
        # action = res_properties[key].get("action", "copy")
        if re.match(OBJ_IN_ARRAY, attr):
            attr, index, sub_attr = re.match(OBJ_IN_ARRAY, attr).groups()
            if _property_exists(vim_resource[vim_res], attr):
                mc_resource[key] = (
                    vim_resource[vim_res][attr][int(index)][sub_attr])
        else:
            if _property_exists(vim_resource[vim_res], attr,
                                res_properties[key].get("required")):
                mc_resource[key] = vim_resource[vim_res][attr]
            else:
                if "default" in res_properties[key]:
                    mc_resource[key] = _convert_default_value(
                        res_properties[key]["default"])

    return mc_resource


def _convert_mc_res_to_vim_res(mc_resource, res_properties):
    vim_resource = {}
    for key in res_properties:
        vim_res, attr = res_properties[key]["source"].split('.', 1)
        # action = res_properties[key].get("action", "copy")
        if re.match(OBJ_IN_ARRAY, attr):
            attr, index, sub_attr = re.match(OBJ_IN_ARRAY, attr).groups()
            if _property_exists(mc_resource, key):
                vim_resource[attr] = vim_resource.get(attr, [])
                if vim_resource[attr]:
                    vim_resource[attr][0].update({sub_attr: mc_resource[key]})
                else:
                    vim_resource[attr].append({sub_attr: mc_resource[key]})
        else:
            if _property_exists(mc_resource, key,
                                res_properties[key].get("required")):
                vim_resource[attr] = mc_resource[key]

    return vim_resource


def _build_api_controller(api_meta):
    # Assume that only one path
    path, path_meta = api_meta['paths'].items()[0]
    # url path is behind third slash. The first is vimid, the second is
    # tenantid.
    path = path.split("/")[3]
    controller_name = path.upper() + "Controller"
    delimiter = path_meta["vim_path"].find("/", 1)
    service_type = path_meta["vim_path"][1:delimiter]
    resource_url = path_meta["vim_path"][delimiter:]

    # Assume there is only one resource.
    name, resource_meta = api_meta['definitions'].items()[0]
    resource_properties = resource_meta['properties']

    controller_meta = {}
    if "get" in path_meta:
        # Add the get method to controller.
        @pecan.expose("json")
        def _get(self, vim_id, tenant_id, resource_id):
            """ General GET """
            session = _get_vim_auth_session(vim_id, tenant_id)
            service = {'service_type': service_type,
                       'interface': 'public'}
            full_url = resource_url + "/%s" % resource_id
            resp = session.get(full_url, endpoint_filter=service)
            mc_res = _convert_vim_res_to_mc_res(resp.json(),
                                                resource_properties)
            mc_res.update({"vimName": vim_id,
                           "vimId": vim_id,
                           "tenantId": tenant_id,
                           "returnCode": 0})
            return mc_res

        controller_meta["get"] = _get

    if "get_all" in path_meta:
        # Add the get_all method to controller.
        @pecan.expose("json")
        def _get_all(self, vim_id, tenant_id):
            """ General GET all """
            session = _get_vim_auth_session(vim_id, tenant_id)
            service = {'service_type': service_type,
                       'interface': 'public'}
            resp = session.get(resource_url, endpoint_filter=service)
            vim_res = resp.json()[resource_meta['plural_vim_resource']]
            mc_res = [_convert_vim_res_to_mc_res(
                          {resource_meta['vim_resource']: v},
                          resource_properties)
                      for v in vim_res]
            return {"vimName": vim_id,
                    resource_meta['plural']: mc_res,
                    "tenantId": tenant_id,
                    "vimid": vim_id}

        controller_meta["get_all"] = _get_all

    if "post" in path_meta:
        # Add the post method to controller.
        @pecan.expose("json")
        def _post(self, vim_id, tenant_id):
            """ General POST """
            session = _get_vim_auth_session(vim_id, tenant_id)
            service = {'service_type': service_type,
                       'interface': 'public'}
            vim_res = _convert_mc_res_to_vim_res(pecan.request.json_body,
                                                 resource_properties)

            req_body = json.JSONEncoder().encode(
                {resource_meta['vim_resource']: vim_res})
            resp = session.post(resource_url,
                                data=req_body,
                                endpoint_filter=service)
            mc_res = _convert_vim_res_to_mc_res(resp.json(),
                                                resource_properties)
            mc_res.update({"vimName": vim_id,
                           "vimId": vim_id,
                           "tenantId": tenant_id,
                           "returnCode": 0})
            return mc_res

        controller_meta["post"] = _post

    if "delete" in path_meta:
        # Add the delete method to controller.
        @pecan.expose("json")
        def _delete(self, vim_id, tenant_id, resource_id):
            """ General DELETE """
            session = _get_vim_auth_session(vim_id, tenant_id)
            service = {'service_type': service_type,
                       'interface': 'public'}
            full_url = resource_url + "/%s" % resource_id
            session.delete(full_url, endpoint_filter=service)

        controller_meta["delete"] = _delete

    return path, type(controller_name, (rest.RestController,), controller_meta)


def insert_dynamic_controller(root_controller):
    api_defs = utils.get_definition_list()
    for d in api_defs:
        path, con_class = _build_api_controller(d)
        setattr(root_controller, path, con_class())
