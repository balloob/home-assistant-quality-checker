```markdown
# synology_dsm: unique-config-entry

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [unique-config-entry](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/unique-config-entry)                                                     |
| Status | **done**                                                                 |

## Overview

This rule requires that an integration prevents the user from setting up the same device or service more than once, typically by using a unique identifier derived from the device or service itself within the config flow. This rule applies to the `synology_dsm` integration as it uses a config flow (`manifest.json` sets `config_flow: true`) and supports discovery (`ssdp`, `zeroconf`).

The `synology_dsm` integration correctly implements this rule. It leverages Home Assistant's built-in unique ID handling within the config flow to prevent duplicate entries for the same Synology DSM device.

The core logic is handled within the `SynologyDSMFlowHandler` in `config_flow.py`:

1.  **Discovery (`async_step_zeroconf`, `async_step_ssdp`, `_async_from_discovery`)**: When a Synology device is discovered via Zeroconf or SSDP, the flow extracts the MAC address(es) (which serve as the device's serial number). It then iterates through these MACs and calls `self.async_set_unique_id(discovered_mac)`. This sets the unique ID for the *config flow instance*. It then checks for existing entries using `self._async_get_existing_entry(discovered_mac)` and `self._abort_if_unique_id_configured()`. If a matching entry is found, it either updates the host if necessary (in the case of an IP change) or aborts the flow with `already_configured`.
2.  **Manual Setup / Validation (`async_validate_input_create_entry`)**: This function is called from `async_step_user` (manual setup) and `async_step_link` (discovery follow-up). After successfully logging into the DSM API, it fetches the device's serial number using `api.information.serial`. It then calls `await self.async_set_unique_id(serial, raise_on_progress=False)`. This sets the *final* unique ID for the configuration entry based on the device's serial number, which is the definitive unique identifier for the NAS device. If a config entry with this serial number already exists (checked implicitly by `async_set_unique_id` and managed through the flow's state or explicitly via `_async_get_existing_entry` in discovery), the flow proceeds to update the existing entry if needed (e.g., reauthentication or reconfigure) rather than creating a new one.

By using the NAS serial number (derived from the MAC during discovery and confirmed via the API after login) as the `unique_id` for the configuration entry and utilizing `self.async_set_unique_id` and the associated duplicate detection mechanisms, the integration effectively prevents multiple config entries for the same Synology DSM device.

## Suggestions

No suggestions needed. The integration correctly follows the rule.
```

_Created at 2025-05-25 11:47:51. Prompt tokens: 40124, Output tokens: 743, Total tokens: 42159_
