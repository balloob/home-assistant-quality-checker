# bsblan: config-entry-unloading

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [config-entry-unloading](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-entry-unloading)                                                     |
| Status | **done**                                                                 |

## Overview

The `config-entry-unloading` rule requires that integrations support being unloaded at runtime. This involves implementing the `async_unload_entry` function to clean up all resources created during setup.

The `bsblan` integration is configured via a config entry and sets up entities on multiple platforms (`climate`, `sensor`, `water_heater`). Therefore, this rule applies.

The integration correctly implements the `async_unload_entry` function in `homeassistant/components/bsblan/__init__.py`:

```python
async def async_unload_entry(hass: HomeAssistant, entry: BSBLanConfigEntry) -> bool:
    """Unload BSBLAN config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
```

This implementation adheres to Home Assistant's best practices. The call to `hass.config_entries.async_unload_platforms` handles the unloading of all entities associated with the config entry across the defined `PLATFORMS`. When the entities are unloaded, they also un-subscribe from the `BSBLanUpdateCoordinator`, which causes the coordinator to automatically stop its periodic polling.

The resources created in `async_setup_entry` (the `BSBLAN` client and the `DataUpdateCoordinator`) are properly managed and do not require further manual cleanup in `async_unload_entry`. Thus, the integration fully complies with the rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-08-04 08:34:37 using gemini-2.5-pro. Prompt tokens: 11099, Output tokens: 430, Total tokens: 13432._

_Report based on [`0ab5a05`](https://github.com/home-assistant/core/tree/0ab5a05a1f6e667e6da3771cfc802aa51388bbbe)._

_AI can be wrong. Always verify the report and the code against the rule._
