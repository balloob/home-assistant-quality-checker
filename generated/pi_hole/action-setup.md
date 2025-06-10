# pi_hole: action-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [action-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-setup)                                                     |
| Status | **todo**                                       |
| Reason |                                                                          |

## Overview

The `action-setup` rule requires that service actions provided by an integration are registered in the main `async_setup` function of the integration (typically located in `__init__.py`). This ensures that services are known to Home Assistant and can be validated (e.g., in automations) even if the associated configuration entry is not currently loaded. If a targeted config entry is not loaded, the service handler itself should raise a `ServiceValidationError`.

The `pi_hole` integration defines one service, `disable`, as specified in `services.yaml` and implemented in `switch.py`.

This rule applies to the `pi_hole` integration because it registers a custom service (`pi_hole.disable`).

Currently, the `pi_hole` integration does **not** follow this rule. The `disable` service is registered within the `async_setup_entry` function of the `switch` platform (`homeassistant/components/pi_hole/switch.py`):

```python
# homeassistant/components/pi_hole/switch.py
async def async_setup_entry(
    hass: HomeAssistant,
    entry: PiHoleConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    # ...
    # register service
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_DISABLE,
        {
            vol.Required(SERVICE_DISABLE_ATTR_DURATION): vol.All(
                cv.time_period_str, cv.positive_timedelta
            ),
        },
        "async_disable",
    )
```

