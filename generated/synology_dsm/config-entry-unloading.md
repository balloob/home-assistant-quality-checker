```markdown
# synology_dsm: config-entry-unloading

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [config-entry-unloading](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-entry-unloading)                                                     |
| Status | **done**                                                                 |
| Reason |                                                                          |

## Overview

This rule requires integrations using config entries to implement `async_unload_entry` for proper runtime unloading and resource cleanup. This integration uses config entries, as seen in `manifest.json` (`"config_flow": true`) and the presence of `async_setup_entry` in `__init__.py`. Therefore, the rule applies.

The `synology_dsm` integration fully follows this rule.

The integration implements the `async_unload_entry` function in `homeassistant/components/synology_dsm/__init__.py`. This function performs the necessary cleanup steps:

1.  It calls `await hass.config_entries.async_unload_platforms(entry, PLATFORMS)` to unload all registered platforms (sensors, binary_sensors, cameras, switches, update, buttons, media_source) associated with this config entry. This is the standard and recommended way to handle platform unloading.
2.  If platform unloading is successful (`unload_ok` is True), it calls `await entry_data.api.async_unload()` on the custom `SynoApi` instance stored in the config entry's `runtime_data`.

The `SynoApi.async_unload` method, defined in `homeassistant/components/synology_dsm/common.py`, specifically calls `await self.dsm.logout()`. This ensures the underlying `py-synologydsm-api` library session is properly closed, releasing the connection and resources held by the library.

Furthermore, the integration utilizes `entry.async_on_unload` in `async_setup_entry` (`homeassistant/components/synology_dsm/__init__.py`) to register callbacks for cleaning up specific listeners:
*   `entry.async_on_unload(entry.add_update_listener(_async_update_listener))` handles the listener for options updates.
*   `entry.async_on_unload(entry.async_on_state_change(async_notify_backup_listeners))` handles a state change listener related to the backup agent.

Entity cleanup is handled implicitly when `async_unload_platforms` is called. Custom entities like `SynologyDSMBaseEntity` (`homeassistant/components/synology_dsm/entity.py`) use `self.async_on_remove(self._api.subscribe(...))` in `async_added_to_hass`. `async_on_remove` automatically triggers the cleanup callable provided by `_api.subscribe` when the entity is removed as part of the platform unloading, effectively removing the entity from the API's internal tracking (`_fetching_entities`).

The coordinators, inheriting from `DataUpdateCoordinator`, automatically stop their update timers when the entry is unloaded, so no explicit stop is needed in `async_unload_entry` for the coordinators themselves.

Overall, the integration correctly implements `async_unload_entry` and uses appropriate helper methods (`async_unload_platforms`, `entry.async_on_unload`, `entity.async_on_remove`) and library methods (`self.dsm.logout`) to ensure proper cleanup during unloading.

## Suggestions

No suggestions needed.
```

_Created at 2025-05-25 11:48:13. Prompt tokens: 39522, Output tokens: 806, Total tokens: 41250_
