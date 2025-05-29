```markdown
# synology_dsm: async-dependency

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [async-dependency](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/async-dependency)                                                     |
| Status | **done**                                                                 |

## Overview

This rule requires that an integration's primary external dependency (the library used to communicate with the device/service) is asynchronous, and that the integration uses the library in an asynchronous manner. This is crucial for preventing the blocking of the Home Assistant event loop, which can cause performance issues.

The `synology_dsm` integration uses the `py-synologydsm-api` library (as specified in `manifest.json`). Review of the integration code confirms that this library appears to be designed for asynchronous operations, leveraging `aiohttp` via `async_get_clientsession` (seen in `common.py` and `config_flow.py`).

The integration consistently interacts with the `SynologyDSM` object and its various API modules (`file`, `information`, `network`, `photos`, `security`, `storage`, `surveillance_station`, `system`, `upgrade`, `utilisation`, `external_usb`) using `await` keyword calls within `async` functions.

Specific examples include:
*   `__init__.py`: `await api.async_setup()`, `await coordinator_cameras.async_config_entry_first_refresh()`.
*   `common.py`: `await self.dsm.login()`, `await self.information.update()`, `await self.dsm.file.get_shared_folders()`, `await self._update()`, `await self.system.reboot()`, `await self.dsm.logout()`. These are all awaited calls to the library or internal async helper methods wrapping library calls.
*   `coordinator.py`: The update coordinators (`SynologyDSMCentralUpdateCoordinator`, `SynologyDSMCameraUpdateCoordinator`, `SynologyDSMSwitchUpdateCoordinator`) are based on `DataUpdateCoordinator`, which is inherently async. Their `_async_update_data` methods correctly use `await` when calling library update functions like `await self.api.async_update()` or `await surveillance_station.get_home_mode_status()`.
*   `config_flow.py`: `await _login_and_fetch_syno_info(api, otp_code)` which in turn awaits various library login and update calls. `await api.file.get_shared_folders()`.
*   `media_source.py`: Awaited calls like `await diskstation.api.photos.get_albums()`, `await diskstation.api.photos.download_item_thumbnail()`. The `SynologyDsmMediaView.get` method also awaits library download calls.
*   `backup.py`: Methods like `async_download_backup`, `async_upload_backup`, `async_delete_backup`, `async_list_backups` all correctly use `await` when interacting with `self._file_station`.
*   Entity files (`binary_sensor.py`, `sensor.py`, etc.): While many entity properties access data synchronously (e.g., `self._api.storage.get_volume(...)`), these access patterns appear to be fetching data that was previously populated by an awaited update call within a coordinator or `SynoApi`, which is the intended pattern for polling integrations with async libraries. Camera image fetching (`camera.py`) correctly uses `await self._api.surveillance_station.get_camera_image()`. Button presses (`button.py`) are also handled asynchronously via `await self.entity_description.press_action(self.syno_api)()`.

Based on the widespread use of `await` when interacting with the `py-synologydsm-api` library throughout the integration's async code paths, it demonstrates that the integration correctly leverages the asynchronous capabilities of its dependency.

## Suggestions

No suggestions needed. The integration correctly utilizes its asynchronous dependency.
```

_Created at 2025-05-25 11:52:54. Prompt tokens: 39184, Output tokens: 927, Total tokens: 42595_
