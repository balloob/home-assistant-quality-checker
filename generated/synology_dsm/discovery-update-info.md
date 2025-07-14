```markdown
# synology_dsm: discovery-update-info

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [discovery-update-info](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/discovery-update-info)                                                     |
| Status | **done**                                                                 |

## Overview

This rule requires that integrations using network discovery protocols should use the discovery information to update the network address (like the IP address) of an already configured device. This ensures that the integration continues to work even if the device's IP address changes via DHCP. The update should only occur if the integration can confidently identify that the discovered device is the same as the configured one, typically using a unique identifier like a MAC address or serial number.

The `synology_dsm` integration uses both SSDP and Zeroconf discovery, as declared in its `manifest.json`:

```json
  "ssdp": [
    {
      "manufacturer": "Synology",
      "deviceType": "urn:schemas-upnp-org:device:Basic:1"
    }
  ],
  "zeroconf": [
    {
      "type": "_http._tcp.local.",
      "properties": {
        "vendor": "synology*"
      }
    }
  ]
```

The integration handles these discovery protocols in its `config_flow.py` file via `async_step_zeroconf` and `async_step_ssdp`. Both of these methods delegate the core logic to `_async_from_discovery`.

The `_async_from_discovery` method implements the required logic:
1.  It extracts the discovered `host` and a list of `discovered_macs` (using the MAC address found in the discovery properties, which serves as the NAS serial number).
2.  It iterates through the `discovered_macs`. For each MAC address, it sets the flow's unique ID using `await self.async_set_unique_id(discovered_mac)`.
3.  It then attempts to find an existing config entry using the MAC address as the unique identifier via `self._async_get_existing_entry(discovered_mac)`.
4.  If an `existing_entry` is found and the discovered IP address (`host`) is different from the currently configured IP (`existing_entry.data[CONF_HOST]`), it performs a check to ensure both are valid IP addresses of the same version (IPv4 or IPv6).
5.  If these conditions pass, it updates the host IP address in the existing config entry's data using `self.hass.config_entries.async_update_entry(existing_entry, data={**existing_entry.data, CONF_HOST: host})`.
6.  Finally, it aborts the flow with the reason `"reconfigure_successful"`, indicating that the existing entry was updated based on the new discovery information.

This process correctly identifies the same device using its MAC address/serial number and updates the stored host information in the config entry if the IP address has changed, fulfilling the requirements of the `discovery-update-info` rule.

## Suggestions

No suggestions needed. The integration correctly implements the requirements of the `discovery-update-info` rule.
```

_Created at 2025-05-25 11:49:47. Prompt tokens: 39678, Output tokens: 761, Total tokens: 41446_
