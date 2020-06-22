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
import pychrome.exceptions
import base64
import json

def gatherInformation(url, username, password, time):
    # create a browser instance
    browser = pychrome.Browser(url="http://127.0.0.1:9222")

    # create a tab
    tab = browser.new_tab()

    requests = {}
    
    # register callback if you want
    def request_will_be_sent(**kwargs):
        #print(kwargs.get('type'))
        if kwargs.get('type') == 'XHR':
            url = kwargs.get('request').get('url')
            request = {'method': kwargs.get('request').get('method'),
                       'header_accept': kwargs.get('request').get('headers').get('Accept')}

            if kwargs.get('request').get('method') == 'POST':
                data = tab.Network.getRequestPostData(requestId=kwargs.get('requestId'))
                request['postData'] = data
            
            requests[url] = {'request': request,
                             'requestId': kwargs.get('requestId')}
    
    
    # register callback if you want
    def response_receied(**kwargs):
        if kwargs.get('type') == 'XHR':
            url = kwargs.get('response').get('url')
            try:
                bodyResp = tab.Network.getResponseBody(requestId=kwargs.get('requestId'))
                bodyResp = bodyResp['body'].replace('\n', '').replace('\t', '')
            except pychrome.exceptions.CallMethodException as cmex:
                print('Error while reading body for ID %s and URL %s\n\t%s' % (kwargs.get('requestId'), url, cmex))
                bodyResp = kwargs
            
            response = {'mime_type': kwargs.get('response').get('mimeType'),
                        'status': kwargs.get('response').get('status'),
                        'status_text': kwargs.get('response').get('statusText'),
                        'body': bodyResp}
            
            requests[url]['response'] = response


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
    tab.Network.enable()
    tab.Fetch.enable(handleAuthRequests=True)
    tab.Security.setIgnoreCertificateErrors(ignore=True)
    tab.Page.navigate(url=url, _timeout=time)
    tab.wait(time)
    tab.stop()
    browser.close_tab(tab)

    for x, y in requests.items():
        print('--------------- ' + x + ' ---------------')
        print(json.dumps(y, indent=4, sort_keys=True))
        print('------------------------------------------\n')