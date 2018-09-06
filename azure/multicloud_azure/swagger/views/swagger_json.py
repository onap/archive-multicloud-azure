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


import json
import logging
import os

from rest_framework.response import Response
from rest_framework.views import APIView


logger = logging.getLogger(__name__)


class SwaggerJsonView(APIView):
    def get(self, request):
        json_file = os.path.join(os.path.dirname(
            __file__), 'multivim.swagger.json')
        f = open(json_file)
        json_data = json.JSONDecoder().decode(f.read())
        f.close()
        # json_file = os.path.join(os.path.dirname(
        #     __file__), 'multivim.image.swagger.json')
        # f = open(json_file)
        # json_data_temp = json.JSONDecoder().decode(f.read())
        # f.close()
        # json_data["paths"].update(json_data_temp["paths"])
        # json_data["definitions"].update(json_data_temp["definitions"])
        json_data["basePath"] = "/api/multicloud-azure/v0/"
        json_data["info"]["title"] = "MultiVIM \
        driver of Microsoft Azure Service NBI"
        return Response(json_data)
