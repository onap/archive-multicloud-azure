# Copyright (c) 2017-2018 VMware, Inc.
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
# import traceback

# from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from azure.pub.exceptions import VimDriverAzureException
from azure.swagger import utils

logger = logging.getLogger(__name__)


class SwaggerJsonView(APIView):
    def get(self, request):

        return Response(utils.get_swagger_json_data())
