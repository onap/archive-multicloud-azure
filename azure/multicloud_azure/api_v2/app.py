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

import pecan


def setup_app(config=None):
    app_conf = {
        'root': "azure.api_v2.api_router.root.RootController",
        'modules': ["azure.api_v2"],
        'debug': True,
        # NOTE: By default, guess_content_type_from_ext is True, and Pecan will
        # strip the file extension from url. For example, ../../swagger.json
        # will look like ../../swagger to Pecan API router. This makes other
        # url like ../../swagger.txt get the same API route. Set this to False
        # to do strict url mapping.
        'guess_content_type_from_ext': False
    }
    app = pecan.make_app(
        app_conf.pop('root'),
        **app_conf
    )

    return app
