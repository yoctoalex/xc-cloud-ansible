#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: fetch_tenant_settings
short_description: Tenant Settings
description: 
    - Receive current tenant settings.
version_added: "0.0.1"
'''

EXAMPLES = r'''
---
- name: Fetch xC Cloud tenant details
  hosts: webservers
  collections:
    - yoctoalex.xc_cloud_modules
  connection: local

  environment:
    XC_API_TOKEN: "your_api_token"
    XC_TENANT: "console.ves.volterra.io"

  tasks:
    - name: fetch current tenant details
      fetch_tenant_settings:
      register: tenant
'''

RETURN = r'''
---
ctive_plan_transition_id:
    description:
        - Id of the plan transition request which is currently in state CREATING.
    type: str
company_name:
    description:
        - Company name of the tenant.
    type: str
domain:
    description:
        - Domain of the tenant.
    type: str
max_credentials_expiry:
    description:
        - CredentialsExpiry is a struct that holds max expiration days setting for the different credentials.
    type: object
name:
    description:
        - name will represent name of the tenant that is being accessed
    type: name
original_tenant:
    description:
        - orginal_tenant represent tenant id where the user belongs to
    type: str
otp_enabled:
    description:
        - OTP configuration for tenant scope.
    type: bool
otp_status:
    description:
        - OtpStatus can be either enabled/disabled or processing. Applying new policy can take time,
          especially if tenant has many users so for this purpose processing state is introduced.
    type: str
scim_enabled:
    description:
        - Flag to show SCIM is enabled for specific tenant.
    type: bool
sso_enabled:
    description:
        - Flag to show SSO is enabled for specific tenant.
    type: bool
state:
    description:
        - Tenant states
    type: bool
'''

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from ansible.module_utils.basic import AnsibleModule

from ..module_utils.client import XcRestClient
from ..module_utils.common import (
    F5ModuleError, AnsibleF5Parameters, f5_argument_spec
)


class Parameters(AnsibleF5Parameters):
    updatables = []

    returnables = [
        'active_plan_transition_id',
        'company_name',
        'domain',
        'max_credentials_expiry',
        'name',
        'otp_enabled',
        'otp_status',
        'sso_enabled',
        'state'
    ]

    def to_return(self):
        result = {}
        for returnable in self.returnables:
            result[returnable] = getattr(self, returnable)
        result = self._filter_params(result)
        return result

    def to_update(self):
        result = {}
        for updatebale in self.updatables:
            result[updatebale] = getattr(self, updatebale)
        result = self._filter_params(result)
        return result


class ModuleParameters(Parameters):
    pass


class ApiParameters(Parameters):
    @property
    def active_plan_transition_id(self):
        return self._values['active_plan_transition_id']

    @property
    def company_name(self):
        return self._values['company_name']

    @property
    def domain(self):
        return self._values['domain']

    @property
    def max_credentials_expiry(self):
        return self._values['max_credentials_expiry']

    @property
    def name(self):
        return self._values['name']

    @property
    def otp_enabled(self):
        return self._values['otp_enabled']

    @property
    def otp_status(self):
        return self._values['otp_status']

    @property
    def sso_enabled(self):
        return self._values['sso_enabled']

    @property
    def state(self):
        return self._values['state']


class Changes(Parameters):
    def to_return(self):
        result = {}
        try:
            for returnable in self.returnables:
                result[returnable] = getattr(self, returnable)
            result = self._filter_params(result)
        except Exception:
            raise
        return result

    def to_update(self):
        result = {}
        try:
            for updatebale in self.updatables:
                result[updatebale] = getattr(self, updatebale)
            result = self._filter_params(result)
        except Exception:
            raise
        return result


class ModuleManager(object):
    def __init__(self, *args, **kwargs):
        self.module = kwargs.get('module', None)
        self.client = XcRestClient(**self.module.params)

        self.want = ModuleParameters(params=self.module.params)
        self.have = ApiParameters()

    def _merge_dicts(self, dict1, dict2):
        for k in set(dict1.keys()).union(dict2.keys()):
            if k in dict1 and k in dict2:
                if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                    yield k, dict(self._merge_dicts(dict1[k], dict2[k]))
                elif dict2[k] is None:
                    pass
                else:
                    yield k, dict2[k]
            elif k in dict1:
                if dict1[k] is None:
                    pass
                else:
                    yield k, dict1[k]
            else:
                if dict2[k] is None:
                    pass
                else:
                    yield k, dict2[k]

    def exec_module(self):
        changed = False
        result = dict()
        state = self.want.state

        self.exists()

        changes = self.have.to_return()
        result.update(**changes)
        result.update(dict(changed=changed))
        return result

    def exists(self):
        uri = f"/api/web/namespaces/system/tenant/settings"
        response = self.client.api.get(url=uri)
        if response.status == 404:
            return False
        if response.status not in [200, 201, 202]:
            raise F5ModuleError(response.content)
        if response.json().get('name', None):
            self.have = ApiParameters(params=response.json())
            return True
        return False


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = False
        self.argument_spec = {}
        self.argument_spec.update(f5_argument_spec)


def main():
    spec = ArgumentSpec()

    module = AnsibleModule(
        argument_spec=spec.argument_spec,
        supports_check_mode=spec.supports_check_mode
    )
    try:
        mm = ModuleManager(module=module)
        results = mm.exec_module()
        module.exit_json(**results)
    except F5ModuleError as ex:
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()