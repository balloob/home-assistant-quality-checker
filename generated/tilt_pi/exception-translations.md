# tilt_pi: exception-translations

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [tilt_pi](https://www.home-assistant.io/integrations/tilt_pi/) |
| Rule   | [exception-translations](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/exception-translations)                                                     |
| Status | **todo**                                                                     |

## Overview

The `exception-translations` rule applies to this integration because it raises an `UpdateFailed` exception in the data update coordinator. `UpdateFailed` inherits from `HomeAssistantError`, and its message is intended to be displayed to the user in the Home Assistant frontend when the integration cannot fetch data.

The integration currently does not follow this rule. In `coordinator.py`, when a `TiltPiError` occurs during data fetching, an `UpdateFailed` exception is raised with a hardcoded, non-translatable f-string.

**File:** `homeassistant/components/tilt_pi/coordinator.py`
```python
async def _async_update_data(self) -> dict[str, TiltHydrometerData]:
    """Fetch data from Tilt Pi and return as a dict keyed by mac_id."""
    try:
        hydrometers = await self._api.get_hydrometers()
    except TiltPiError as err:
        raise UpdateFailed(f"Error communicating with Tilt Pi: {err}") from err  # <--- This is not translatable

    return {h.mac_id: h for h in hydrometers}
```

To comply with the rule, this exception should be raised using `translation_domain` and `translation_key` parameters, with the corresponding error message defined in the `strings.json` file under an `exceptions` key. The `strings.json` file is also missing this required section.

## Suggestions

To make the integration compliant, you need to modify the exception handling in the coordinator and add the corresponding translation to `strings.json`.

1.  **Update `coordinator.py`:**
    Modify the `_async_update_data` method to raise the `UpdateFailed` exception with translation keys. You will also need to import the `DOMAIN` constant.

    ```python
    # homeassistant/components/tilt_pi/coordinator.py

    # ... (imports)
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

    from .const import DOMAIN, LOGGER # <--- Import DOMAIN

    # ... (rest of the file)

    async def _async_update_data(self) -> dict[str, TiltHydrometerData]:
        """Fetch data from Tilt Pi and return as a dict keyed by mac_id."""
        try:
            hydrometers = await self._api.get_hydrometers()
        except TiltPiError as err:
            # V--- Change this line
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="cannot_connect_api",
            ) from err
            # ^--- To this
    
        return {h.mac_id: h for h in hydrometers}
    ```

2.  **Update `strings.json`:**
    Add a new top-level `exceptions` key to your `strings.json` file with the translation for the new key.

    ```json
    // homeassistant/components/tilt_pi/strings.json
    {
      "config": {
        // ... existing config entries
      },
      "exceptions": {
        "cannot_connect_api": {
          "message": "Error communicating with the Tilt Pi. Please check the connection and logs for more information."
        }
      },
      "entity": {
        // ... existing entity entries
      }
    }
    ```

These changes will ensure that the error message shown to the user when the Tilt Pi is unreachable is translatable, thus satisfying the `exception-translations` rule.

---

_Created at 2025-06-25 18:55:16 using gemini-2.5-pro-preview-06-05. Prompt tokens: 4203, Output tokens: 889, Total tokens: 6807._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
