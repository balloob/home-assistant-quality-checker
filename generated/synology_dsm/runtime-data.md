```markdown
# synology_dsm: runtime-data

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [runtime-data](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/runtime-data)                                                     |
| Status | **done**                                                                 |
| Reason |                                                                          |

## Overview

This rule requires that runtime data, which is data needed during the lifetime of a configuration entry but not persisted, be stored in the `ConfigEntry.runtime_data` attribute. It also encourages using a custom typed `ConfigEntry` for better type safety.

The `synology_dsm` integration fully complies with this rule.

1.  **Typed ConfigEntry:** The integration defines a dataclass `SynologyDSMData` in `homeassistant/components/synology_dsm/coordinator.py`:
    ```python
    @dataclass
    class SynologyDSMData:
        """Data for the synology_dsm integration."""

        api: SynoApi
        coordinator_central: SynologyDSMCentralUpdateCoordinator
        coordinator_central_old_update_success: bool
        coordinator_cameras: SynologyDSMCameraUpdateCoordinator | None
        coordinator_switches: SynologyDSMSwitchUpdateCoordinator | None

    type SynologyDSMConfigEntry = ConfigEntry[SynologyDSMData]
    ```
    This dataclass holds the core API object (`SynoApi`) and the various `DataUpdateCoordinator` instances needed by the integration's platforms. A custom type alias `SynologyDSMConfigEntry` is created, correctly typing the `runtime_data` attribute.

2.  **Storing in `runtime_data`:** In `homeassistant/components/synology_dsm/__init__.py`, the `async_setup_entry` function is correctly typed as `async_setup_entry(hass: HomeAssistant, entry: SynologyDSMConfigEntry)`. Inside this function, after setting up the API and coordinators, the `SynologyDSMData` instance is created and assigned to `entry.runtime_data`:
    ```python
    entry.runtime_data = SynologyDSMData(
        api=api,
        coordinator_central=coordinator_central,
        coordinator_central_old_update_success=True,
        coordinator_cameras=coordinator_cameras,
        coordinator_switches=coordinator_switches,
    )
    ```

3.  **Accessing from `runtime_data`:** Various parts of the integration correctly access the stored runtime data by referencing `entry.runtime_data`. Examples include:
    *   In `__init__.py`'s `async_unload_entry`: `entry_data = entry.runtime_data`
    *   In `__init__.py`'s `async_remove_config_entry_device`: `data = entry.runtime_data`
    *   In `config_flow.py`'s `SynologyDSMOptionsFlowHandler`: `syno_data = self.config_entry.runtime_data`
    *   In `media_source.py`'s `async_get_media_source`, `_async_build_diskstations`, and `SynologyDsmMediaView`: `diskstation = entry.runtime_data`
    *   In `backup.py`'s `SynologyDSMBackupAgent`: `syno_data = entry.runtime_data`
    *   In `repairs.py`'s `MissingBackupSetupRepairFlow`: `syno_data = self.entry.runtime_data`
    *   In `diagnostics.py`'s `async_get_config_entry_diagnostics`: `data = entry.runtime_data`

Entities access the API and coordinators either through the `SynologyDSMBaseEntity` constructor (which are populated in `__init__.py` from the `runtime_data`) or, in the case of the coordinators holding a reference to the `api`, via `self.coordinator.api`. This access pattern is consistent with the data being rooted in `runtime_data`.

The implementation correctly utilizes `ConfigEntry.runtime_data` with a typed dataclass to store and manage runtime-specific data, fully satisfying the rule's requirements.

## Suggestions

No suggestions needed.
```

_Created at 2025-05-25 11:47:19. Prompt tokens: 39457, Output tokens: 983, Total tokens: 41834_
