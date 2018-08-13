# Copyright (c) 2018 Amdocs
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import mock
import unittest
import urllib2

from azure.pub.utils import restcall


class TestRestCall(unittest.TestCase):

    def test_combine_url(self):
        url = ["http://a.com/test/", "http://a.com/test/",
               "http://a.com/test", "http://a.com/test"]
        res = ["/resource", "resource", "/resource", "resource"]
        expected = "http://a.com/test/resource"
        for i in range(len(url)):
            self.assertEqual(expected, restcall.combine_url(url[i], res[i]))

    @mock.patch.object(restcall, "call_req")
    def test_get_res_from_aai(self, mock_call):
        res = "cloud-regions"
        content = ""
        expect_url = "https://aai.api.simpledemo.openecomp.org:8443/aai/v13"
        expect_user = "AAI"
        expect_pass = "AAI"
        expect_headers = {
            'X-FromAppId': 'MultiCloud',
            'X-TransactionId': '9001',
            'content-type': 'application/json',
            'accept': 'application/json'
        }
        restcall.get_res_from_aai(res, content=content)
        mock_call.assert_called_once_with(
            expect_url, expect_user, expect_pass, restcall.rest_no_auth,
            res, "GET", content, expect_headers)

    @mock.patch.object(restcall, "call_req")
    def test_req_by_msb(self, mock_call):
        res = "multicloud"
        method = "GET"
        content = "no content"
        restcall.req_by_msb(res, method, content=content)
        expect_url = "http://msb.onap.org:10080/"
        mock_call.assert_called_once_with(
            expect_url, "", "", restcall.rest_no_auth, res, method,
            content)

    @mock.patch("httplib2.Http.request")
    def test_call_req_success(self, mock_req):
        mock_resp = {
            "status": "200"
        }
        resp_content = "hello"
        mock_req.return_value = mock_resp, resp_content
        expect_ret = [0, resp_content, "200", mock_resp]
        ret = restcall.call_req("http://onap.org/", "user", "pass",
                                restcall.rest_no_auth, "vim", "GET")
        self.assertEqual(expect_ret, ret)

    @mock.patch("httplib2.Http.request")
    def test_call_req_not_200(self, mock_req):
        mock_resp = {
            "status": "404"
        }
        resp_content = "hello"
        mock_req.return_value = mock_resp, resp_content
        expect_ret = [1, resp_content, "404", mock_resp]
        ret = restcall.call_req("http://onap.org/", "user", "pass",
                                restcall.rest_no_auth, "vim", "GET")
        self.assertEqual(expect_ret, ret)

    @mock.patch("traceback.format_exc")
    @mock.patch("sys.exc_info")
    @mock.patch("httplib2.Http.request")
    def test_call_req_response_not_ready(self, mock_req, mock_sys,
                                         mock_traceback):
        mock_sys.return_value = "httplib.ResponseNotReady"
        mock_req.side_effect = [Exception("httplib.ResponseNotReady")] * 3
        expect_ret = [1, "Unable to connect to http://onap.org/vim", "", ""]
        ret = restcall.call_req("http://onap.org/", "user", "pass",
                                restcall.rest_no_auth, "vim", "GET")
        self.assertEqual(expect_ret, ret)
        self.assertEqual(3, mock_req.call_count)

    @mock.patch("httplib2.Http.request")
    def test_call_req_url_err(self, mock_req):
        urlerr = urllib2.URLError("urlerror")
        mock_req.side_effect = [urlerr]
        expect_ret = [2, str(urlerr), "", ""]
        ret = restcall.call_req("http://onap.org/", "user", "pass",
                                restcall.rest_no_auth, "vim", "GET")
        self.assertEqual(expect_ret, ret)