This registration method means the `disable` service (and its handler) becomes available only after a `pi_hole` config entry is successfully loaded and its switch platform is set up. If the config entry is not loaded (e.g., due to an error or if it's disabled), the service handler won't be registered, and attempts to call the service might result in less specific errors like "service not found" or "entity not found," rather than a clear message from the service handler indicating the entry is not loaded.

The `pi_hole` integration currently lacks an `async_setup` function in its `__init__.py` file, which is where the service registration should occur according to the rule, using `hass.services.async_register`.

## Suggestions

To make the `pi_hole` integration compliant with the `action-setup` rule, the following changes are recommended:

1.  **Define `async_setup` in `__init__.py`**:
    Create an `async_setup` function in `homeassistant/components/pi_hole/__init__.py`.

2.  **Register the service in `async_setup`**:
    Move the service registration logic for the `disable` service into this new `async_setup` function using `hass.services.async_register`.

3.  **Implement a global service handler**:
    This handler will be responsible for:
    *   Extracting targeted entity IDs from the service call (e.g., using `homeassistant.helpers.service.async_extract_referenced_entity_ids`).
    *   For each targeted entity:
        *   Retrieving its `config_entry_id` from the entity registry.
        *   Fetching the `ConfigEntry` object.
        *   Checking if the `ConfigEntry` exists and if its state is `ConfigEntryState.LOADED`. If not, it must raise a `ServiceValidationError` with an appropriate message.
        *   If the entry is loaded, obtain the corresponding `PiHoleSwitch` entity instance.
        *   Call the entity's `async_disable` method.

4.  **Modify the service schema (if necessary)**:
    The schema passed to `hass.services.async_register` should match the `fields` defined in `services.yaml`. Since `services.yaml` uses a `target` selector, Home Assistant will handle entity ID extraction; the schema in `async_register` should primarily define the `duration` field.

5.  **Update `switch.py`**:
    *   Remove the `platform.async_register_entity_service` call from `async_setup_entry` in `homeassistant/components/pi_hole/switch.py`.
    *   Ensure the `PiHoleSwitch.async_disable` method contains the core logic for disabling Pi-hole and handles API errors appropriately (e.g., by logging and potentially raising `HomeAssistantError` if the API call fails). This method will be called by the new global service handler.

**Example Snippets:**

**In `homeassistant/components/pi_hole/__init__.py`:**

```python
from __future__ import annotations

# ... other imports from __init__.py ...
import asyncio
import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant, ServiceCall, ConfigEntryState, ConfigType
from homeassistant.exceptions import ServiceValidationError, HomeAssistantError
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.helpers.service import async_extract_referenced_entity_ids
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, SERVICE_DISABLE, SERVICE_DISABLE_ATTR_DURATION
from .switch import PiHoleSwitch  # Ensure this import is valid or use type checking

_LOGGER = logging.getLogger(__name__)

# Schema for the 'disable' service, matching fields in services.yaml
SERVICE_DISABLE_SCHEMA = vol.Schema(
    {
        vol.Required(SERVICE_DISABLE_ATTR_DURATION): vol.All(
            cv.time_period_str, cv.positive_timedelta
        ),
        # ATTR_ENTITY_ID is handled by HA based on 'target' in services.yaml
    }
)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Pi-hole integration and register services."""

    async def async_handle_disable_service(call: ServiceCall) -> None:
        """Handle the pi_hole.disable service call."""
        entity_reg = er.async_get(hass)
        duration = call.data[SERVICE_DISABLE_ATTR_DURATION]
        
        target_entity_ids = await call.async_extract_referenced_entity_ids(hass)
        
        tasks = []
        # Keep track of processed config entries to avoid redundant checks
        # and to raise error only once per unloaded entry.
        checked_config_entries: set[str] = set() 

        for entity_id in target_entity_ids:
            entity_entry = entity_reg.async_get(entity_id)

            if not entity_entry:
                _LOGGER.warning(
                    "Service %s: Entity %s not found in registry. Skipping.",
                    SERVICE_DISABLE, entity_id
                )
                continue

            # Verify it's a Pi-hole switch entity
            if not (entity_entry.platform == DOMAIN and entity_entry.domain == Platform.SWITCH):
                _LOGGER.warning(
                    "Service %s: Entity %s is not a Pi-hole switch. Skipping.",
                    SERVICE_DISABLE, entity_id
                )
                continue
            
            if not entity_entry.config_entry_id:
                _LOGGER.error(
                    "Service %s: Entity %s has no config entry ID. Skipping.",
                    SERVICE_DISABLE, entity_id
                )
                continue

            config_entry_id = entity_entry.config_entry_id

            if config_entry_id not in checked_config_entries:
                entry = hass.config_entries.async_get_entry(config_entry_id)
                if not entry:
                    # This case should ideally not happen if entity_entry exists with a config_entry_id
                    raise ServiceValidationError(
                        f"Configuration entry for {entity_id} (ID: {config_entry_id}) not found."
                    )
                
                if entry.state is not ConfigEntryState.LOADED:
                    raise ServiceValidationError(
                        f"Configuration entry for {entity_id} (Pi-hole: {entry.title}) is not loaded. Current state: {entry.state}",
                        translation_domain=DOMAIN,
                        translation_key="config_entry_not_loaded_service", # Example, add to strings.json
                        translation_placeholders={"entity_id": entity_id, "name": entry.title, "state": str(entry.state)},
                    )
                checked_config_entries.add(config_entry_id)

            # Get the switch entity instance
            # Ensure switch platform and its entities are available via hass.data
            # This relies on standard entity component structure.
            switch_platform = hass.data.get(Platform.SWITCH)
            if not switch_platform:
                 # Should not happen in a running HA system with switch components
                _LOGGER.error("Switch entity component not available.")
                raise ServiceValidationError("Switch component not available.")

            switch_entity_instance = switch_platform.get_entity(entity_id)

            if not isinstance(switch_entity_instance, PiHoleSwitch):
                _LOGGER.error(
                    "Service %s: Entity %s is not an instance of PiHoleSwitch or not found. Skipping.",
                    SERVICE_DISABLE, entity_id
                )
                continue
            
            tasks.append(switch_entity_instance.async_disable(duration=duration))

        if not tasks:
            _LOGGER.warning(
                "Service %s: No valid Pi-hole switch entities were targeted or actionable.",
                SERVICE_DISABLE
            )
            # Depending on desired behavior, could raise ServiceValidationError if no tasks created.
            return

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Errors are logged within async_disable, but we can log a summary here
                # Or re-raise if one failure should fail the whole service call (usually not for multi-target)
                _LOGGER.error("Error during disable service execution for one of the targets: %s", result)
                # If HomeAssistantError was raised by async_disable, it will propagate.


    hass.services.async_register(
        DOMAIN,
        SERVICE_DISABLE,
        async_handle_disable_service,
        schema=SERVICE_DISABLE_SCHEMA,
    )

    return True  # Indicate successful setup of the integration's global aspects

async def async_setup_entry(hass: HomeAssistant, entry: PiHoleConfigEntry) -> bool:
    # ... (existing async_setup_entry logic) ...
    # DO NOT register services here anymore
    # ...
    # Ensure runtime_data is populated as it might be used by the service handler
    # via the ConfigEntry if not directly calling entity methods.
    # The example above calls entity methods, which is cleaner.
    
    # Forward to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

# ... (rest of __init__.py, like async_unload_entry) ...
```

**In `homeassistant/components/pi_hole/switch.py`:**

```python
# ... other imports ...

async def async_setup_entry(
    hass: HomeAssistant,
    entry: PiHoleConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Pi-hole switch."""
    name = entry.data[CONF_NAME]
    hole_data = entry.runtime_data
    switches = [
        PiHoleSwitch(
            hole_data.api,
            hole_data.coordinator,
            name,
            entry.entry_id,
        )
    ]
    async_add_entities(switches, True)

    # REMOVE service registration from here:
    # platform = entity_platform.async_get_current_platform()
    # platform.async_register_entity_service(...)


class PiHoleSwitch(PiHoleEntity, SwitchEntity):
    # ... (existing properties) ...

    async def async_disable(self, duration: timedelta | None = None) -> None: # duration is timedelta
        """Disable the service for a given duration.
        This method is now called by the global service handler.
        """
        duration_seconds: bool | float = True  # Disable infinitely by default

        if duration is not None:
            duration_seconds = duration.total_seconds()
            # As per original logic: if disabling for 0 seconds, it means indefinitely
            if duration_seconds == 0:
                 duration_seconds = True # Pi-hole API uses 'True' for indefinite, or specific seconds.
            _LOGGER.debug(
                "Disabling Pi-hole '%s' (%s) for %s seconds",
                self._name, # Use self._name as in original class
                self.api.host,
                "infinite" if duration_seconds is True else duration_seconds,
            )
        else: # This case might occur if async_turn_off calls it directly without duration
             _LOGGER.debug(
                "Disabling Pi-hole '%s' (%s) infinitely",
                self._name,
                self.api.host,
            )
            
        try:
            await self.api.disable(duration_seconds)
            await self.coordinator.async_request_refresh() # self.async_update() calls this
        except HoleError as err:
            _LOGGER.error("Unable to disable Pi-hole for %s: %s", self._name, err)
            # Re-raise as HomeAssistantError to allow the service caller to be notified
            raise HomeAssistantError(f"Failed to disable Pi-hole {self._name}: {err}") from err

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the service (disable indefinitely)."""
        # This will call async_disable with duration=None, which means infinitely.
        # If the service required a duration, this direct call path needs consideration,
        # but for rule compliance, the service registration is key.
        await self.async_disable() 
```

**In `strings.json` (optional, for custom error messages):**
Add a new key under `config.error` or a new top-level section if preferred, for example:
```json
{
  "services": {
    "disable": {
       // ... existing service description ...
    }
  },
  "service_errors": {
    "config_entry_not_loaded_service": "Configuration entry for {entity_id} (Pi-hole: {name}) is not loaded. Current state: {state}"
  }
}
```
And then use `translation_key="config_entry_not_loaded_service"` and `translation_domain=DOMAIN` in `ServiceValidationError`. The example `ServiceValidationError` above shows how to include placeholders.

These changes would align the `pi_hole` integration with the `action-setup` rule by centralizing service registration and ensuring proper validation of config entry states within the service handler.

---

_Created at 2025-06-10 23:04:35. Prompt tokens: 10187, Output tokens: 3577, Total tokens: 21602._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
