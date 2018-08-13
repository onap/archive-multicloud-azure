# Copyright (c) 2018 Amdocs
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

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from azure.swagger.views.swagger_json import SwaggerJsonView


# Registry
from azure.swagger.views.registry.views import Registry
from azure.swagger.views.registry.views import UnRegistry




urlpatterns = [
    # swagger
    url(r'^api/multicloud-azure/v0/swagger.json$', SwaggerJsonView.as_view()),

    # Registry
    url(r'^api/multicloud-azure/v0/(?P<vimid>[0-9a-z-A-Z\-\_]+)/registry$',
        Registry.as_view()),
    url(r'^api/multicloud-azure/v0/(?P<vimid>[0-9a-z-A-Z\-\_]+)$',
        UnRegistry.as_view()),

]

urlpatterns = format_suffix_patterns(urlpatterns)
