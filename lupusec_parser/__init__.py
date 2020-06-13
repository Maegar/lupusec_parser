#!/usr/bin/env python3
# Copyright 2020 Paul Proske
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pychrome
import base64


def gatherInformation(url, username, password):
    # create a browser instance
    browser = pychrome.Browser(url="http://127.0.0.1:9222")

    # create a tab
    tab = browser.new_tab()

    # register callback if you want
    def request_will_be_sent(**kwargs):
        if (kwargs.get('type') == 'XHR') & (kwargs.get('request').get('method') == 'POST'):
            print("---------%s---------" % kwargs.get('response').get('url'))
            print("Request: %s" % tab.Network.getRequestBody(requestId=kwargs.get('requestId')))
            print("-------------------------\n")

    # register callback if you want
    def response_receied(**kwargs):
        if kwargs.get('type') == 'XHR':
            print("---------%s---------" % kwargs.get('response').get('url'))
            print("Response: %s" % tab.Network.getResponseBody(requestId=kwargs.get('requestId')))#.get('url'))
            print("-------------------------\n")


    tab.Network.requestWillBeSent = request_will_be_sent
    tab.Network.responseReceived = response_receied


    def continue_requests(**kwargs):
        tab.Fetch.continueRequest(requestId=kwargs['requestId'])

    def do_auth(**kwargs):
        tab.Fetch.continueWithAuth(requestId=kwargs['requestId'], authChallengeResponse={'response': 'ProvideCredentials', 'username': username, 'password': password})
        tab.Fetch.disable()

    tab.Fetch.authRequired = do_auth
    tab.Fetch.requestPaused = continue_requests

    tab.start()
    tab.Fetch.enable(handleAuthRequests=True)
    tab.Security.setIgnoreCertificateErrors(ignore=True)
    tab.Network.enable()
    tab.Page.navigate(url=url, _timeout=5)
    tab.wait(5)
    tab.stop()
    browser.close_tab(tab)