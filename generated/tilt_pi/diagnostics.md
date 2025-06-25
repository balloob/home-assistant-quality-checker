# tilt_pi: diagnostics

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [tilt_pi](https://www.home-assistant.io/integrations/tilt_pi/) |
| Rule   | [diagnostics](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/diagnostics)                                                     |
| Status | **todo**                                                                 |

## Overview

The `diagnostics` rule applies to all integrations that are configured via a config entry, and it has no exceptions. The `tilt_pi` integration uses a config flow and an `async_setup_entry` function, so this rule is applicable.

Currently, the integration does not follow this rule. A review of the integration's files shows that there is no `diagnostics.py` file, and therefore no implementation of the `async_get_config_entry_diagnostics` function. This function is required to allow users to download diagnostic information about the integration's state and configuration, which is essential for troubleshooting.

## Suggestions

To comply with the rule, you should add a `diagnostics.py` file to the `homeassistant/components/tilt_pi/` directory. This file will implement the `async_get_config_entry_diagnostics` function to gather relevant, non-sensitive data for debugging.

The diagnostic data should include the contents of the config entry and the data managed by the `TiltPiDataUpdateCoordinator`.

Here is a suggested implementation:

**1. Create a new file `homeassistant/components/tilt_pi/diagnostics.py`:**

```python
"""Diagnostics support for Tilt Pi."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.core import HomeAssistant

from .coordinator import TiltPiConfigEntry, TiltPiDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: TiltPiConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: TiltPiDataUpdateCoordinator = entry.runtime_data

    # The config entry data (host, port) is not sensitive, so no redaction is needed.
    return {
        "config_entry": entry.data,
        "coordinator_data": {
            mac: asdict(hydrometer)
            for mac, hydrometer in coordinator.data.items()
        },
    }
```

**2. Explanation of changes:**

*   This new file adds the required `async_get_config_entry_diagnostics` function.
*   It retrieves the `TiltPiDataUpdateCoordinator` instance from `entry.runtime_data`.
*   It builds a dictionary containing:
    *   `config_entry`: The data from the config entry, which includes the `host` and `port` of the Tilt Pi instance. This data is not sensitive and does not require redaction.
    *   `coordinator_data`: The latest data fetched from the Tilt Pi. The `tiltpi.TiltHydrometerData` objects are converted to dictionaries using `dataclasses.asdict` to ensure they are JSON serializable.
*   Adding this file will enable the diagnostics feature for the `tilt_pi` integration, making it compliant with the rule and easier for users and developers to debug.

---

_Created at 2025-06-25 18:53:08 using gemini-2.5-pro-preview-06-05. Prompt tokens: 3971, Output tokens: 740, Total tokens: 6734._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
