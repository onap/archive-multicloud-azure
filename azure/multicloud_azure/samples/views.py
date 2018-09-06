# Copyright (c) 2018 Amdocs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:

#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import os
import logging

from rest_framework.views import APIView
from rest_framework.response import Response

logger = logging.getLogger(__name__)
log_file = "/var/log/onap/multicloud/azure/azure.log"


class SampleList(APIView):
    """
    List all samples.
    """

    def get(self, request, format=None):
        logger.debug("get")
        output = ""
        if os.path.exists(log_file):
            with open("/var/log/onap/multicloud/azure/azure.log", "r") as f:
                lines = f.readlines()
                output = lines[-1]
        return Response({"status": "active", "logs": output})
