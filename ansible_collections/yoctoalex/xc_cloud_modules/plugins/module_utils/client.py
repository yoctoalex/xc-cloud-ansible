# -*- coding: utf-8 -*-
#
# Copyright (c) 2020 F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os
from ..module_utils.constants import BASE_HEADERS

from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import Request

try:
    import json as _json
except ImportError:
    import simplejson as _json


class XcRestClient(object):
    def __init__(self, *args, **kwargs):
        self.params = kwargs
        self.module = kwargs.get('module', None)
        self.provider = self.params.get('provider', None)
        self.api_token = self.merge_provider_api_token_param(self.provider)
        self.tenant = self.merge_provider_tenant_param(self.provider)

    @staticmethod
    def validate_params(key, store):
        if store and key in store and store[key] is not None:
            return True
        else:
            return False

    def merge_provider_api_token_param(self, provider):
        result = None
        if self.validate_params('api_token', provider):
            result = provider['api_token']
        elif self.validate_params('XC_API_TOKEN', os.environ):
            result = os.environ.get('XC_API_TOKEN')
        return result

    def merge_provider_tenant_param(self, provider):
        result = None
        if self.validate_params('tenant', provider):
            result = provider['tenant']
        elif self.validate_params('XC_TENANT', os.environ):
            result = os.environ.get('XC_TENANT')
        return result

    @property
    def api(self):
        return RestApi(
            headers={"Authorization": "APIToken {0}".format(self.api_token)},
            host=self.tenant
        )


class RestApi(object):
    def __init__(self, headers=None, use_proxy=True, force=False, timeout=120,
                 validate_certs=True, url_username=None, url_password=None,
                 http_agent=None, force_basic_auth=False, follow_redirects='urllib2',
                 client_cert=None, client_key=None, cookies=None, host=None):
        self.request = Request(
            headers=headers,
            use_proxy=use_proxy,
            force=force,
            timeout=timeout,
            validate_certs=validate_certs,
            url_username=url_username,
            url_password=url_password,
            http_agent=http_agent,
            force_basic_auth=force_basic_auth,
            follow_redirects=follow_redirects,
            client_cert=client_cert,
            client_key=client_key,
            cookies=cookies
        )
        self.last_url = None
        self.host = host

    def get_headers(self, result):
        try:
            return dict(result.getheaders())
        except AttributeError:
            return result.headers

    def update_response(self, response, result):
        response.headers = self.get_headers(result)
        response._content = result.read()
        response.status = result.getcode()
        response.url = result.geturl()
        response.msg = "OK (%s bytes)" % response.headers.get('Content-Length', 'unknown')

    def send(self, method, url, **kwargs):
        response = Response()

        self.last_url = url

        body = None
        data = kwargs.pop('data', None)
        json = kwargs.pop('json', None)

        if not data and json is not None:
            self.request.headers.update(BASE_HEADERS)
            body = _json.dumps(json)
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
        if data:
            body = data
        if body:
            kwargs['data'] = body

        try:
            result = self.request.open(method, url, **kwargs)
        except HTTPError as e:
            # Catch HTTPError delivered from Ansible
            #
            # The structure of this object, in Ansible 2.8 is
            #
            # HttpError {
            #   args
            #   characters_written
            #   close
            #   code
            #   delete
            #   errno
            #   file
            #   filename
            #   filename2
            #   fp
            #   getcode
            #   geturl
            #   hdrs
            #   headers
            #   info
            #   msg
            #   name
            #   reason
            #   strerror
            #   url
            #   with_traceback
            # }
            self.update_response(response, e)
            return response

        self.update_response(response, result)
        return response

    def delete(self, url, **kwargs):
        return self.send('DELETE', f"https://{self.host}{url}", **kwargs)

    def get(self, url, **kwargs):
        return self.send('GET', f"https://{self.host}{url}", **kwargs)

    def patch(self, url, data=None, **kwargs):
        return self.send('PATCH', f"https://{self.host}{url}", data=data, **kwargs)

    def post(self, url, data=None, **kwargs):
        return self.send('POST', f"https://{self.host}{url}", data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.send('PUT', f"https://{self.host}{url}", data=data, **kwargs)


class Response(object):
    def __init__(self):
        self._content = None
        self.status = None
        self.headers = dict()
        self.url = None
        self.reason = None
        self.request = None
        self.msg = None

    @property
    def content(self):
        return self._content

    @property
    def raw_content(self):
        return self._content

    def json(self):
        return _json.loads(self._content or 'null')

    @property
    def ok(self):
        if self.status is not None and int(self.status) > 400:
            return False
        try:
            response = self.json()
            if 'code' in response and response['code'] > 400:
                return False
        except ValueError:
            pass
        return True
