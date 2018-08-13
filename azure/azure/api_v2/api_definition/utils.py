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

import pkg_resources
import yaml


def get_definition_list():
    """ Get API Definition from YAML files. """

    api_def = []
    definition_dir = __name__[:__name__.rfind(".")]
    for f in pkg_resources.resource_listdir(definition_dir, '.'):
        if f.endswith(".yaml"):
            with pkg_resources.resource_stream(definition_dir, f) as fd:
                # TODO(xiaohhui): Should add exception handler to inform user of
                # potential error.
                api_def.append(yaml.safe_load(fd))

    return api_def
