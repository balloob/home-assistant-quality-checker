# bsblan: log-when-unavailable

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [bsblan](https://www.home-assistant.io/integrations/bsblan/) |
| Rule   | [log-when-unavailable](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/log-when-unavailable)                                                     |
| Status | **done**                                                                 |

## Overview

The `log-when-unavailable` rule applies to this integration as it uses local polling (`iot_class: local_polling`) to communicate with a network device that can become unavailable.

The integration correctly follows this rule by leveraging the built-in functionality of the `DataUpdateCoordinator`. In `coordinator.py`, the `_async_update_data` method within the `BSBLanUpdateCoordinator` class implements a `try...except` block to handle communication errors.

Specifically, it catches `BSBLANConnectionError` and, in response, raises `UpdateFailed` with a descriptive error message.

```python
# homeassistant/components/bsblan/coordinator.py:80-85
        except BSBLANConnectionError as err:
            host = self.config_entry.data[CONF_HOST] if self.config_entry else "unknown"
            raise UpdateFailed(
                f"Error while establishing connection with BSB-Lan device at {host}"
            ) from err
```

By raising `UpdateFailed`, the integration delegates the logging responsibility to the `DataUpdateCoordinator` base class. The coordinator is designed to automatically handle this scenario by:
1.  Logging an `INFO` message the first time an `UpdateFailed` exception occurs.
2.  Suppressing further logs for subsequent consecutive failures to avoid spam.
3.  Logging another `INFO` message once the `_async_update_data` method successfully completes again, indicating the connection has been restored.

This implementation perfectly aligns with the recommended pattern for coordinator-based integrations and fully satisfies the rule's requirements.

## Suggestions

No suggestions needed.

---

_Created at 2025-08-04 09:07:09 using gemini-2.5-pro. Prompt tokens: 11288, Output tokens: 467, Total tokens: 13068._

_Report based on [`0ab5a05`](https://github.com/home-assistant/core/tree/0ab5a05a1f6e667e6da3771cfc802aa51388bbbe)._

_AI can be wrong. Always verify the report and the code against the rule._
