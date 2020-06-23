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

"""LUPUSEC UI extractor.

This module is able to recognize HTTP requests and response pairs for a LUPUSEC UI
(alarm-panel). All important data will be printed to the console. This is typically
needed for reverse engineering of LUPUSEC alarm panels. To do so chromedev tools
will be used - therefore chrome must be started in debugging mode before
e.g. /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

Port is set fix to 9222

  Typical usage example:

  lupusec_parser.gatherInformation(lupusec_url, lupusec_username, lupusec_password)
"""

import pychrome
import pychrome.exceptions
import base64
import json

class LupusecExtractor:
    """Lupusec extractor.

    This extractor contains all functions to capture / extract HTTP request and
    response pairs.

    Attributes:
        result: Dictionary with all details for all captured request and response pairs 
    """

    def __init__(self, url, username, password):
        """ Initialise the class 
        
        Args:
            url: The Lupusec URL.
            username: Username for login to the Lupusec UI
            password: Password for login to the Lupusec UI
        """
        self._url = url
        self._username = username
        self._password = password
        self._browser = pychrome.Browser(url="http://127.0.0.1:9222")
        self.result = {}

    def _capture_request(self, **kwargs):
        """ Capture outgoing XHR request """
        if kwargs.get('type') == 'XHR':
            http_request = kwargs.get('request')
            request = {'method': http_request.get('method'),
                    'header_accept': http_request.get('headers').get('Accept')}
            
            reqId = kwargs.get('requestId')
            if http_request.get('method') == 'POST':
                data = self._tab.Network.getRequestPostData(requestId=reqId)
                request['postData'] = data

            self.result[reqId] = {'request': request, 'url': http_request.get('url')}
    
    
    def _capture_response(self, **kwargs):
        """ Capture incoming XHR response """
        if kwargs.get('type') == 'XHR':

            http_response = kwargs.get('response')
            response = {'mime_type': http_response.get('mimeType'),
                        'status': http_response.get('status'),
                        'status_text': http_response.get('statusText')}
            
            self.result[kwargs.get('requestId')]['response'] = response

    def _capture_finished_loaded_response(self, **kwargs):
        """ Capture finish loaded XHR response body """
        reqId = kwargs.get('requestId')
        if reqId in self.result:
            bodyResp = self._tab.Network.getResponseBody(requestId=reqId)
            self.result[kwargs.get('requestId')]['request']['body'] = bodyResp['body'].replace('\n', '').replace('\t', '')

    def _continue_requests(self, **kwargs):
        """ Continue the request """
        self._tab.Fetch.continueRequest(requestId=kwargs['requestId'])

    def _do_auth(self, **kwargs):
        """ Do the authorization """
        self._tab.Fetch.continueWithAuth(requestId=kwargs['requestId'], authChallengeResponse={'response': 'ProvideCredentials', 'username': self._username, 'password': self._password})
        self._tab.Fetch.disable()

    def gatherInformation(self, timeout):
        """ Collect information from Lupusec UI

        Open a new tab in the remote debugging chrome to access Lupusec UI and
        capture all request response pairs that will be automatically loaded

        Args:
            timeout: Seconds how long we will wait for collection informations
        
        Returns:
            A dict mapping request IDs to the corresponding XHR response / requests pairs.
            Each tuple contains a request and response pair in a dict format.
        """
        self._tab = self._browser.new_tab()

        self._tab.Network.requestWillBeSent = self._capture_request
        self._tab.Network.responseReceived = self._capture_response
        self._tab.Network.loadingFinished = self._capture_finished_loaded_response

        self._tab.Fetch.authRequired = self._do_auth
        self._tab.Fetch.requestPaused = self._continue_requests
        
        self._tab.start()
        self._tab.Network.enable()
        self._tab.Fetch.enable(handleAuthRequests=True)
        self._tab.Security.setIgnoreCertificateErrors(ignore=True)
        self._tab.Page.navigate(url=self._url, _timeout=timeout)
        self._tab.wait(timeout)
        self._tab.stop()
        self._browser.close_tab(self._tab)

        return self.result
    
    def print_result(self):
        """ Print the result to console """
        for y in self.result.values():
            print('--------------- ' + y['url'] + ' ---------------')
            print(json.dumps(y, indent=4, sort_keys=True))
            print('------------------------------------------\n')