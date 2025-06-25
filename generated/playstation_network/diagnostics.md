# playstation_network: diagnostics

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [playstation_network](https://www.home-assistant.io/integrations/playstation_network/) |
| Rule   | [diagnostics](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/diagnostics)                                                     |
| Status | **todo**                                                                 |

## Overview

The `diagnostics` rule applies to this integration as it is a cloud-polling service with a configuration entry. It manages runtime state and data via a coordinator, which can be useful for debugging user-reported issues.

The integration currently does not follow this rule. A review of the provided source code shows there is no `diagnostics.py` file, and consequently, no implementation of the `async_get_config_entry_diagnostics` function. This means users cannot easily download diagnostic information for this integration from the Home Assistant UI.

The `PlaystationNetworkCoordinator` holds valuable runtime data in `coordinator.data` (an instance of the `PlaystationNetworkData` dataclass defined in `helpers.py`), which would be ideal for inclusion in a diagnostics dump.

## Suggestions

To meet the requirements of this rule, a `diagnostics.py` file should be created within the `homeassistant/components/playstation_network/` directory. This file should implement the `async_get_config_entry_diagnostics` function to gather and return relevant data while redacting sensitive information.

The configuration for this integration contains a sensitive `CONF_NPSSO` token, which must be redacted.

Here is a suggested implementation for `homeassistant/components/playstation_network/diagnostics.py`:

```python
"""Diagnostics support for PlayStation Network."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CONF_NPSSO
from .coordinator import PlaystationNetworkConfigEntry, PlaystationNetworkCoordinator

# Set of keys to redact from the config entry data.
TO_REDACT = {
    CONF_NPSSO,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: PlaystationNetworkConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: PlaystationNetworkCoordinator = entry.runtime_data

    # The coordinator.data is a dataclass, convert it to a dict for serialization.
    coordinator_data = asdict(coordinator.data)

    return {
        "entry": async_redact_data(entry.data, TO_REDACT),
        "data": coordinator_data,
    }
```

**Why this helps:**

*   **Creates `diagnostics.py`:** This file will be automatically picked up by Home Assistant to provide the diagnostics feature.
*   **Redacts Sensitive Data:** It uses `async_redact_data` to ensure the user's `NPSSO` token is not exposed in the diagnostics output, which is a critical security requirement of the rule.
*   **Provides Rich Data:** It includes both the (redacted) configuration entry data and the full runtime data from the coordinator. Using `dataclasses.asdict` ensures all the valuable information from the `PlaystationNetworkData` object (like presence, profile, and active sessions) is included in a serializable format. This will greatly aid in troubleshooting.

---

_Created at 2025-06-25 19:07:16 using gemini-2.5-pro. Prompt tokens: 9300, Output tokens: 783, Total tokens: 11608._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
