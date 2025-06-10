# pi_hole: unique-config-entry

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [pi_hole](https://www.home-assistant.io/integrations/pi_hole/) |
| Rule   | [unique-config-entry](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/unique-config-entry)                                                     |
| Status | **done**                                       |
| Reason |                                                                          |

## Overview

The `unique-config-entry` rule requires that an integration prevents the same device or service from being set up multiple times. This is typically achieved by either assigning a `unique_id` to the configuration entry and checking for its existence, or by verifying that specific pieces of configuration data (like a host or serial number) are unique among existing entries.

The `pi_hole` integration uses a config flow (`"config_flow": true` in `manifest.json`), so this rule applies.

The integration correctly follows this rule by using the `self._async_abort_entries_match()` method within its config flow. Specifically, in the `async_step_user` method of `config_flow.py`, it checks for existing entries that match the combination of the Pi-hole's host (including port) and its web interface location:

```python
# homeassistant/components/pi_hole/config_flow.py
# Lines 43-49
            self._async_abort_entries_match(
                {
                    CONF_HOST: f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}",
                    CONF_LOCATION: user_input[CONF_LOCATION],
                }
            )
```

This ensures that if a user attempts to configure a Pi-hole instance with the same host, port, and location as an already configured instance, the config flow will abort, preventing duplicate entries. This approach aligns with the "Unique data" method described in the rule's example implementation. The combination of `host:port` and `location` is a suitable way to uniquely identify a Pi-hole service instance.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-10 23:14:30. Prompt tokens: 10696, Output tokens: 484, Total tokens: 13738._

_Report based on [`ab7f6c3`](https://github.com/home-assistant/core/tree/ab7f6c35287f43fe1207b3de4581b3bfabd49399)._

_AI can be wrong. Always verify the report and the code against the rule._
