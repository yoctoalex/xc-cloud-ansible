#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
'''

EXAMPLES = r'''
---
'''

RETURN = r'''
---
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