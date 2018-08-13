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
import eventlet
eventlet.monkey_patch()

import os # noqa
from oslo_config import cfg # noqa
from oslo_service import service # noqa
import sys # noqa
# FIXME: Since there is no explicitly setup process for the project. Hack the
# python here.
sys.path.append(os.path.abspath('.'))

from azure.api_v2 import service as api_service # noqa


def main():
    try:
        api_server = api_service.WSGIService()
        launcher = service.launch(cfg.CONF,
                                  api_server,
                                  workers=api_server.workers)
        launcher.wait()
    except RuntimeError as excp:
        sys.stderr.write("ERROR: %s\n" % excp)
        sys.exit(1)


if __name__ == '__main__':
    main()
