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

import inspect
import json
from collections import defaultdict
from rest_framework import status


keystoneV2Json = \
    {
        "auth": {
            "tenantName": "",
            "passwordCredentials": {
                "username": "",
                "password": ""
            }
        }
    }


SUCCESS_STATE = [status.HTTP_200_OK, status.HTTP_201_CREATED,
                 status.HTTP_202_ACCEPTED]


def fun_name():
    return inspect.stack()[1][3]


def jsonResponse(data, encoding='utf-8'):

    content_type = "application/json"
    try:
        res = json.loads(data, encoding=encoding)
    except Exception:
        res = data
        content_type = "text/plain"
    return (res, content_type)


class Catalogs(object):

    def __init__(self):
        self.ct = defaultdict(dict)

    def storeEndpoint(self, vimid, endpoints):
        if vimid in self.ct:
            self.ct[vimid].update(endpoints)
        else:
            self.ct.setdefault(vimid, endpoints)

    def getEndpointBy(self, vimid, serverType, interface='public'):

        vim = self.ct.get(vimid)
        return vim.get(serverType).get(interface, "") if vim else ""


def verifyKeystoneV2(param):

    return _walk_json(param, keystoneV2Json)


# comapare two json by key
def _walk_json(data, data2):
    if isinstance(data, dict) and isinstance(data2, dict):
        if set(data.keys()) != set(data2.keys()):
            return False
        else:
            v1 = data.values()
            v2 = data2.values()
            v1.sort()
            v2.sort()
            if len(v1) != len(v2):
                return False
            for (i, j) in zip(v1, v2):
                # continue compare key
                if isinstance(i, dict) and isinstance(j, dict):
                    if not _walk_json(i, j):
                        return False
                # ignore value
                else:
                    continue

            return True

    return False


def keystoneVersion(url, version="v3"):

    tmp = url.split("/")
    v = tmp[-1]
    if v not in ["v2.0", "v3"]:
        url += "/" + version
    else:
        tmp[-1] = version
        url = "/".join(tmp)

    return url


catalog = Catalogs()
