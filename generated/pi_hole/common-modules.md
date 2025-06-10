# pi_hole: common-modules

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [common-modules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/common-modules)                                                     |
| Status | **todo**                                                                 |

## Overview

The `common-modules` rule applies to the `pi_hole` integration because it utilizes both a `DataUpdateCoordinator` for managing data updates and a base entity class for its various entities.

The integration partially follows the rule:
1.  **Base Entity:** The base entity `PiHoleEntity` is correctly defined in `homeassistant/components/pi_hole/entity.py`. This class is then subclassed by sensors, switches, binary sensors, and update entities within the integration, adhering to the rule's requirement for base entities.

2.  **Coordinator:** The integration does not fully follow the rule regarding the coordinator.
    *   In `homeassistant/components/pi_hole/__init__.py`, the `DataUpdateCoordinator` is instantiated directly:
        ```python
        # homeassistant/components/pi_hole/__init__.py
        # ...
        async def async_update_data() -> None:
            """Fetch data from API endpoint."""
            try:
                await api.get_data()
                await api.get_versions()
            except HoleError as err:
                raise UpdateFailed(f"Failed to communicate with API: {err}") from err
            if not isinstance(api.data, dict):
                raise ConfigEntryAuthFailed

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            config_entry=entry,
            name=name,
            update_method=async_update_data,
            update_interval=MIN_TIME_BETWEEN_UPDATES,
        )
        # ...
        ```
    *   The core data fetching logic (`async_update_data`) and the instantiation of `DataUpdateCoordinator` are located in `__init__.py`. The rule "The coordinator should be placed in `coordinator.py`" implies that such logic, typically encapsulated in a custom class inheriting from `DataUpdateCoordinator`, should reside in a separate `coordinator.py` file. This practice enhances consistency and makes it easier to locate the data fetching mechanism.

Due to the coordinator logic not being in a dedicated `coordinator.py` file, the integration is marked as "todo" for this rule.

## Suggestions

To make the `pi_hole` integration compliant with the `common-modules` rule, the coordinator logic should be moved into a dedicated `coordinator.py` file. This typically involves creating a custom coordinator class.

1.  **Create `homeassistant/components/pi_hole/coordinator.py`:**
    Add a new file named `coordinator.py` to the `homeassistant/components/pi_hole/` directory.

2.  **Define a custom coordinator class:**
    In `coordinator.py`, define a class (e.g., `PiHoleDataUpdateCoordinator`) that inherits from `DataUpdateCoordinator`. This class will encapsulate the data fetching logic.

    ```python
    # homeassistant/components/pi_hole/coordinator.py
    from __future__ import annotations

    import logging

    from hole import Hole, HoleError

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
    # ConfigEntryAuthFailed might be needed if auth checks are done within the coordinator update cycle
    # from homeassistant.exceptions import ConfigEntryAuthFailed

    from .const import MIN_TIME_BETWEEN_UPDATES # Ensure this constant is accessible

    _LOGGER = logging.getLogger(__name__)


    class PiHoleDataUpdateCoordinator(DataUpdateCoordinator[None]): # Using [None] as per current design
        """Manages fetching Pi-hole data from the API."""

        config_entry: ConfigEntry # For type hinting if the entry is stored/used

        def __init__(self, hass: HomeAssistant, api: Hole, name: str, entry: ConfigEntry) -> None:
            """Initialize the data update coordinator."""
            self.api = api
            self.config_entry = entry # Store entry if needed, e.g., for unique IDs or logging context
            super().__init__(
                hass,
                _LOGGER,
                name=name, # Name of the integration instance
                update_interval=MIN_TIME_BETWEEN_UPDATES,
            )

        async def _async_update_data(self) -> None:
            """Fetch data from API endpoint."""
            try:
                await self.api.get_data()
                await self.api.get_versions()
            except HoleError as err:
                raise UpdateFailed(f"Failed to communicate with API: {err}") from err
            # Note: The original ConfigEntryAuthFailed check in __init__.py was after the
            # first refresh and based on `api.data` not being a dict.
            # This check might be better suited in __init__.py after the initial refresh,
            # or handled via a different mechanism if it's a persistent auth issue.
            # For regular updates, UpdateFailed is for transient communication issues.
    ```

3.  **Update `homeassistant/components/pi_hole/__init__.py`:**
    Modify `__init__.py` to import and use the new `PiHoleDataUpdateCoordinator`.

    ```python
    # homeassistant/components/pi_hole/__init__.py
    # ... other imports
    from .coordinator import PiHoleDataUpdateCoordinator # NEW import
    from homeassistant.exceptions import ConfigEntryAuthFailed # Keep for the post-refresh check

    # ... (PiHoleData dataclass can remain here or move to coordinator.py if preferred)

    # The local async_update_data function is removed as its logic moves to the coordinator class

    async def async_setup_entry(hass: HomeAssistant, entry: PiHoleConfigEntry) -> bool:
        name = entry.data[CONF_NAME]
        host = entry.data[CONF_HOST]
        # ... (other config loading) ...
        api_key = entry.data.get(CONF_API_KEY, "")

        session = async_get_clientsession(hass, verify_tls)
        api = Hole(
            host,
            session,
            location=location,
            tls=use_tls,
            api_token=api_key,
        )

        # Instantiate the new coordinator
        coordinator = PiHoleDataUpdateCoordinator(hass, api, name, entry)

        await coordinator.async_config_entry_first_refresh()

        # The check for invalid data (potentially auth failure) after first refresh
        if not isinstance(api.data, dict):
            raise ConfigEntryAuthFailed("API data is not a dictionary after initial fetch, possibly an authentication issue.")

        entry.runtime_data = PiHoleData(api, coordinator) # Update PiHoleData type hint if it refers to coordinator

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        return True
    ```
    If `PiHoleData` is updated, ensure its type hint for `coordinator` reflects `PiHoleDataUpdateCoordinator`.

4.  **Update `PiHoleData` (Optional but good practice):**
    The `PiHoleData` dataclass in `__init__.py` should have its `coordinator` field type-hinted to the new `PiHoleDataUpdateCoordinator`.
    ```python
    # homeassistant/components/pi_hole/__init__.py
    from .coordinator import PiHoleDataUpdateCoordinator # ensure this is imported

    @dataclass
    class PiHoleData:
        """Runtime data definition."""

        api: Hole
        coordinator: PiHoleDataUpdateCoordinator # Updated type hint
    ```

**Why these changes satisfy the rule:**
*   By creating `PiHoleDataUpdateCoordinator` in `coordinator.py` and moving the data fetching logic (`_async_update_data`) into it, the coordinator "is placed in `coordinator.py`."
*   This centralizes the data fetching responsibilities, adhering to the common pattern promoted by the rule.
*   It improves code organization and makes it easier for other developers to find and understand the data update mechanism of the `pi_hole` integration, fulfilling the rule's goal of increasing consistency and improving developer experience.

---

_Created at 2025-06-10 23:06:20. Prompt tokens: 9984, Output tokens: 1945, Total tokens: 18452._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
