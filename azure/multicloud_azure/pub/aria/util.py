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

import threading


def make_template_name(user, template_name):
    return "{}.{}".format(user, template_name)


class SafeDict(dict):
    def __init__(self, *args):
        self._lockobj = threading.Lock()
        dict.__init__(self, args)

    def __getitem__(self, key):
        try:
            self._lockobj.acquire()
        except Exception as ex:
            raise ex
        finally:
            self._lockobj.release()

    def __setitem__(self, key, value):
        try:
            self._lockobj.acquire()
            dict.__setitem__(self, key, value)
        except Exception as ex:
            raise ex
        finally:
            self._lockobj.release()
