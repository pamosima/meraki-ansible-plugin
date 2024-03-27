from __future__ import (absolute_import, division, print_function)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

__metaclass__ = type

DOCUMENTATION = '''
name: meraki_devices
author:
    - Patrick Mosimann (@pamosima)
short_description: Ansible dynamic inventory plugin for Meraki Catalyst devices.
requirements:
    - meraki
extends_documentation_fragment:
    - constructed
description:
    - Reads inventories from the Meraki API.
    - Uses a YAML configuration file meraki_devices.[yml|yaml].
options:
    plugin:
        description: The name of this plugin, it should always be set to 'meraki_devices' for this plugin to recognize it as its own.
        type: str
        required: true
        choices:
            - meraki_devices
    host_vars:
        description:
            - Variables to assign to each host.
        type: dict
        required: False
    keyed_groups:
        description:
            - Add hosts to group based on the values of a variable.
        type: list
        required: False
    group_vars:
        description:
            - Define group variables using a Jinja2 expression.
        type: dict
        required: False
'''

EXAMPLES = '''
# meraki_devices.yml
plugin: meraki_devices
strict: False
keyed_groups:
  # group devices based on device type (e.g., meraki_device_type_MX64)
  - prefix: meraki_device_type
    key: meraki_device_type
  # group devices based on network ID
  - prefix: meraki_network_id
    key: network_id
'''

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.module_utils._text import to_native
import os
import json

try:
    import meraki
    HAS_MERAKI = True
except ImportError:
    HAS_MERAKI = False

class InventoryModule(BaseInventoryPlugin, Constructable):
    NAME = 'meraki_devices'

    def verify_file(self, path):
        return (
            super(InventoryModule, self).verify_file(path) and
            (path.endswith(('meraki_devices.yml', 'meraki_devices.yaml')))
        )

    def parse(self, inventory, loader, path, cache=True):
        if not HAS_MERAKI:
            raise AnsibleError('Meraki Python library missing. Please install it using `pip install meraki`.')
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)
        self._populate()

    def _populate(self):
        self.inventory.add_group('meraki_devices')
        MERAKI_API_KEY = os.getenv('MERAKI_API_KEY')
        MERAKI_ORG_ID = os.getenv('MERAKI_ORG_ID')

        if not MERAKI_API_KEY or not MERAKI_API_KEY.strip():
            raise AnsibleError("MERAKI_API_KEY environment variable not set or is empty.")
        if not MERAKI_ORG_ID or not MERAKI_ORG_ID.strip():
            raise AnsibleError("MERAKI_ORG_ID environment variable not set or is empty.")

        dashboard = meraki.DashboardAPI(
            api_key=MERAKI_API_KEY.strip(),
            base_url='https://api.meraki.com/api/v1/',
            output_log=False,
            print_console=False
        )
        try:
            networks = dashboard.organizations.getOrganizationNetworks(MERAKI_ORG_ID, total_pages='all')
            for network in networks:
                devices = dashboard.networks.getNetworkDevices(network['id'])
                for device in devices:
                # Check if lanIp is present and not None
                    if device.get('lanIp'):
                        hostname = device['name'] if 'name' in device else device['mac']
                        self.inventory.add_host(hostname, group='meraki_devices')
                        self.inventory.set_variable(hostname, 'ansible_host', device['lanIp'])
                        self.inventory.set_variable(hostname, 'meraki_device_type', device['model'])
                        self.inventory.set_variable(hostname, 'meraki_network', network['name'])

                        # Use the keyed_groups option defined in the configuration file
                        # to create groups based on device attributes
                        strict = self.get_option('strict')
                        keyed_groups = self.get_option('keyed_groups')
                        host_attr = device
                        # Add the host to the keyed groups
                        self._add_host_to_keyed_groups(keyed_groups, host_attr, hostname, strict=strict)
                    else:
                        # If lanIp is not present or is None, you can choose to log this information
                        # and continue to the next device without adding it to the inventory
                        self.display.warning("Skipping device without lanIp: %s" % device['name'])

        except Exception as e:
            error_msg = "Failed to get devices from Meraki API: {0}".format(to_native(e))
            raise AnsibleError(error_msg)