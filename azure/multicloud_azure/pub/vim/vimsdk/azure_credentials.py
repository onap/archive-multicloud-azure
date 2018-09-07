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

from azure.common.credentials import ServicePrincipalCredentials


class ClientObj(object):

    def get_client_obj(self, params):
        if params is None:
            params = {}
        TENANT_ID = params['tenant_id']
        CLIENT = params['username']
        KEY = params['password']

        credentials = ServicePrincipalCredentials(client_id=CLIENT,
                                                  secret=KEY, tenant=TENANT_ID)

        return credentials
