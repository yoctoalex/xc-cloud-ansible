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
    updatables = ['metadata', 'spec']

    returnables = ['metadata', 'spec']

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
    @property
    def metadata(self):
        return self._values['metadata']

    @property
    def spec(self):
        return self._values['spec']


class ApiParameters(Parameters):
    @property
    def metadata(self):
        return self._values['metadata']

    @property
    def spec(self):
        return self._values['spec']


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

        if state == 'present':
            changed = self.present()
        elif state == 'absent':
            changed = self.absent()
        elif state == 'fetch':
            self.exists()

        changes = self.have.to_return()
        result.update(**changes)
        result.update(dict(changed=changed))
        return result

    def present(self):
        if self.exists():
            return self.update()
        else:
            return self.create()

    def absent(self):
        if self.exists():
            return self.remove()
        return False

    def remove(self):
        uri = f"/api/config/namespaces/{self.want.metadata['namespace']}/http_loadbalancers/{self.want.metadata['name']}"
        response = self.client.api.delete(url=uri)
        if response.status == 404:
            return False
        if response.status not in [200, 201, 202]:
            raise F5ModuleError(response.content)

    def exists(self):
        uri = f"/api/config/namespaces/{self.want.metadata['namespace']}/http_loadbalancers/{self.want.metadata['name']}"
        response = self.client.api.get(url=uri)
        if response.status == 404:
            return False
        if response.status not in [200, 201, 202]:
            raise F5ModuleError(response.content)
        if response.json().get('metadata', None):
            self.have = ApiParameters(params=response.json())
            return True
        return False

    def create(self):
        uri = f"/api/config/namespaces/{self.want.metadata['namespace']}/http_loadbalancers"
        response = self.client.api.post(url=uri, json=self.want.to_update())
        if response.status not in [200, 201, 202]:
            raise F5ModuleError(response.content)
        self.have = ApiParameters(params=response.json())
        return True

    def update(self):
        if self.want.patch:
            to_update = dict(self._merge_dicts(self.have.to_update(), self.want.to_update()))
        else:
            to_update = self.want.to_update()
        uri = f"/api/config/namespaces/{self.want.metadata['namespace']}/http_loadbalancers/{self.want.metadata['name']}"
        response = self.client.api.put(url=uri, json=to_update)
        if response.status not in [200, 201, 202]:
            raise F5ModuleError(response.content)
        self.have = ApiParameters(params=to_update)
        return True


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = False

        argument_spec = dict(
            state=dict(
                default='present',
                choices=['present', 'absent', 'fetch']
            ),
            patch=dict(type='bool', default=False),
            metadata=dict(
                type='dict',
                name=dict(required=True),
                namespace=dict(required=True),
                labels=dict(type=dict),
                annotations=dict(type=dict),
                description=dict(type="str"),
                disable=dict(type='bool')
            ),
            spec=dict(
                type=dict,
                active_service_policies=dict(),
                add_location=dict(type='bool'),
                advertise_custom=dict(),
                advertise_on_public=dict(),
                advertise_on_public_default_vip=dict(),
                api_definition=dict(),
                api_protection_rules=dict(),
                api_rate_limit=dict(),
                app_firewall=dict(),
                blocked_clients=dict(),
                captcha_challenge=dict(),
                cookie_stickiness=dict(),
                cors_policy=dict(),
                data_guard_rules=dict(),
                ddos_mitigation_rules=dict(),
                default_route_pools=dict(),
                disable_api_definition=dict(),
                disable_ip_reputation=dict(),
                disable_rate_limit=dict(),
                disable_waf=dict(),
                do_not_advertise=dict(),
                domains=dict(type='list', elements='str', required=True),
                enable_ip_reputation=dict(),
                http=dict(),
                https=dict(),
                https_auto_cert=dict(),
                js_challenge=dict(),
                least_active=dict(),
                more_option=dict(),
                multi_lb_app=dict(),
                no_challenge=dict(),
                no_service_policies=dict(),
                policy_based_challenge=dict(),
                random=dict(),
                rate_limit=dict(),
                ring_hash=dict(),
                round_robin=dict(),
                routes=dict(),
                service_policies_from_namespace=dict(),
                single_lb_app=dict(),
                source_ip_stickiness=dict(),
                trusted_clients=dict(),
                user_id_client_ip=dict(),
                user_identification=dict(),
                waf_exclusion_rules=dict(),
            )
        )
        self.argument_spec = {}
        self.argument_spec.update(f5_argument_spec)
        self.argument_spec.update(argument_spec)


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