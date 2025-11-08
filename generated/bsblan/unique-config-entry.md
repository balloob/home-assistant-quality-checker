# bsblan: unique-config-entry

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [unique-config-entry](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/unique-config-entry)                                                     |
| Status | **done**                                                                 |

## Overview

The `unique-config-entry` rule applies to this integration as it has a config flow (`config_flow: true` in `manifest.json`) for setting up the device via the UI.

The integration correctly follows this rule by ensuring a single BSB-Lan device cannot be configured more than once. It achieves this by using the device's MAC address as a unique identifier for the config entry.

The implementation can be found in `config_flow.py`:

1.  **User-initiated Flow (`async_step_user`):**
    *   This flow eventually calls the `_get_bsblan_info` helper method.
    *   Inside `_get_bsblan_info`, the integration connects to the device, retrieves its MAC address, and uses it to establish uniqueness:
        ```python
        # homeassistant/components/bsblan/config_flow.py

        device = await bsblan.device()
        retrieved_mac = device.MAC
        # ...
        await self.async_set_unique_id(
            format_mac(self.mac), raise_on_progress=raise_on_progress
        )
        # ...
        self._abort_if_unique_id_configured(
            updates={
                CONF_HOST: self.host,
                CONF_PORT: self.port,
            }
        )
        ```
    *   This sequence of calling `async_set_unique_id` followed by `_abort_if_unique_id_configured` is the correct pattern to prevent duplicate entries.

2.  **Discovery Flow (`async_step_zeroconf`):**
    *   The discovery flow is robust and handles two scenarios.
    *   If the MAC address is available in the Zeroconf discovery properties, it is immediately used to set the unique ID and check for existing configurations.
        ```python
        # homeassistant/components/bsblan/config_flow.py

        if self.mac:
            await self.async_set_unique_id(format_mac(self.mac))
            self._abort_if_unique_id_configured(...)
        ```
    *   If the MAC is not in the discovery data, the integration first aborts if an entry with the same host and port already exists (`_async_abort_entries_match`). It then tries to fetch the MAC from the device API. If successful, it sets the unique ID and performs the `_abort_if_unique_id_configured` check, just like in the user flow.

This comprehensive approach ensures that whether a user adds the device manually or it's discovered on the network, the integration correctly prevents duplicates.

## Suggestions

No suggestions needed.

---

_Created at 2025-08-05 09:39:52 using gemini-2.5-pro. Prompt tokens: 11626, Output tokens: 713, Total tokens: 14515._

_Report based on [`ee9ff71`](https://github.com/home-assistant/core/tree/ee9ff717e0d36ca02bf52a242acd3a47359eae61)._

_AI can be wrong. Always verify the report and the code against the rule._
