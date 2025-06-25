# geocaching: appropriate-polling

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [appropriate-polling](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/appropriate-polling)                                                     |
| Status | **done**                                                                 |

## Overview

The `appropriate-polling` rule applies to this integration because it is a cloud polling integration, as indicated by its `iot_class` of `cloud_polling` in `manifest.json`. It fetches data from the Geocaching API on a regular schedule.

The integration correctly follows this rule by setting a reasonable and explicit polling interval.

The integration utilizes a `DataUpdateCoordinator` to manage data fetching. In `geocaching/coordinator.py`, the coordinator is initialized with a specific `update_interval`:

```python
# geocaching/coordinator.py
# ...
from .const import DOMAIN, ENVIRONMENT, LOGGER, UPDATE_INTERVAL
# ...

class GeocachingDataUpdateCoordinator(DataUpdateCoordinator[GeocachingStatus]):
    # ...
    def __init__(
        self,
        # ...
    ) -> None:
        # ...
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
# ...
```

The value for `UPDATE_INTERVAL` is defined in `geocaching/const.py`:

```python
# geocaching/const.py
from datetime import timedelta
# ...
UPDATE_INTERVAL = timedelta(hours=1)
```

A polling interval of one hour is appropriate for the type of data being retrieved (user statistics like find counts, favorite points, etc.). This data does not change in real-time and an hourly update is more than sufficient for the vast majority of users, while also being respectful to the Geocaching API. This implementation aligns perfectly with the rule's requirements.

---

_Created at 2025-06-25 18:47:24 using gemini-2.5-pro-preview-06-05. Prompt tokens: 5932, Output tokens: 470, Total tokens: 7864._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
