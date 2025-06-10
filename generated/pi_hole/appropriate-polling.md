# pi_hole: appropriate-polling

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [appropriate-polling](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/appropriate-polling)                                                     |
| Status | **done**                                       |
| Reason | (Only include if Status is "exempt". Explain why the rule does not apply.) |

## Overview

The `appropriate-polling` rule applies to this integration because the `manifest.json` file declares `"iot_class": "local_polling"`, indicating that it polls a device or service for data.

The integration follows this rule. It uses a `DataUpdateCoordinator` to manage polling, and a specific update interval is set.

In `homeassistant/components/pi_hole/__init__.py`, the `DataUpdateCoordinator` is initialized with an `update_interval`:
```python
# homeassistant/components/pi_hole/__init__.py
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        config_entry=entry,
        name=name,
        update_method=async_update_data,
        update_interval=MIN_TIME_BETWEEN_UPDATES, # This sets the polling interval
    )
```

The `MIN_TIME_BETWEEN_UPDATES` constant is defined in `homeassistant/components/pi_hole/const.py`:
```python
# homeassistant/components/pi_hole/const.py
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)
```
A polling interval of 5 minutes is generally appropriate for Pi-hole. Pi-hole statistics (like ads blocked, DNS queries) change relatively frequently, but an update every 5 minutes provides a good balance between data freshness and minimizing load on the Pi-hole device and Home Assistant. This interval should serve the majority of users well. Users requiring more frequent updates can customize this interval through Home Assistant's built-in mechanisms.

The chosen interval avoids overly frequent polling (e.g., every few seconds) which would be unnecessary for most use cases, and it's also not too infrequent for data that can change dynamically.

## Suggestions
No suggestions needed.

---

_Created at 2025-06-10 23:04:55. Prompt tokens: 10223, Output tokens: 522, Total tokens: 12132._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
