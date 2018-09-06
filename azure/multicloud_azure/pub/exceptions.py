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


class ClientException(Exception):

    message = "ClientException"

    def __init__(self, message=None):
        self.message = message or self.message
        super(ClientException, self).__init__(self.message)


class ServerException(Exception):

    message = "ServerException"

    def __init__(self, message=None, status_code="", content=""):
        super(ServerException, self).__init__(message)
        self.message = message or self.message
        self.status_code = status_code
        self.content = content


class RetriableConnectionFailure(Exception):
    pass


class ConnectionError(ClientException):
    message = "Cannot connect to API service."


class ConnectTimeout(ConnectionError, RetriableConnectionFailure):
    message = "Timed out connecting to service."


class ConnectFailure(ConnectionError, RetriableConnectionFailure):
    message = "Connection failure that may be retried."


class SSLError(ConnectionError):
    message = "An SSL error occurred."


class UnknownConnectionError(ConnectionError):

    def __init__(self, msg, original):
        super(UnknownConnectionError, self).__init__(msg)
        self.original = original


class NotFoundError(ServerException):
    message = "Cannot find value"


class VimDriverAzureException(ServerException):
    message = "Cannot find  vim driver"
