# devolo_home_network: unique-config-entry

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_network](https://www.home-assistant.io/integrations/devolo_home_network/) |
| Rule   | [unique-config-entry](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/unique-config-entry)                                                     |
| Status | **done**                                                                 |

## Overview

The `unique-config-entry` rule applies to this integration because it has `config_flow: true` in its `manifest.json`, meaning it is configured through the Home Assistant UI. The purpose of this rule is to prevent a user from accidentally setting up the same device more than once.

The `devolo_home_network` integration correctly follows this rule by using a unique identifier (the device's serial number) to ensure each device is configured only once. This is implemented in its config flow (`config_flow.py`).

**1. User-initiated setup (`async_step_user`):**
When a user manually adds the integration, the flow validates the input and fetches the device's serial number. It then uses this serial number as a unique ID for the config entry.

*Code Reference (`config_flow.py`):*
```python
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        # ...
            else:
                info = await validate_input(self.hass, user_input)
                await self.async_set_unique_id(
                    info[SERIAL_NUMBER], raise_on_progress=False
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info[TITLE], data=user_input)
        # ...
```
The calls to `async_set_unique_id` and `_abort_if_unique_id_configured` ensure that if an entry with the same serial number already exists, the flow is aborted, preventing duplicates.

**2. Discovery setup (`async_step_zeroconf`):**
When a device is discovered via Zeroconf, the flow extracts the serial number (`SN`) from the discovery properties and uses it as the unique ID.

*Code Reference (`config_flow.py`):*
```python
    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        # ...
        await self.async_set_unique_id(discovery_info.properties["SN"])
        self._abort_if_unique_id_configured(
            updates={CONF_IP_ADDRESS: discovery_info.host}
        )
        # ...
```
This implementation also correctly prevents duplicate entries from discovery and has the added benefit of updating the IP address of an already configured device if it changes.

Both configuration paths properly implement the uniqueness check as recommended by the rule documentation.

---

_Created at 2025-06-25 19:06:49 using gemini-2.5-pro. Prompt tokens: 19325, Output tokens: 700, Total tokens: 22058._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
