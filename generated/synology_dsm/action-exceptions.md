```markdown
# synology_dsm: action-exceptions

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [action-exceptions](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-exceptions)                                                     |
| Status | **todo**                                                                 |

## Overview

This rule requires that service actions within an integration raise exceptions (specifically `ServiceValidationError` for invalid input or `HomeAssistantError` for service-side errors) when they encounter failures. These exceptions are then used by Home Assistant to provide feedback to the user interface.

This rule applies to the `synology_dsm` integration as it registers and handles service calls for `reboot` and `shutdown` in `homeassistant/components/synology_dsm/service.py`.

The integration currently does **not** fully follow this rule for the registered services. The `service_handler` function in `service.py` handles both the `reboot` and `shutdown` service calls. It attempts to execute the corresponding API calls (`await getattr(dsm_api, f"async_{call.service}")()`) within a `try...except SynologyDSMException as ex:` block. However, inside the `except` block, it only logs an error message using `LOGGER.error(...)` and then returns, rather than raising a Home Assistant specific exception like `HomeAssistantError`.

While the underlying `_syno_api_executer` in `common.py` *does* raise `SynologyDSMAPIErrorException` or `SynologyDSMRequestException`, the `service_handler` intercepts these and prevents them from propagating in a way that Home Assistant can use to inform the user via the UI.

For example, the `service_handler` in `homeassistant/components/synology_dsm/service.py` contains:
```python
            try:
                await getattr(dsm_api, f"async_{call.service}")()
            except SynologyDSMException as ex:
                LOGGER.error(
                    "%s of DSM with serial %s not possible, because of %s",
                    call.service,
                    serial,
                    ex,
                )
                return # <--- Failure is logged, but no exception raised.
```
This prevents the user from seeing an error message in the Home Assistant UI if the reboot or shutdown fails.

## Suggestions

To comply with the `action-exceptions` rule for service calls, modify the `service_handler` function in `homeassistant/components/synology_dsm/service.py` to re-raise caught exceptions as `HomeAssistantError`.

Specifically, change the `except` block within the `service_handler` from logging the error to raising a `HomeAssistantError`, including a user-friendly message derived from the original exception if possible.

Here is a suggested code change:

```python
# homeassistant/components/synology_dsm/service.py

# ... other imports ...
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError # <-- Import HomeAssistantError

# ... other code ...

async def async_setup_services(hass: HomeAssistant) -> None:
    """Service handler setup."""

    async def service_handler(call: ServiceCall) -> None:
        """Handle service call."""
        serial: str | None = call.data.get(CONF_SERIAL)
        entries: list[SynologyDSMConfigEntry] = (
            hass.config_entries.async_loaded_entries(DOMAIN)
        )
        dsm_devices = {
            cast(str, entry.unique_id): entry.runtime_data for entry in entries
        }

        # ... (rest of the serial/device lookup logic remains the same) ...

        if call.service in [SERVICE_REBOOT, SERVICE_SHUTDOWN]:
            if serial not in dsm_devices:
                # This case should ideally raise a ServiceValidationError
                # because the input 'serial' is invalid.
                # However, given the current structure, logging and returning
                # is less bad than silent failure, but still not ideal.
                # A proper fix might involve restructuring the service handling
                # or validation. For now, focus on the API call failure.
                LOGGER.error("DSM with specified serial %s not found", serial)
                return

            LOGGER.debug("%s DSM with serial %s", call.service, serial)
            LOGGER.warning(
                (
                    "The %s service is deprecated and will be removed in future"
                    " release. Please use the corresponding button entity"
                ),
                call.service,
            )
            dsm_device = dsm_devices[serial]
            dsm_api = dsm_device.api
            try:
                await getattr(dsm_api, f"async_{call.service}")()
            except SynologyDSMException as ex:
                # Catch the SynologyDSMException and raise HomeAssistantError
                # to propagate the failure to the UI.
                error_message = f"Failed to {call.service} DSM with serial {serial}: {ex}"
                LOGGER.error(error_message)
                raise HomeAssistantError(error_message) from ex # <-- Raise HomeAssistantError

    for service in SERVICES:
        hass.services.async_register(DOMAIN, service, service_handler)

```
This change ensures that when the Synology API call for reboot or shutdown fails (raising a `SynologyDSMException`), the `service_handler` converts it into a `HomeAssistantError`, which Home Assistant can then display to the user in the frontend, providing clear feedback about the action's failure.

Additionally, consider reviewing other parts of the code that interact with the Synology API (like switch `turn_on`/`turn_off` or button `press`) to ensure they also handle exceptions appropriately, although the rule specifically targets "service actions". While not strictly required by this specific rule, it's good practice for user feedback. In this integration, button presses already use `_syno_api_executer` which raises exceptions, so the button entities should handle those exceptions or allow them to propagate correctly. The switch entities' `async_turn_on`/`async_turn_off` might also need similar exception handling.

_Created at 2025-05-25 11:48:03. Prompt tokens: 39491, Output tokens: 1425, Total tokens: 41983_
