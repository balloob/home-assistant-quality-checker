```markdown
# synology_dsm: action-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [action-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-setup)                                                     |
| Status | **todo**                                                                 |
| Reason |                                                                          |

## Overview

The `action-setup` rule requires that integrations register their custom service actions in the `async_setup` method, rather than `async_setup_entry`. This ensures the services are always available for automation validation, even if a configuration entry is not currently loaded.

The `synology_dsm` integration defines `reboot` and `shutdown` services in `services.yaml` and implements their handler in `service.py`. However, the registration of these services occurs within the `async_setup_services` function in `service.py`, which is called from the `async_setup_entry` function in `__init__.py`.

This means the `reboot` and `shutdown` services are only registered when at least one `synology_dsm` configuration entry is successfully loaded. If Home Assistant starts and the `synology_dsm` entry fails to load, these services will not be available, preventing users from validating automations that use them. This directly violates the requirement of the `action-setup` rule.

While the services are marked as deprecated in favor of button entities, the rule applies to any custom service defined and registered by the integration.

## Suggestions

To comply with the `action-setup` rule, the registration of the `reboot` and `shutdown` services should be moved from `async_setup_entry` to the `async_setup` method in `__init__.py`.

1.  **Modify `__init__.py`**:
    - Add an `async_setup` function.
    - Move the call to `async_setup_services(hass)` from `async_setup_entry` to the new `async_setup` function.

    ```python
    # In homeassistant/components/synology_dsm/__init__.py

    # ... other imports

    async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
        """Set up Synology DSM integration."""
        # Call service setup here, globally
        await async_setup_services(hass)
        # Return True as async_setup doesn't manage configuration
        return True


    async def async_setup_entry(hass: HomeAssistant, entry: SynologyDSMConfigEntry) -> bool:
        """Set up Synology DSM sensors."""
        # ... existing async_setup_entry code ...

        # Remove the call to async_setup_services from here
        # await async_setup_services(hass) # <-- Remove this line

        # ... rest of async_setup_entry code ...
    ```

2.  **Refine `service.py` (Optional but Recommended based on rule example):**
    - The current `service_handler` already attempts to find a loaded entry. Ensure it robustly handles cases where the specified serial is not found or the entry is not loaded, raising `homeassistant.exceptions.ServiceValidationError` as suggested by the rule's example for better user feedback.

By moving the service registration to `async_setup`, the `reboot` and `shutdown` services will be registered at Home Assistant startup, regardless of the status of the `synology_dsm` configuration entries, fulfilling the requirements of the `action-setup` rule.
```

_Created at 2025-05-25 11:45:57. Prompt tokens: 39615, Output tokens: 819, Total tokens: 41292_
